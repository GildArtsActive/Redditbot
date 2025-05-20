import praw
import random
import time
import os
import json
import logging
from datetime import datetime, timedelta
from config_manager import ConfigManager
import requests # type: ignore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("karma_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("KarmaBot")

class RedditKarmaBot:
    def __init__(self, config_path="config.json"):
        """Initialize the Reddit Karma Bot with configuration."""
        self.config_manager = ConfigManager(config_path)
        self.account = self.config_manager.get_account()
        self.reddit = self._initialize_reddit()
        self.last_action_time = datetime.now()
        self.daily_actions = 0
        self.max_daily_actions = self.config_manager.config.get("max_daily_actions", 50)

    def _initialize_reddit(self):
        """Initialize the Reddit API client."""
        try:
            return praw.Reddit(
                client_id=self.account["client_id"],
                client_secret=self.account["client_secret"],
                username=self.account["username"],
                password=self.account["password"],
                user_agent=self.account["user_agent"]
            )
        except Exception as e:
            logger.error(f"Error initializing Reddit API: {e}")
            raise

    def _human_like_delay(self):
        """Simulate human-like delays between actions."""
        human_sim = self.config_manager.config.get("human_simulation", {})
        min_delay = human_sim.get("min_delay_between_actions", 300)
        max_delay = human_sim.get("max_delay_between_actions", 1800)
        
        # Reduce activity on weekends if configured
        now = datetime.now()
        if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            reduction = human_sim.get("weekend_activity_reduction", 0.7)
            max_delay = int(max_delay / reduction)
        
        # Check if we're in active hours
        active_start = human_sim.get("active_hours_start", 9)
        active_end = human_sim.get("active_hours_end", 23)
        current_hour = now.hour
        
        if not (active_start <= current_hour < active_end):
            logger.info("Outside active hours, sleeping longer...")
            # Sleep longer outside active hours (4-8 hours)
            self._sleep_random(14400, 28800)
            return
        
        # Normal delay during active hours
        self._sleep_random(min_delay, max_delay)

    def _sleep_random(self, min_seconds, max_seconds):
        """Sleep for a random duration between min_seconds and max_seconds."""
        delay = random.randint(min_seconds, max_seconds)
        logger.info(f"Waiting for {delay} seconds to appear human-like...")
        time.sleep(delay)

    def _should_take_action(self):
        """Determine if the bot should take an action based on daily limits."""
        # Reset counter if it's a new day
        now = datetime.now()
        if now.date() > self.last_action_time.date():
            self.daily_actions = 0
        
        # Check if we've exceeded daily action limit
        if self.daily_actions >= self.max_daily_actions:
            logger.info("Daily action limit reached, waiting until tomorrow...")
            return False
        
        self.last_action_time = now
        self.daily_actions += 1
        return True

    def repost_content(self):
        """Repost popular content from target subreddits."""
        if not self._should_take_action():
            return

        subreddits = self.config_manager.config.get("repost_subreddits", [])
        if not subreddits:
            logger.warning("No repost subreddits configured")
            return

        target_subreddit = random.choice(subreddits)
        logger.info(f"Fetching posts from r/{target_subreddit}")

        # Fetch recent posts (submissions) from the subreddit
        posts = self.fetch_posts(target_subreddit, limit=20)
        if not posts:
            logger.warning(f"No posts found in r/{target_subreddit}")
            return

        # Choose a random post that's at least 2 weeks old
        post = random.choice(posts)
        post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)

        if post_age < timedelta(days=14):
            logger.info(f"Post is too recent ({post_age.days} days old), skipping")
            return

        repost_to = random.choice([s for s in subreddits if s != target_subreddit])

        try:
            logger.info(f"Checking if the post URL already exists in r/{repost_to}")
            existing_posts = self.reddit.subreddit(repost_to).search(f"url:{post.url}", limit=1)
            if any(existing_posts):
                logger.info(f"Post URL already exists in r/{repost_to}, skipping repost")
                return

            title_modifiers = [
                "This is interesting: ", "", "Check this out: ", "Wow: ",
                "Amazing: ", "", "Interesting: ", ""
            ]
            new_title = random.choice(title_modifiers) + post.title

            logger.info(f"Reposting '{new_title}' to r/{repost_to}")

            # For demonstration only - in a real bot, this would actually post
            # self.reddit.subreddit(repost_to).submit(new_title, url=post.url)
            logger.info("Repost simulation successful")

            self._human_like_delay()
        except Exception as e:
            logger.error(f"Error reposting content: {e}")

    def fetch_posts(self, subreddit_name, limit=10):
        """Fetch recent posts (submissions) from a subreddit."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            return list(subreddit.new(limit=limit))
        except Exception as e:
            logger.error(f"Error fetching posts from Reddit for r/{subreddit_name}: {e}")
            return []

    def fetch_comment_text_from_gemini(self, comment_body, subreddit_name):
        """Fetch a reply text from Google Gemini API based on the comment body and subreddit."""
        try:
            logger.info(f"Fetching reply from Google Gemini API for subreddit '{subreddit_name}' and comment '{comment_body[:50]}...'")
            return f",{comment_body[:50]}"
        except Exception as e:
            logger.error(f"Error fetching reply from Google Gemini API: {e}")
            return "This is an automated response!"

    def interact_with_posts(self):
        """Comment on the most recent post in each target subreddit."""
        if not self._should_take_action():
            return

        subreddits = self.config_manager.config.get("comment_subreddits", [])
        if not subreddits:
            logger.warning("No comment subreddits configured")
            return

        for target_subreddit in subreddits:
            logger.info(f"Fetching most recent post from r/{target_subreddit}")
            try:
                subreddit = self.reddit.subreddit(target_subreddit)
                posts = list(subreddit.new(limit=1))
                if not posts:
                    logger.warning(f"No posts found in r/{target_subreddit}")
                    continue

                post_to_comment = posts[0]
                logger.info(f"Selected post for interaction: {str(post_to_comment.title)[:50]}... (id={post_to_comment.id})")

                comment_text = self.fetch_comment_text_from_gemini(post_to_comment.title, target_subreddit)
                logger.info(f"Replying to post id={post_to_comment.id} in subreddit r/{target_subreddit} with: {comment_text}")
                reply = post_to_comment.reply(comment_text)
                logger.info(f"Commented successfully in r/{target_subreddit}. Reply ID: {reply.id}, Reply body: {reply.body}")
                self._human_like_delay()
            except Exception as e:
                logger.error(f"Error interacting with post in r/{target_subreddit}: {e}")

if __name__ == "__main__":
    import sys

    logger.info("Starting Reddit Karma Bot...")

    try:
        bot = RedditKarmaBot()
        # Trigger the first action immediately
        action = random.choice(["repost", "comment"])
        if action == "repost":
            logger.info("Performing repost_content action")
            bot.repost_content()
        else:
            logger.info("Performing interact_with_posts action")
            bot.interact_with_posts()
        # Now enter the loop with human-like delays
        while True:
            bot._human_like_delay()
            action = random.choice(["repost", "comment"])
            if action == "repost":
                logger.info("Performing repost_content action")
                bot.repost_content()
            else:
                logger.info("Performing interact_with_posts action")
                bot.interact_with_posts()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}")
        sys.exit(1)
