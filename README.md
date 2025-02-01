# SEND NUDES Telegram Bot

An automated system that generates AI images to send nudes daily via Telegram using GitHub Actions.

## Prerequisites

- Python 3.x
- Telegram account
- API credentials from https://my.telegram.org/apps
- Replicate API token from https://replicate.com/account

## Setup Guide

### 1. Local Setup

Install required packages:

```bash
pip install telethon replicate requests
```

### 2. Generate Telegram Session

1. Create a file called `create_session.py`:

```python
from telethon import TelegramClient

api_id = 'your_api_id'    # From my.telegram.org/apps
api_hash = 'your_api_hash' # From my.telegram.org/apps

# Create and start the client
client = TelegramClient('session', api_id, api_hash)
client.start()
```

2. Run it and follow the Telegram authentication process:

```bash
python create_session.py
```

This will create a `session.session` file in your directory.

### 3. Split Session File for GitHub Actions

1. Create `split_session.py` (included in repository) or use the existing one:

```python
import base64

CHUNK_SIZE = 48000  # GitHub has a 48KB limit per secret

def split_session_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    b64_data = base64.b64encode(data).decode()
    chunks = [b64_data[i:i+CHUNK_SIZE] for i in range(0, len(b64_data), CHUNK_SIZE)]
    
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\nCHUNK_{i+1}:")
        print(chunk)

if __name__ == "__main__":
    split_session_file('session.session')
```

2. Run it to get your session chunks:

```bash
python split_session.py
```

3. Copy both `CHUNK_1` and `CHUNK_2` outputs - you'll need these for GitHub secrets.

### 4. GitHub Repository Setup

1. Create a new GitHub repository
2. Push these files to your repository:
   - `telegram-user-account-script.py`
   - `.github/workflows/daily-telegram.yml`
   - `.gitignore`
   - `split_session.py`
   - `README.md`

### 5. Set Up GitHub Actions Secrets

1. Go to your GitHub repository
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:

| Secret Name | Description |
|------------|-------------|
| `API_ID` | Your Telegram API ID (number from my.telegram.org) |
| `API_HASH` | Your Telegram API hash (from my.telegram.org) |
| `REPLICATE_API_TOKEN` | Your Replicate API token |
| `TELEGRAM_SESSION_1` | First chunk from split_session.py output |
| `TELEGRAM_SESSION_2` | Second chunk from split_session.py output |

### 6. Configure Phone Numbers

In `telegram-user-account-script.py`, update these values:

```python
phone_number = '+1234567890'      # Your phone number
recipient_user_id = '+1234567890'  # Recipient's phone number
```

### 7. Test the GitHub Action

1. Go to your repository's Actions tab
2. Click on "Daily Telegram Image Sender" workflow
3. Click "Run workflow" → "Run workflow"
4. Monitor the workflow run for any errors

The workflow will:
- Set up Python
- Install dependencies
- Create necessary directories
- Run the script using your secrets
- Generate and send an image via Telegram

## Schedule

The bot runs daily at 12:00 UTC. To change this, modify in `.github/workflows/daily-telegram.yml`:

```yaml
on:
  schedule:
    - cron: '0 12 * * *'  # Modify this line
```

## Troubleshooting GitHub Actions

### Common Issues:

1. "Secrets not found"
   - Verify all secrets are added correctly in repository settings
   - Check secret names match exactly (case-sensitive)
   - Make sure there are no extra spaces in secret values

2. "Session file reconstruction failed"
   - Regenerate session file locally
   - Split and update both session chunks in secrets
   - Check for any extra whitespace in chunk values

3. "API credentials invalid"
   - Verify API_ID is a number (no quotes)
   - Double-check API_HASH value
   - Ensure credentials match my.telegram.org

### Viewing Logs

1. Go to Actions tab
2. Click on the failed workflow run
3. Expand the failed step
4. Check logs for specific error messages

