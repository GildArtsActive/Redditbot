from flask import Flask, jsonify
from app import RedditKarmaBot
import threading
import random

app = Flask(__name__)

# Initialize the bot
bot = RedditKarmaBot()

def trigger_bot_actions():
    """Trigger bot actions automatically on app startup."""
    try:
        # Trigger the first action immediately
        action = random.choice(["repost", "comment"])
        if action == "repost":
            bot.repost_content()
        else:
            bot.interact_with_posts()
        # Continue with human-like delays in a loop
        while True:
            bot._human_like_delay()
            action = random.choice(["repost", "comment"])
            if action == "repost":
                bot.repost_content()
            else:
                bot.interact_with_posts()
    except Exception as e:
        print(f"Error triggering bot actions: {e}")

@app.route('/status', methods=['GET'])
def status():
    """Endpoint to check the bot's status."""
    return jsonify({
        "status": "running",
        "daily_actions": bot.daily_actions,
        "max_daily_actions": bot.max_daily_actions
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    """Endpoint to fetch the bot's activity logs."""
    try:
        with open('karma_bot.log', 'r') as log_file:
            logs = log_file.read()
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Trigger bot actions in a separate thread to avoid blocking the server
    threading.Thread(target=trigger_bot_actions).start()
    app.run(debug=True)
