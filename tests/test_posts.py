import unittest
from unittest.mock import patch
from faker import Faker
from datetime import datetime, timedelta


from data.users import create_user
from data.posts import (
    create_post,
    get_post_by_id,
    delete_post,
    get_posts_by_time_range,
    get_posts_by_user,
    get_posts_by_queries,
)

MODULE_PATH = "data.posts"
_posts = {}


class TestCreatePost(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        self.test_user, err = self.create_test_user()

    @staticmethod
    def create_test_user():
        """Helper function to create a test user."""
        username = Faker().user_name()
        user_bio = Faker().text(max_nb_chars=50)
        # Assuming you have a create_user function in your users module
        user, err = create_user(username, user_bio)
        return user, err

    def test_create_post_valid(self):
        """Test creating a post with valid inputs."""
        fake_msg = self.fake.text()
        post, err = create_post(
            fake_msg,
            user_id=self.test_user["user_id"],
            user_key=self.test_user["user_key"],
        )
        self.assertIsNone(err, "Expected no error for valid post creation")
        self.assertEqual(post["msg"], fake_msg, "Post message should match input")

    def test_create_post_invalid_msg(self):
        """Test creating a post with an invalid message."""
        post, err = create_post(
            "", user_id=self.test_user["user_id"], user_key=self.test_user["user_key"]
        )
        self.assertIsNotNone(err, "Expected an error for invalid message")

    def test_create_post_without_user_id(self):
        """Test creating a post without providing a user ID."""
        fake_msg = self.fake.text()
        post, err = create_post(fake_msg, user_key=self.test_user["user_key"])
        self.assertIsNotNone(err, "Expected an error for missing user ID")

    def test_create_post_without_user_key(self):
        """Test creating a post without providing a user key."""
        fake_msg = self.fake.text()
        post, err = create_post(fake_msg, user_id=self.test_user["user_id"])
        self.assertIsNotNone(err, "Expected an error for missing user key")

    def test_create_post_with_invalid_reply_to(self):
        """Test creating a post with an invalid reply_to ID."""
        fake_msg = self.fake.text()
        invalid_reply_to = 99999  # Assuming this ID doesn't exist
        post, err = create_post(
            fake_msg,
            user_id=self.test_user["user_id"],
            user_key=self.test_user["user_key"],
            reply_to=invalid_reply_to,
        )
        self.assertIsNotNone(err, "Expected an error for invalid reply_to ID")

    def test_create_post_with_unmatched_user_key(self):
        """Test creating a post with a user key that does not match the user ID."""
        fake_msg = self.fake.text()
        wrong_key = "incorrect_key"
        post, err = create_post(
            fake_msg, user_id=self.test_user["user_id"], user_key=wrong_key
        )
        self.assertIsNotNone(err, "Expected an error for unmatched user key")


class TestGetPostById(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        # Creating a primary post
        self.primary_post, err = self.create_test_post()
        # Creating a reply post
        self.reply_post, err = self.create_test_post(
            reply_to=self.primary_post["post_id"]
        )

    @staticmethod
    def create_test_post(reply_to=None):
        """Helper function to create a test post."""
        fake = Faker()
        msg = fake.text(max_nb_chars=280)
        user, err = TestCreatePost.create_test_user()
        return create_post(
            msg, user_id=user["user_id"], user_key=user["user_key"], reply_to=reply_to
        )

    def test_get_post_by_id_valid(self):
        """Test retrieving a post by a valid ID."""
        post, err = get_post_by_id(self.primary_post["post_id"])
        self.assertIsNone(err, "Expected no error for valid post ID")
        self.assertEqual(
            post["post_id"], self.primary_post["post_id"], "Post IDs should match"
        )

    def test_get_post_with_replies(self):
        """Test retrieving a post that has replies."""
        post, err = get_post_by_id(self.primary_post["post_id"])
        self.assertIsNone(err, "Expected no error for valid post ID with replies")
        self.assertIn(
            self.reply_post["post_id"],
            post["replies"],
            "Reply post ID should be in the primary post's replies",
        )

    def test_get_post_by_id_invalid(self):
        """Test retrieving a post by an invalid ID."""
        invalid_post_id = 99999  # Assuming this ID doesn't exist
        post, err = get_post_by_id(invalid_post_id)
        self.assertIsNotNone(err, "Expected an error for invalid post ID")


class TestDeletePost(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        # Create a primary post and a reply post for testing
        self.primary_post, err = self.create_test_post()
        self.reply_post, err = self.create_test_post(
            reply_to=self.primary_post["post_id"]
        )

    @staticmethod
    def create_test_post(reply_to=None):
        """Helper function to create a test post."""
        fake = Faker()
        msg = fake.text(max_nb_chars=280)
        user, err = TestCreatePost.create_test_user()
        return create_post(
            msg, user_id=user["user_id"], user_key=user["user_key"], reply_to=reply_to
        )

    def test_delete_post_with_unspecified_key_type(self):
        """Test deleting a post without specifying key type."""
        _, err = delete_post(
            self.primary_post["post_id"], self.primary_post["user_key"]
        )
        self.assertIsNotNone(err, "Expected an error for unspecified key type")

    def test_delete_post_invalid_key(self):
        """Test deleting a post with an invalid key."""
        _, err = delete_post(
            self.primary_post["post_id"], "invalid_key", is_user_key=True
        )
        self.assertIsNotNone(err, "Expected an error for invalid key")

    def test_delete_post_invalid_post_id(self):
        """Test deleting a post with an invalid post ID."""
        invalid_post_id = 99999  # Assuming this ID doesn't exist
        _, err = delete_post(
            invalid_post_id, self.primary_post["user_key"], is_user_key=True
        )
        self.assertIsNotNone(err, "Expected an error for invalid post ID")

    def test_delete_post_with_wrong_key_type(self):
        """Test deleting a post with a mismatched key type."""
        _, err = delete_post(
            self.primary_post["post_id"],
            self.primary_post["post_key"],
            is_user_key=True,
        )
        self.assertIsNotNone(
            err, "Expected an error for using post key with is_user_key set to True"
        )

    def test_delete_post_valid_user_key(self):
        """Test deleting a post with a valid user key."""
        _, err = delete_post(
            self.primary_post["post_id"],
            self.primary_post["user_key"],
            is_user_key=True,
        )
        self.assertIsNone(
            err, "Expected no error for valid post deletion with user key"
        )

    def test_delete_post_valid_post_key(self):
        """Test deleting a post with a valid post key."""
        _, err = delete_post(
            self.reply_post["post_id"],
            self.reply_post["post_key"],
            is_user_key=False,
        )
        self.assertIsNone(
            err, "Expected no error for valid post deletion with post key"
        )

    def test_delete_post_already_deleted(self):
        """Test deleting a post that has already been deleted."""
        # Delete the post
        p1, e = delete_post(
            self.reply_post["post_id"],
            self.reply_post["post_key"],
            is_user_key=False,
        )
        # Attempt to delete again
        post, err = delete_post(
            self.reply_post["post_id"],
            self.reply_post["post_key"],
            is_user_key=False,
        )
        self.assertIsNotNone(
            err, "Expected an error for deleting an already deleted post"
        )


class TestGetPostsByTimeRange(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = Faker()
        cls.base_time = datetime.utcnow()  # Base time for controlled post creation

        # Populate _posts with controlled data
        global _posts
        _posts = {
            **cls.create_mock_post(time_delta=timedelta(days=-2)),  # 2 days ago
            **cls.create_mock_post(time_delta=timedelta(days=-1)),  # 1 day ago
            **cls.create_mock_post(time_delta=timedelta(hours=-1)),  # 1 hour ago
            **cls.create_mock_post(
                time_delta=timedelta(minutes=30)
            ),  # 30 minutes from now
        }

    @classmethod
    def create_mock_post(cls, time_delta):
        """Creates a mock post with a timestamp offset by time_delta."""
        post_time = cls.base_time + time_delta
        post_id = cls.fake.random_number(digits=5)
        return {
            post_id: {
                "post_id": post_id,
                "timestamp": post_time.isoformat(),
                "user_id": cls.fake.random_number(digits=5),
                "username": cls.fake.user_name(),
                # ... other fields ...
            }
        }

    def test_posts_within_past_day(self):
        """Test retrieving posts within the past day."""
        start_time = (self.base_time - timedelta(days=1)).isoformat()
        end_time = self.base_time.isoformat()
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_time_range(start=start_time, end=end_time)
            self.assertIsNone(err)
            self.assertTrue(
                all(start_time <= post["timestamp"] <= end_time for post in posts)
            )

    def test_posts_within_specific_range(self):
        """Test retrieving posts within a specific time range."""
        # Define a specific range
        start_time = (self.base_time - timedelta(hours=1, minutes=30)).isoformat()
        end_time = (self.base_time + timedelta(minutes=10)).isoformat()
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_time_range(start=start_time, end=end_time)
            self.assertIsNone(err)
            # Assertions to check posts are within the specific range

    def test_no_posts_in_future_range(self):
        """Test retrieving no posts in a future time range."""
        start_time = (self.base_time + timedelta(days=1)).isoformat()
        end_time = (self.base_time + timedelta(days=2)).isoformat()
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_time_range(start=start_time, end=end_time)
            self.assertIsNone(err)
            self.assertEqual(
                len(posts), 0, "Should return no posts for a future time range"
            )

    def test_invalid_start_time_format(self):
        """Test with an invalid start time format."""
        invalid_start_time = "2021-13-01T00:00:00"  # Invalid month
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            _, err = get_posts_by_time_range(start=invalid_start_time)
            self.assertIsNotNone(err, "Expected an error for invalid start time format")

    def test_start_time_after_end_time(self):
        """Test with start time after end time."""
        start_time = (self.base_time + timedelta(days=1)).isoformat()
        end_time = self.base_time.isoformat()  # Earlier than start_time
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            _, err = get_posts_by_time_range(start=start_time, end=end_time)

            self.assertIsNotNone(
                err, "Expected an error when start time is after end time"
            )

    def test_posts_without_time_range(self):
        """Test retrieving posts without specifying time range."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            _, err = get_posts_by_time_range()
            self.assertIsNotNone(
                err, "Expected an error when no time range is specified"
            )


class TestGetPostsByUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = Faker()
        cls.base_time = datetime.utcnow()

        global _posts
        _posts = {
            **cls.create_mock_post(user_id=1, username="user1"),
            **cls.create_mock_post(user_id=2, username="user2"),
            **cls.create_mock_post(user_id=1, username="user1"),
            **cls.create_mock_post(user_id=3, username="user3"),
        }

    @classmethod
    def create_mock_post(cls, user_id, username):
        post_time = cls.base_time + timedelta(
            minutes=cls.fake.random_int(min=1, max=60)
        )
        post_id = cls.fake.random_number(digits=5)
        return {
            post_id: {
                "post_id": post_id,
                "timestamp": post_time.isoformat(),
                "user_id": user_id,
                "username": username,
                # ... other fields ...
            }
        }

    def test_posts_by_specific_user_id(self):
        """Test retrieving posts for a specific user ID."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            user_id = 1
            posts, err = get_posts_by_user(user_id=user_id, username=None)
            self.assertIsNone(err)
            self.assertTrue(all(post["user_id"] == user_id for post in posts))

    def test_posts_by_specific_username(self):
        """Test retrieving posts for a specific username."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            username = "user2"
            posts, err = get_posts_by_user(user_id=None, username=username)
            self.assertIsNone(err)
            self.assertTrue(all(post["username"] == username for post in posts))

    def test_posts_by_nonexistent_user(self):
        """Test retrieving posts for a nonexistent user."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            user_id = 999  # Assuming this user ID does not exist in mock data
            posts, err = get_posts_by_user(user_id=user_id, username=None)
            self.assertIsNone(err)
            self.assertEqual(
                len(posts), 0, "Should return no posts for a nonexistent user"
            )

    def test_posts_by_user_id_and_username(self):
        """Test retrieving posts for a specific user ID and username combination."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            user_id = 1
            username = "user1"
            posts, err = get_posts_by_user(user_id=user_id, username=username)
            self.assertIsNone(err)
            self.assertTrue(
                all(
                    post["user_id"] == user_id and post["username"] == username
                    for post in posts
                )
            )

    def test_posts_with_invalid_user_id(self):
        """Test retrieving posts with an invalid user ID."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            invalid_user_id = "invalid_id"  # Non-integer user ID
            posts, err = get_posts_by_user(user_id=invalid_user_id, username=None)
            self.assertIsNotNone(err, "Expected an error for invalid user ID type")

    def test_posts_with_invalid_username(self):
        """Test retrieving posts with an invalid username."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            invalid_username = 12345  # Non-string username
            posts, err = get_posts_by_user(user_id=None, username=invalid_username)
            self.assertIsNotNone(err, "Expected an error for invalid username type")

    def test_posts_with_blank_username(self):
        """Test retrieving posts with a blank username."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            blank_username = ""
            posts, err = get_posts_by_user(user_id=None, username=blank_username)
            self.assertIsNotNone(err, "Expected an error for blank username")


class TestGetPostsByQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = Faker()
        cls.base_time = datetime.utcnow()

        global _posts
        _posts = {
            **cls.create_mock_post(
                time_delta=timedelta(days=-2), user_id=1, username="user1"
            ),
            **cls.create_mock_post(
                time_delta=timedelta(days=-1), user_id=2, username="user2"
            ),
            **cls.create_mock_post(
                time_delta=timedelta(hours=-1), user_id=1, username="user1"
            ),
            **cls.create_mock_post(
                time_delta=timedelta(minutes=30), user_id=3, username="user3"
            ),
        }

    @classmethod
    def create_mock_post(cls, time_delta, user_id, username):
        post_time = cls.base_time + time_delta
        post_id = cls.fake.random_number(digits=5)
        return {
            post_id: {
                "post_id": post_id,
                "timestamp": post_time.isoformat(),
                "user_id": user_id,
                "username": username,
                # ... other fields ...
            }
        }

    def test_queries_by_time_and_user(self):
        """Test retrieving posts by combined time range and user filters."""
        start_time = (self.base_time - timedelta(days=1)).isoformat()
        end_time = self.base_time.isoformat()
        user_id = 1
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_queries(
                start=start_time, end=end_time, user_id=user_id
            )
            self.assertIsNone(err)
            self.assertTrue(
                all(
                    start_time <= post["timestamp"] <= end_time
                    and post["user_id"] == user_id
                    for post in posts
                )
            )

    def test_queries_with_invalid_time(self):
        """Test error handling for invalid time formats."""
        invalid_time = "invalid_time"
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            _, err = get_posts_by_queries(start=invalid_time)
            self.assertIsNotNone(err, "Expected an error for invalid time format")

    def test_queries_with_nonexistent_user(self):
        """Test retrieving posts for a nonexistent user."""
        user_id = 999  # Assuming this user ID does not exist in mock data
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_queries(user_id=user_id)
            self.assertIsNone(err)
            self.assertEqual(
                len(posts), 0, "Should return no posts for a nonexistent user"
            )

    def test_queries_with_empty_parameters(self):
        """Test retrieving posts with all parameters empty."""
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_queries()
            self.assertIsNotNone(
                err, "Expected an error when no parameters are provided"
            )

    def test_queries_with_only_username(self):
        """Test retrieving posts for a specific username without other filters."""
        username = "user1"
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_queries(username=username)
            self.assertIsNone(err)
            self.assertTrue(all(post["username"] == username for post in posts))

    def test_queries_with_future_time_range(self):
        """Test retrieving posts within a future time range."""
        future_start = (self.base_time + timedelta(days=1)).isoformat()
        future_end = (self.base_time + timedelta(days=2)).isoformat()
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_queries(start=future_start, end=future_end)
            self.assertIsNone(err)
            self.assertEqual(
                len(posts), 0, "Should return no posts for a future time range"
            )

    def test_queries_with_past_time_range_no_user(self):
        """Test retrieving posts within a past time range without specifying a user."""
        past_start = (self.base_time - timedelta(days=2)).isoformat()
        past_end = (self.base_time - timedelta(days=1)).isoformat()
        with patch(f"{MODULE_PATH}._posts", new=_posts):
            posts, err = get_posts_by_queries(start=past_start, end=past_end)
            self.assertIsNone(err)
            # Assertions to check if posts fall within the specified past time range


if __name__ == "__main__":
    unittest.main()