## Security Notes

- Never commit `session.session` file
- Keep API credentials private
- Don't share GitHub secrets
- Use `.gitignore` to prevent sensitive file commits

## Project Structure

```
├── telegram-user-account-script.py  # Main script
├── split_session.py                 # Splits session for GitHub
├── .github/
│   └── workflows/
│       └── daily-telegram.yml       # GitHub Actions config
└── .gitignore                       # Prevents sensitive file commits
```

## Customizing the AI Model

### Using a Different Replicate Model

The script can run with a custom Flux LORA model. In `telegram-user-account-script.py`, find the `replicate.run()` call and update the model ID and parameters:

```python
output = replicate.run(
    "your-model-id-here",  # Replace with any Replicate model ID
    input={
        # Update parameters according to your chosen model
        "prompt": prompt,
        "num_outputs": 1,
        # ... other model-specific parameters
    }
)
```

### Training Your Own Model

You can train your own model using [Replicate's FLUX trainer](https://replicate.com/ostris/flux-dev-lora-trainer/train):

1. **Prepare Your Training Data**
   - Collect your training images
   - Create a ZIP file containing your images
   - Images should be high quality and consistent in style

2. **Start Training on Replicate**
   - Go to [FLUX trainer](https://replicate.com/ostris/flux-dev-lora-trainer/train)
   - Select or create a destination model
   - Upload your ZIP file as input_images
   - Configure training parameters:
     - Set a trigger_word (e.g., "MYMODEL" or something unique)
     - Start with 1000 steps
     - Keep default learning_rate and batch_size
     - Enable autocaptioning unless you have custom captions

3. **Using Your Trained Model**
   - After training completes, you'll get a model ID
   - Update the script with your model ID:
   ```python
   output = replicate.run(
       "your-trained-model-id",
       input={
           "prompt": f"your-trigger-word {prompt}",  # Include your trigger word
           # ... other parameters
       }
   )
   ```

Training costs $0.001525 per second on H100 GPU hardware. Monitor your usage on Replicate's dashboard.

### Tips for Training

- Use 15-20 high-quality images for best results
- Keep your image style consistent
- Test different step counts (1000-2000 range)
- Include your trigger word in prompts to activate your style
- Save successful models on Hugging Face by providing your token and repo ID during training

### Example Training Configuration

```python
{
    "input_images": "your-images.zip",
    "trigger_word": "MYMODEL",
    "steps": 1000,
    "learning_rate": 1e-4,
    "batch_size": 1,
    "resolution": 512,
    "enable_autocaption": true
}
```

After training, update the model ID in your script and include your trigger word in prompts to generate images in your trained style.

### Updating the Trigger Word

After training your model, you need to update both the model ID and trigger word in `telegram-user-account-script.py`:

1. Update the model ID in the `replicate.run()` call:
```python
output = replicate.run(
    "your-trained-model-id",  # Your new model ID from Replicate
    input={
        "model": "dev",
        "prompt": prompt,
        # ... other parameters
    }
)
```

2. Update the prompt generation to include your trigger word. Find the `generate_prompt()` function:
```python
def generate_prompt():
    role = random.choice(roles)
    descriptor = random.choice(nsfw_descriptors)
    return f"YOURTRIGGERWORD as a naked {role}, showing bare tits, {descriptor}"  # Replace YOURTRIGGERWORD
```

The trigger word must exactly match what you used during training (case-sensitive). For example, if your trigger word was "JESSICA", your prompt should start with "JESSICA as a naked...".

### Testing Your Trigger Word

1. Test locally first:
```python
prompt = generate_prompt()
print(f"Generated prompt: {prompt}")
```

2. Make sure the prompt always includes:
   - Your exact trigger word
   - The style/pose descriptors
   - Any additional keywords that work well with your model

Remember: The trigger word is crucial for getting images in your model's style. If it's missing or incorrect, the images won't look like your training data.

