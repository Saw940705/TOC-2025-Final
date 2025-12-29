from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import requests
import json
import os
from datetime import datetime, timedelta
import re

# Import configuration from config.py
try:
    from config import (
        LINE_CHANNEL_ACCESS_TOKEN,
        LINE_CHANNEL_SECRET,
        API_URL,
        API_KEY,
        MODEL,
        DB_FILE
    )
    print("✓ Configuration loaded from config.py")
except ImportError:
    print("⚠ Warning: config.py not found. Using default values.")
    print("Please copy config.example.py to config.py and fill in your credentials.")
    # Fallback to default values
    LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
    LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'
    API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/generate"
    API_KEY = "YOUR_API_KEY"
    MODEL = "gemma3:4b"
    DB_FILE = "journal_db.json"

app = Flask(__name__)

# LINE SDK v3 configuration
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

class JournalAgent:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.tasks = []
        self.load_database()
    
    def load_database(self):
        """Load existing tasks from database file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                print(f"Loaded {len(self.tasks)} tasks from database.")
            except Exception as e:
                print(f"Error loading database: {e}")
                self.tasks = []
        else:
            self.tasks = []
            print("Starting with empty database.")
    
    def save_database(self):
        """Save tasks to database file"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def call_llm(self, prompt, is_json=False, timeout=80):
        """Call the LLM API with the given prompt"""
        headers = {"Authorization": f"Bearer {API_KEY}"}
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
        if is_json:
            payload["format"] = "json"
        
        try:
            print(f"Calling LLM API... (timeout={timeout}s)")
            response = requests.post(API_URL, json=payload, headers=headers, timeout=timeout)
            if response.status_code == 200:
                raw_text = response.json().get('response', '')
                if is_json:
                    # Extract JSON from response
                    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if match:
                        return json.loads(match.group())
                return raw_text
            else:
                print(f"API returned status code {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"API call timed out after {timeout} seconds")
        except Exception as e:
            print(f"API call failed: {e}")
        return None
    
    def parse_user_intent(self, user_input):
        """Use LLM to understand user intent and extract task details"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""You are a smart assistant helping to parse user requests about tasks and schedules.
Current date: {current_date}
Current time: {current_time}

Analyze this user input: "{user_input}"

Determine:
1. Is this a STORE request (adding a new task), RETRIEVE request (asking about existing tasks), or REMOVE request (deleting tasks)?
2. What is the task description (if storing)?
3. What is the date and time? Calculate the actual date if relative terms like "tomorrow", "today", "next Monday" are used.
4. What is the location (if mentioned)?

Return a JSON object with this structure:
{{
    "intent": "STORE" or "RETRIEVE" or "REMOVE",
    "task_description": "description of task or null",
    "date": "YYYY-MM-DD format or null",
    "time": "HH:MM format or null",
    "location": "location or null",
    "query_context": "description of what user wants to retrieve/remove (if RETRIEVE/REMOVE)"
}}

Be smart about date parsing:
- "tomorrow" = {(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}
- "today" = {current_date}
- Handle day names and calculate the correct date

Only return the JSON, nothing else."""

        return self.call_llm(prompt, is_json=True, timeout=200)
    
    def generate_natural_response(self, operation_type, details):
        """Use LLM to generate natural-sounding responses"""
        prompt = f"""You are a smart assistant that parse user requests about tasks and schedules.
        
Generate a natural, human-like response to tell user that the action was successful for the following operation:
Operation: {operation_type}
Details: {details}

You should make the response friendly and human-like.

Only return the response text, nothing else."""

        response = self.call_llm(prompt, is_json=False, timeout=200)
        return response if response else details.get("fallback", "Operation completed.")
    
    def store_task(self, task_desc, date, time, location, user_id):
        """Store a new task in the database"""
        task = {
            "id": len(self.tasks) + 1,
            "user_id": user_id,
            "description": task_desc,
            "date": date,
            "time": time,
            "location": location,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        
        if self.save_database():
            # Generate natural response via LLM
            details = {
                "task": task_desc,
                "date": date,
                "time": time,
                "location": location,
                "fallback": f"✓ Task saved: {task_desc}"
            }
            return self.generate_natural_response("STORE_TASK", details)
        else:
            return "Sorry, I encountered an error while saving the task."
    
    def retrieve_tasks(self, user_id, date=None, query_context=None):
        """Retrieve tasks matching the criteria"""
        matching_tasks = []
        
        for task in self.tasks:
            if task.get("user_id") != user_id:
                continue
            
            if date:
                if task.get("date") == date:
                    matching_tasks.append(task)
            else:
                matching_tasks.append(task)
        
        if not matching_tasks:
            return "You don't have any scheduled tasks for that time."
        
        # Prepare details for natural response
        task_list = []
        for task in matching_tasks:
            task_info = {
                "description": task['description'],
                "time": task.get('time'),
                "location": task.get('location'),
                "date": task.get('date')
            }
            task_list.append(task_info)
        
        details = {
            "tasks": task_list,
            "count": len(matching_tasks),
            "date": date,
            "fallback": f"You have {len(matching_tasks)} task(s) scheduled."
        }
        
        return self.generate_natural_response("RETRIEVE_TASKS", details)
    
    def remove_tasks_by_date(self, user_id, date):
        """Remove all tasks for a given date"""
        if not date:
            return "I need a specific date to remove tasks."
        
        # Find tasks matching the date and user
        tasks_to_remove = [task for task in self.tasks 
                          if task.get("date") == date and task.get("user_id") == user_id]
        
        if not tasks_to_remove:
            return f"You don't have any tasks scheduled for {date}."
        
        # Count how many tasks will be removed
        count = len(tasks_to_remove)
        
        # Remove tasks with the specified date
        self.tasks = [task for task in self.tasks 
                     if not (task.get("date") == date and task.get("user_id") == user_id)]
        
        # Save the updated database
        if self.save_database():
            # Generate natural response via LLM
            details = {
                "count": count,
                "date": date,
                "fallback": f"✓ Removed {count} task(s) from {date}."
            }
            return self.generate_natural_response("REMOVE_TASKS", details)
        else:
            return "Sorry, I encountered an error while removing the tasks."
    
    def process_request(self, user_input, user_id):
        """Main processing function"""
        print(f"Processing request from user {user_id}: {user_input}")
        
        # Parse user intent
        intent_data = self.parse_user_intent(user_input)
        
        if not intent_data:
            return "Sorry, I couldn't understand your request. The system took too long to respond. Please try a simpler message."
        
        print(f"Intent detected: {intent_data.get('intent')}")
        intent = intent_data.get("intent")
        
        if intent == "STORE":
            task_desc = intent_data.get("task_description")
            date = intent_data.get("date")
            time = intent_data.get("time")
            location = intent_data.get("location")
            
            if not task_desc:
                return "I couldn't identify what task you want me to store."
            
            return self.store_task(task_desc, date, time, location, user_id)
        
        elif intent == "RETRIEVE":
            date = intent_data.get("date")
            query_context = intent_data.get("query_context")
            return self.retrieve_tasks(user_id, date, query_context)
        
        elif intent == "REMOVE":
            date = intent_data.get("date")
            return self.remove_tasks_by_date(user_id, date)
        
        else:
            return "I'm not sure what you want me to do. You can ask me to store tasks, check your schedule, or remove tasks."

# Initialize the agent
agent = JournalAgent()

@app.route("/callback", methods=['POST'])
def callback():
    """LINE webhook callback"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Check your channel secret.")
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """Handle incoming text messages"""
    user_id = event.source.user_id
    user_message = event.message.text
    
    print(f"\n=== New message from {user_id} ===")
    print(f"Message: {user_message}")
    
    try:
        # Process the request
        response = agent.process_request(user_message, user_id)
        print(f"Response: {response}")
        
        # Send reply using v3 API
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response)]
                )
            )
        print("Message sent successfully!")
        
    except Exception as e:
        print(f"Error handling message: {e}")
        # Try to send error message to user
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="Sorry, something went wrong. Please try again.")]
                    )
                )
        except:
            pass

if __name__ == "__main__":
    print("\n=== LINE Journal Bot Starting ===")
    print(f"Database: {DB_FILE}")
    print(f"Tasks loaded: {len(agent.tasks)}")
    print("Waiting for messages...\n")
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)