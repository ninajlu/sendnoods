# Send (Flux LoRA) Noods via Telegram

Generate your own Flux LoRA model and automatically schedule daily AI-generated images to be sent via Telegram using GitHub Actions.

## 1. Training Your Own Model

You can train your own model using [Replicate's FLUX trainer](https://replicate.com/ostris/flux-dev-lora-trainer/train):

### Preparing Training Data
1. Collect 15-20 high-quality training images in a consistent style
2. Create a ZIP file containing your images

### Training on Replicate
1. Go to [FLUX trainer](https://replicate.com/ostris/flux-dev-lora-trainer/train)
2. Select or create a destination model
3. Configure training parameters:
   ```python
   {
       "input_images": "your-images.zip",
       "trigger_word": "MYMODEL",  # Choose a unique trigger word
       "steps": 1000,
       "learning_rate": 1e-4,
       "batch_size": 1,
       "resolution": 512,
       "enable_autocaption": true
   }
   ```

### Training Tips
- Keep image style consistent
- Test different step counts (1000-2000 range)
- Include your trigger word in prompts to activate your style
- Save successful models on Hugging Face by providing your token and repo ID during training
- Training costs approximately $0.001525 per second on H100 GPU hardware

## 2. Prerequisites

- Python 3.x
- Telegram account
- API credentials from https://my.telegram.org/apps
- Replicate API token from https://replicate.com/account

## 3. Local Setup

Install required packages:
```bash
pip install telethon replicate requests
```

## 4. Generate Telegram Session

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

## 5. Split Session File for GitHub Actions

1. Create or use the existing `split_session.py`:
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

## 6. GitHub Repository Setup

1. Create a new GitHub repository
2. Push these files to your repository:
   - `telegram-user-account-script.py`
   - `.github/workflows/daily-telegram.yml`
   - `.gitignore`
   - `split_session.py`
   - `README.md`

## 7. Set Up GitHub Actions Secrets

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:

| Secret Name | Description |
|------------|-------------|
| `API_ID` | Your Telegram API ID (number from my.telegram.org) |
| `API_HASH` | Your Telegram API hash (from my.telegram.org) |
| `REPLICATE_API_TOKEN` | Your Replicate API token |
| `TELEGRAM_SESSION_1` | First chunk from split_session.py output |
| `TELEGRAM_SESSION_2` | Second chunk from split_session.py output |

## 8. Configure Phone Numbers

In `telegram-user-account-script.py`, update these values:
```python
phone_number = '+1234567890'      # Your phone number
recipient_user_id = '+1234567890'  # Recipient's phone number
```

## 9. Test the GitHub Action

1. Go to your repository's Actions tab
2. Click on "Daily Telegram Image Sender" workflow
3. Click "Run workflow" → "Run workflow"
4. Monitor the workflow run for any errors

## Schedule Configuration

The bot runs daily at 12:00 UTC. To change this, modify in `.github/workflows/daily-telegram.yml`:
```yaml
on:
  schedule:
    - cron: '0 12 * * *'  # Modify this line
```

## Troubleshooting GitHub Actions

### Common Issues:
1. "Secrets not found"
   - Verify all secrets are added correctly
   - Check secret names match exactly (case-sensitive)
   - Ensure no extra spaces in secret values

2. "Session file reconstruction failed"
   - Regenerate session file locally
   - Split and update both session chunks
   - Check for extra whitespace in chunks

3. "API credentials invalid"
   - Verify API_ID is a number (no quotes)
   - Double-check API_HASH value
   - Ensure credentials match my.telegram.org

### Viewing Logs
1. Go to Actions tab
2. Click the failed workflow run
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

