# LINE Journal Bot

A personal assistant chatbot for LINE that helps you manage schedules.

## Prerequisites

- Python 3.8 or higher
- LINE Developer Account, get from https://developers.line.biz/en/
- ngrok (for local testing), download from https://ngrok.com/

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Saw940705/TOC-2025-Final
cd TOC-2025-final
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure LINE Bot and LLM API
1. Create a LINE Messaging API channel at [LINE Developers Console](https://developers.line.biz/console/)
2. Get your **Channel Access Token** and **Channel Secret**
3. Get you **LLM API key** and **LLM API Url**
4. json file defaults to **journal_db.json**
5. Open `config.py` and update these lines:
```python
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

API_URL = "your_api_url"
API_KEY = "your_api_key"
MODEL = "your_model"
```

## Usage

### Running with ngrok

1. **Start the agent**, the ngrok terminal will start in the background
   **ngrok Web Interface defualts at http://localhost:4040**
```bash
python journal_agent.py
```

2. **Set webhook URL** in LINE Developers Console
   - Copy your ngrok URL (e.g., `https://xxxx.ngrok-free.app`)
   - Add `/callback` to the end

3. **Add your bot as a friend** and start chatting!

### Example Commands

```
I have a meeting at NCKU tomorrow at 9:00
What is my schedule tomorrow?
Remind me to buy groceries at 5 PM today
Remove all my tasks tomorrow
```

## Project Structure

```
TOC-2025-final/
├── journal_agent.py       # Main bot code
├── journal_db.json        # Database (auto-generated)
├── requirements.txt       # Python dependencies
├── config.py              # Config (sensitive inforamtion)
├── .gitignore             
└── README.md              
```

## State Machine Diagram