
## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/TechyCSR/AdvAITelegramBot.git

# Navigate to directory
cd AdvAITelegramBot

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your bot
cp config.example.py config.py
# Edit config.py with your API credentials

# Launch!
python run.py
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | 🏁 Start a conversation with the bot |
| `/help` | ❓ Get help and see available commands |
| `/generate [prompt]` | 🎨 Generate an image from text |
| `/newchat` | 🔄 Clear conversation history |
| `/settings` | ⚙️ Adjust bot preferences |
| `/rate` | ⭐ Rate your experience |
| `/clear_cache` | 🧹 Clear your stored images |

## 💡 Inline Features

The bot offers powerful inline mode capabilities:

### Inline AI Responses
Type `@YourBot your question?` in any chat to quickly get AI responses without leaving the conversation.

### Inline Image Generation
Type `@YourBot image your description.` to generate and share images instantly in any chat.

**Pro Tip:** End your AI queries with `.` or `?` and your image prompts with `.` to trigger generation. If the response takes time, simply add a space every 5-7 seconds to refresh the query without losing your prompt.

<details>
<summary>How to use inline mode effectively</summary>

1. **AI Responses**: Type `@YourBot What is quantum computing?` in any chat
2. **Image Generation**: Type `@YourBot image beautiful sunset over mountains.` 
3. Select the result when it appears to send it to the chat
4. For complex queries, wait a few seconds and you'll see "Still generating..." which will update with your response
5. **If no response appears**: Add a space after your prompt every 5-7 seconds to refresh the query while maintaining your place in the generation queue
6. You can use this in private chats, group conversations, or channels

</details>

## 🏗️ Project Structure

<details>
<summary>Click to expand folder structure</summary>

```
AdvAITelegramBot/
├── modules/                  # Core application modules
│   ├── core/                 # Core infrastructure components
│   │   ├── database.py       # DatabaseService with connection pooling
│   │   └── service_container.py # Dependency injection container
│   ├── models/               # Data models and services
│   │   ├── ai_res.py         # AI conversation functionality
│   │   ├── user_db.py        # User data operations
│   │   ├── inline_ai_response.py # Inline mode AI responses
│   │   └── image_service.py  # Image generation and management
│   ├── user/                 # User interaction modules
│   │   ├── start.py          # Bot start and onboarding
│   │   ├── settings.py       # User settings management
│   │   ├── help.py           # Help and documentation
│   │   ├── commands.py       # Command handling
│   │   ├── assistant.py      # Assistant mode settings
│   │   ├── lang_settings.py  # Language preferences
│   │   └── user_support.py   # User support functionality
│   ├── group/                # Group chat functionality
│   │   ├── group_info.py     # Group information
│   │   ├── group_settings.py # Group configuration
│   │   └── new_group.py      # New group handling
│   ├── image/                # Image processing components
│   │   ├── img_to_text.py    # OCR and text extraction
│   │   ├── image_generation.py # Image generation from prompts
│   │   └── inline_image_generation.py # Inline mode image generation
│   ├── speech/               # Voice processing components
│   │   ├── voice_to_text.py  # Speech recognition
│   │   └── text_to_voice.py  # Text-to-speech conversion
│   ├── chatlogs.py           # Logging user interactions
│   ├── feedback_nd_rating.py # User feedback system
│   ├── lang.py               # Language translation
│   └── maintenance.py        # Maintenance utilities
├── database/                 # Database configuration
├── generated_images/         # Local storage for generated images
├── sessions/                 # Pyrogram session files
├── logs/                     # Application logs
├── assets/                   # Static assets
├── ImgGenModel/              # Image generation models
├── run.py                    # Main application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
└── LICENSE                   # MIT License
```
</details>

## 🧠 Architecture

The bot employs a modern, modular architecture with several key design patterns:

- **💉 Service Container**: Centralized dependency injection for clean, testable code
- **🔄 Singleton Database Service**: Efficient MongoDB connection pooling
- **📊 Model-View Pattern**: Separation of data and presentation layers
- **🔄 Async Processing**: Non-blocking operations for inline queries and image generation

## 🛠️ Setup Guide

### System Requirements

- Python 3.8 or higher
- MongoDB (local or cloud instance)
- Telegram Bot Token from BotFather
- 1GB+ RAM recommended for image generation

### Detailed Installation

<details>
<summary>1. Environment Setup</summary>

```bash
# Make sure you have Python 3.8+ installed
python --version

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
</details>
<details>
<summary>2. Install Dependencies</summary>

```bash
# Install required packages
pip install -r requirements.txt

# Verify installations
pip list
```
</details>

<details>
<summary>3. Configuration</summary>

Create a `config.py` file with your credentials:

```python
BOT_TOKEN = "your_telegram_bot_token"  # From BotFather
API_KEY = "your_telegram_api_key"      # From my.telegram.org
API_HASH = "your_telegram_api_hash"    # From my.telegram.org
DATABASE_URL = "mongodb://localhost:27017/"
ADMINS = [123456789]  # Your Telegram user ID
OCR_KEY = "your_ocr_space_api_key"     # From ocr.space
```
</details>

<details>
<summary>4. Database Setup</summary>

```bash
# Start MongoDB (if using local instance)
mongod --dbpath /path/to/data/db

# The bot will automatically create required collections
```
</details>

<details>
<summary>5. Running the Bot</summary>

```bash
# Start the bot
python run.py

# For production deployment
# Consider using systemd, Docker, or PM2
```
</details>

## 🔧 Advanced Configuration

<details>
<summary>Docker Deployment</summary>

```bash
# Build the Docker image
docker build -t advai-telegram-bot .

# Run the container
docker run -d --name advai-bot advai-telegram-bot
```
</details>

<details>
<summary>Environment Variables</summary>

You can use environment variables instead of config.py:

```bash
export BOT_TOKEN="your_telegram_bot_token"
export API_KEY="your_telegram_api_key"
export API_HASH="your_telegram_api_hash"
export DATABASE_URL="mongodb://localhost:27017/"
# Optional API keys
export OPENAI_API_KEY="your_openai_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
export GETIMG_API_KEY="your_getimg_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export PIAPI_API_KEY="your_piapi_key"
export ELEVENLABS_API_KEY="your_elevenlabs_key"
export FAL_AI_KEY="your_fal_ai_key"
```
</details>

## 💻 Technologies

- [**Pyrogram**](https://docs.pyrogram.org/): Modern Telegram client library
- [**MongoDB**](https://www.mongodb.com/): NoSQL database for user data
- [**GPT-4o**](https://openai.com/): Advanced language model
- [**OCR.space**](https://ocr.space/): Text extraction API
- [**Various Image Generators**](https://github.com): High-quality AI image creation
