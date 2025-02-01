from telethon import TelegramClient
import asyncio
import replicate
import os
import random
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.messages import SendMediaRequest
import requests
import base64

# Add debug logging for environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
if not api_id or not api_hash:
    print("Debug: Environment variables not found")
    print(f"API_ID present: {'API_ID' in os.environ}")
    print(f"API_HASH present: {'API_HASH' in os.environ}")
    raise ValueError("API_ID or API_HASH environment variables are missing")

# Convert API_ID to integer since Telethon expects it as int
api_id = int(api_id)

# REPLACE WITH YOUR OWN PHONE NUMBER AND RECIPIENT ID
phone_number = '+11234567890'
recipient_user_id = '+11234567890'

if not phone_number or not recipient_user_id:
    raise ValueError("TELEGRAM_PHONE or TELEGRAM_RECIPIENT environment variables are missing")

# Replicate API setup
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# Lists for random prompt generation
roles = [
    "astronaut", "chef", "detective", "artist", "scientist", "superhero",
    "pirate", "ninja", "wizard", "knight", "explorer", "time traveler",
    "mermaid", "vampire", "werewolf", "fairy", "robot", "alien"
]

descriptors = [
    "futuristic", "steampunk", "cyberpunk", "medieval", "renaissance",
    "post-apocalyptic", "magical", "underwater", "ethereal", "neon",
    "vintage", "retro", "dystopian", "utopian", "surreal", "minimalist",
    "maximalist", "psychedelic", "pastel", "monochromatic"
]

# Example greetings - you can customize these
casual_greetings = [
    "Good morning! Hope your day is amazing!",
    "Hey there! Wishing you a wonderful day!",
    "Have a fantastic day ahead!",
    "Rise and shine! Have the best day ever!",
    "Hello! May your day be filled with joy!"
]
# REPLACE WITH YOUR OWN TRIGGER WORD
def generate_prompt():
    role = random.choice(roles)
    descriptor = random.choice(descriptors)
    return f"[TRIGGER WORD] as {descriptor} {role} in an artistic style"

def reconstruct_session():
    session_data = ''
    chunk_index = 1
    
    while True:
        chunk = os.getenv(f'TELEGRAM_SESSION_{chunk_index}')
        if not chunk:
            break
        session_data += chunk
        chunk_index += 1
    
    if session_data:
        with open('session.session', 'wb') as f:
            f.write(base64.b64decode(session_data))
        return True
    return False

async def generate_and_send_image():
    prompt = generate_prompt()
    print(f"Generated prompt: {prompt}")

    # Generate image using Replicate
    output = replicate.run(
        "YOUR_MODEL_ID_HERE",  # Replace with your Replicate model ID
        input={
            "prompt": prompt,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "jpg",
            "guidance_scale": 3.5,
            "output_quality": 80,
            "num_inference_steps": 28,
        }
    )
    
    if output and len(output) > 0:
        image_url = output[0]
        image_path = f"downloaded_images/{prompt.replace(' ', '_')}.jpg"
        os.makedirs("downloaded_images", exist_ok=True)
        
        with open(image_path, "wb") as file:
            file.write(requests.get(image_url).content)
        print(f"Image downloaded and saved as {image_path}")
        
        # Send image via Telegram
        if reconstruct_session():
            print("Session file reconstructed successfully")
            try:
                client = TelegramClient('session', api_id, api_hash)
                print("Connecting to Telegram...")
                await client.connect()
                
                if not await client.is_user_authorized():
                    print("User not authorized - attempting to start session")
                    await client.start(phone=phone_number)
                
                print("Getting recipient entity...")
                recipient = await client.get_input_entity(recipient_user_id)
                intro = random.choice(casual_greetings)
                
                print("Sending file...")
                await client.send_file(
                    recipient,
                    file=image_path,
                    caption=f"{intro}\nHere's your generated image!\nPrompt: {prompt}"
                )
                print("Image sent successfully!")
                
            except Exception as e:
                print(f"Failed to send image: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
            finally:
                if 'client' in locals():
                    await client.disconnect()
        else:
            print("Failed to reconstruct session file")

# Run the async function
if __name__ == "__main__":
    asyncio.run(generate_and_send_image())
