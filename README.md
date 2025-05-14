# <div align="center">🤖 Advanced AI Telegram Bot</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-informational?style=for-the-badge&logo=telegram)](https://t.me/AdvChatGptBot)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-success?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

<p align="center">
  <a href="https://t.me/AdvChatGptBot">
    <img src="https://img.shields.io/badge/TELEGRAM-BOT-blue?style=for-the-badge&logo=telegram&logoColor=white&labelColor=blue&color=blue&logoWidth=20&logoHeight=20" alt="Telegram Bot" height="60">
  </a>
</p>

<div align="center">
  A powerful AI-driven Telegram bot that brings cutting-edge artificial intelligence features to your fingertips.
</div>

---

## ✨ Features

<table>
  <tr>
    <td align="center">💬</td>
    <td><b>AI Chat</b><br>Natural conversations powered by GPT-4o</td>
    <td align="center">🎨</td>
    <td><b>Image Generation</b><br>Create stunning images from text descriptions</td>
  </tr>
  <tr>
    <td align="center">🔊</td>
    <td><b>Voice Processing</b><br>Two-way voice message and text conversion</td>
    <td align="center">📝</td>
    <td><b>Text Extraction</b><br>Extract text from any image with OCR</td>
  </tr>
  <tr>
    <td align="center">🌐</td>
    <td><b>Multi-language Support</b><br>Communicate in your preferred language</td>
    <td align="center">👥</td>
    <td><b>Group Integration</b><br>Full AI functionality in group chats</td>
  </tr>
</table>

> 📱 **Try it now**: [t.me/AdvChatGptBot](https://t.me/AdvChatGptBot)

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
```
</details>

## 💻 Technologies

- [**Pyrogram**](https://docs.pyrogram.org/): Modern Telegram client library
- [**MongoDB**](https://www.mongodb.com/): NoSQL database for user data
- [**GPT-4o**](https://openai.com/): Advanced language model
- [**OCR.space**](https://ocr.space/): Text extraction API
- [**Various Image Generators**](https://github.com): High-quality AI image creation

## 🤝 Contributing

Contributions are welcome! Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

<details>
<summary>Development Workflow</summary>

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request
</details>

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  Made with ❤️ by TechyCSR
  <br>
  <a href="https://techycsr.me">Website</a> •
  <a href="https://x.com/techycsr">Twitter</a> •
  <a href="https://linkedin.com/in/techycsr">LinkedIn</a>
</div> 