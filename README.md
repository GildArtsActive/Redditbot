# Reddit Karma Bot

A Reddit bot that can automatically repost content and comment on posts in specified subreddits. It supports human-like delays, multi-account configuration, and a simple web interface for monitoring and control.

## Features

- Reposts popular or recent content between configured subreddits.
- Comments on the most recent post in each configured subreddit.
- Human-like delays and activity simulation.
- Google Gemini API integration for generating comment text.
- Logging to `karma_bot.log`.
- Flask web interface for status, logs, and manual triggers.

## Requirements

- Python 3.7+
- Reddit API credentials (see below)
- [praw](https://praw.readthedocs.io/)
- [Flask](https://flask.palletsprojects.com/)
- [requests](https://docs.python-requests.org/)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. **Reddit App Credentials**  
   - Go to [Reddit Apps](https://www.reddit.com/prefs/apps).
   - Create a new app of type **script**.
   - Copy the `client_id`, `client_secret`, `username`, and `password` into `config.json`.

2. **Configure `config.json`**  
   - Edit `config.json` to set your accounts, subreddits, and other options.
   - Example:
     ```json
     {
       "accounts": [
         {
           "client_id": "...",
           "client_secret": "...",
           "username": "...",
           "password": "...",
           "user_agent": "KarmaBot v1.0 by /u/yourusername"
         }
       ],
       "comment_subreddits": ["funny", "pics"],
       "repost_subreddits": ["funny", "pics", "memes"],
       "max_daily_actions": 50,
       "human_simulation": {
         "min_delay_between_actions": 60,
         "max_delay_between_actions": 300,
         "active_hours_start": 9,
         "active_hours_end": 23,
         "weekend_activity_reduction": 0.7
       }
     }
     ```

3. **Google Gemini API Key (Optional)**  
   - Add your Gemini API key to `config.json` if you want to use AI-generated comments.

## Usage

### Run the Bot

```bash
python app.py
```

The bot will start running, alternating between reposting and commenting actions.

### Web Interface

```bash
python web.py
```

- Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
- Use the web interface to check status, view logs, and manually trigger actions.

## Project Structure

```
RedditBot/
├── app.py
├── web.py
├── config.json
├── config_manager.py
├── requirements.txt
├── karma_bot.log
├── test_app.py
└── templates/
    └── index.html
```

## Testing

Run unit tests with:

```bash
python test_app.py
```

## Notes

- Make sure your Reddit app is of type **script**.
- The bot respects Reddit's rate limits and simulates human-like activity.
- Logging is written to `karma_bot.log`.

## License

MIT License
