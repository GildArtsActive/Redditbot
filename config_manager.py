import os
import json
import random

CONFIG_FILE_PATH = "config.json"

class ConfigManager:
    def __init__(self, config_path=CONFIG_FILE_PATH):
        """Initialize the ConfigManager with the path to the configuration file."""
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Load the configuration from the JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file '{self.config_path}' not found.")
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")

    def get_account(self):
        """Retrieve a random account from the configuration for multi-account use."""
        accounts = self.config.get("accounts", [])
        if not accounts:
            raise ValueError("No accounts configured in the configuration file.")
        return random.choice(accounts)

    def get_human_simulation_settings(self):
        """Retrieve human simulation settings."""
        return self.config.get("human_simulation", {})

    def get_target_subreddits(self):
        """Retrieve the list of target subreddits."""
        return self.config.get("target_subreddits", [])

    def get_comment_subreddits(self):
        """Retrieve the list of subreddits for commenting."""
        return self.config.get("comment_subreddits", [])

    def get_repost_subreddits(self):
        """Retrieve the list of subreddits for reposting."""
        return self.config.get("repost_subreddits", [])

    def get_google_gemini_api_key(self):
        """Retrieve the Google Gemini API key."""
        return self.config.get("google_gemini_api_key", None)
