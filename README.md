# LINE Journal Bot

A smart personal assistant chatbot for LINE that helps you manage tasks and schedules using natural language processing.

## Features ✨

- 📅 **Store tasks** with date, time, and location
- 🔍 **Retrieve schedule** by asking in natural language
- 🗑️ **Remove tasks** by date
- 🤖 **AI-powered** natural language understanding and responses
- 💾 **Persistent storage** of all your tasks

## Prerequisites

- Python 3.8 or higher
- LINE Developer Account
- ngrok (for local testing)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/line-journal-bot.git
cd line-journal-bot
```

### 2. Create virtual environment
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure LINE Bot

1. Create a LINE Messaging API channel at [LINE Developers Console](https://developers.line.biz/console/)
2. Get your **Channel Access Token** and **Channel Secret**
3. Open `line_journal_bot.py` and update these lines:
```python
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'
```

**⚠️ IMPORTANT**: Never commit your actual tokens to GitHub!

### 5. Configure LLM API (Optional)

If you have your own LLM API, update these lines:
```python
API_URL = "your_api_url"
API_KEY = "your_api_key"
MODEL = "your_model"
```

## Usage

### Running Locally with ngrok

1. **Start the Flask app**
```bash
python line_journal_bot.py
```

2. **Start ngrok** (in a new terminal)
```bash
ngrok http 5000
```

3. **Set webhook URL** in LINE Developers Console
   - Copy your ngrok URL (e.g., `https://xxxx.ngrok-free.app`)
   - Add `/callback` to the end
   - Example: `https://xxxx.ngrok-free.app/callback`

4. **Configure LINE settings**
   - Enable "Use webhook"
   - Disable "Auto-reply messages"

5. **Add your bot as a friend** and start chatting!

### Example Commands

```
I have a meeting at NCKU tomorrow at 9:00
What is my schedule tomorrow?
Remind me to buy groceries at 5 PM today
Remove all tasks tomorrow
```

## Project Structure

```
line-journal-bot/
├── line_journal_bot.py    # Main bot code
├── journal_db.json         # Database (auto-generated)
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Deployment

For production deployment, consider using:
- [Heroku](https://heroku.com)
- [Railway](https://railway.app)
- [Render](https://render.com)
- AWS/GCP/Azure

Remember to set environment variables instead of hardcoding tokens!

## Security Notes 🔒

- **Never commit** your Channel Access Token or Channel Secret
- Use environment variables for sensitive data in production
- Consider using `.env` files with `python-dotenv`

## Troubleshooting

### Bot doesn't respond
- Check if Flask is running
- Check if ngrok is running
- Verify webhook URL is correct
- Make sure "Auto-reply messages" is OFF
- Check Flask terminal for errors

### API Timeout
- The LLM API might be slow
- Check your internet connection
- Consider reducing timeout values

### Webhook verification failed
- Double-check your Channel Secret
- Make sure Flask is accessible via ngrok
- Verify the webhook URL ends with `/callback`

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License - feel free to use this project for learning or personal use.

## Contact

For questions or issues, please open an issue on GitHub.

---

Made with ❤️ for personal task management