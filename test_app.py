import unittest
from unittest.mock import patch, MagicMock
from app import RedditKarmaBot

class TestRedditKarmaBot(unittest.TestCase):
    @patch("app.ConfigManager")
    @patch("app.praw.Reddit")
    def setUp(self, mock_reddit, mock_config_manager):
        # Mock config manager and its methods
        mock_config = {
            "max_daily_actions": 2,
            "repost_subreddits": ["testsub1", "testsub2"],
            "comment_subreddits": ["testsub3"],
            "human_simulation": {
                "min_delay_between_actions": 1,
                "max_delay_between_actions": 2,
                "active_hours_start": 0,
                "active_hours_end": 24
            }
        }
        mock_config_manager.return_value.get_account.return_value = {
            "client_id": "id",
            "client_secret": "secret",
            "username": "user",
            "password": "pass",
            "user_agent": "agent"
        }
        mock_config_manager.return_value.config = mock_config
        self.mock_reddit = mock_reddit
        self.bot = RedditKarmaBot()

    @patch("app.RedditKarmaBot.fetch_posts")
    @patch("app.RedditKarmaBot._should_take_action", return_value=True)
    def test_repost_content(self, mock_should, mock_fetch):
        # Simulate a post object
        post = MagicMock()
        post.created_utc = 0  # Very old post
        post.title = "Test Title"
        post.url = "http://test.com"
        mock_fetch.return_value = [post]
        with patch.object(self.bot.reddit, "subreddit") as mock_subreddit:
            mock_subreddit.return_value.search.return_value = []
            with patch.object(self.bot, "_human_like_delay") as patched_delay:
                self.bot.repost_content()
                self.assertTrue(patched_delay.called)

    @patch("app.praw.Reddit")
    def test_initialize_reddit(self, mock_reddit):
        bot = RedditKarmaBot()
        self.assertIsNotNone(bot.reddit)
        self.assertTrue(mock_reddit.called)

    def test_fetch_comment_text_from_gemini(self):
        reply = self.bot.fetch_comment_text_from_gemini("Test body", "somesub")
        self.assertIn(",", reply)

    @patch("app.RedditKarmaBot.fetch_posts")
    def test_fetch_posts(self, mock_fetch):
        post = MagicMock()
        post.title = "Test Post"
        post.id = "abc123"
        mock_fetch.return_value = [post]
        posts = self.bot.fetch_posts("sometestsub", limit=1)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, "Test Post")

if __name__ == "__main__":
    unittest.main()
