import unittest
from faker import Faker
from data.users import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_unique_metadata,
    get_non_unique_metadata,
    get_metadata,
    update_metadata,
)


class TestCreateUser(unittest.TestCase):
    def setUp(self):
        # Initialize Faker
        self.fake = Faker()

    def test_create_user_success(self):
        """Test creating a user with valid inputs."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()

        user, err = create_user(fake_username, fake_user_bio)

        self.assertIsNone(err, "Expected no error for valid input")
        self.assertIn(
            "user_id", user, "User ID should be present in returned user data"
        )
        self.assertEqual(user["username"], fake_username, "Username should match input")
        self.assertEqual(user["user_bio"], fake_user_bio, "User bio should match input")

    def test_create_user_with_existing_username(self):
        """Test creating a user with an existing username."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()

        # Create a user with the fake data
        create_user(fake_username, fake_user_bio)

        # Attempt to create another user with the same username
        user, err = create_user(fake_username, self.fake.text())

        self.assertIsNotNone(err, "Expected an error for duplicate username")
        self.assertIn("username already exists", err[0]["err"])

    def test_create_user_invalid_username(self):
        """Test creating a user with an invalid username."""
        invalid_username = ""  # or any other invalid criteria
        fake_user_bio = self.fake.text()
        user, err = create_user(invalid_username, fake_user_bio)
        self.assertIsNotNone(err, "Expected an error for invalid username")

    def test_create_user_empty_inputs(self):
        """Test creating a user with empty inputs."""
        user, err = create_user("", "")
        self.assertIsNotNone(err, "Expected an error for empty inputs")

    def test_create_multiple_unique_users(self):
        """Test creating multiple unique users."""
        usernames = set(self.fake.user_name() for _ in range(5))
        for username in usernames:
            user, err = create_user(username, self.fake.text())
            self.assertIsNone(err, "Expected no error for unique username: " + username)
            self.assertIn(
                "user_id", user, f"User ID should be present for username: {username}"
            )


class TestGetUserById(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_get_user_by_id_valid(self):
        """Test retrieving a user by a valid ID."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()
        user, _ = create_user(fake_username, fake_user_bio)
        user_id = user["user_id"]

        retrieved_user, err = get_user_by_id(user_id)
        self.assertIsNone(err, "Expected no error for valid user ID")
        self.assertEqual(
            retrieved_user["username"], fake_username, "Usernames should match"
        )

    def test_get_user_by_id_invalid(self):
        """Test retrieving a user by an invalid ID."""
        invalid_id = 99999  # Assuming this ID doesn't exist
        user, err = get_user_by_id(invalid_id)
        self.assertIsNotNone(err, "Expected an error for invalid user ID")


class TestGetUserByUsername(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_get_user_by_username_valid(self):
        """Test retrieving a user by a valid username."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()
        create_user(fake_username, fake_user_bio)

        user, err = get_user_by_username(fake_username)
        self.assertIsNone(err, "Expected no error for valid username")
        self.assertEqual(user["username"], fake_username, "Usernames should match")

    def test_get_user_by_username_invalid(self):
        """Test retrieving a user by an invalid username."""
        invalid_username = "nonexistent_user"
        user, err = get_user_by_username(invalid_username)
        self.assertIsNotNone(err, "Expected an error for invalid username")


class TestGetUniqueMetadata(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_get_unique_metadata_by_id_valid(self):
        """Test retrieving unique metadata by a valid user ID."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()
        created_user, _ = create_user(fake_username, fake_user_bio)
        user_id = created_user["user_id"]

        metadata, err = get_unique_metadata(user_id=user_id)
        self.assertIsNone(err, "Expected no error for valid user ID")
        self.assertEqual(metadata["username"], fake_username, "Username should match")

    def test_get_unique_metadata_by_username_valid(self):
        """Test retrieving unique metadata by a valid username."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()
        create_user(fake_username, fake_user_bio)

        metadata, err = get_unique_metadata(username=fake_username)
        self.assertIsNone(err, "Expected no error for valid username")
        self.assertIn("user_id", metadata, "Metadata should contain user_id")

    def test_get_unique_metadata_invalid(self):
        """Test retrieving unique metadata with invalid parameters."""
        metadata, err = get_unique_metadata()
        self.assertIsNotNone(err, "Expected an error for missing parameters")


class TestGetNonUniqueMetadata(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_get_non_unique_metadata_valid(self):
        """Test retrieving non-unique metadata for a valid user."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()
        created_user, _ = create_user(fake_username, fake_user_bio)
        user_id = created_user["user_id"]

        metadata, err = get_non_unique_metadata(user_id=user_id)
        self.assertIsNone(err, "Expected no error for valid user ID")
        self.assertEqual(metadata["user_bio"], fake_user_bio, "User bio should match")

    def test_get_non_unique_metadata_invalid(self):
        """Test retrieving non-unique metadata with invalid parameters."""
        metadata, err = get_non_unique_metadata()
        self.assertIsNotNone(err, "Expected an error for missing parameters")


class TestGetMetadata(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_get_metadata_valid(self):
        """Test retrieving combined metadata for a valid user."""
        fake_username = self.fake.user_name()
        fake_user_bio = self.fake.text()
        created_user, _ = create_user(fake_username, fake_user_bio)
        user_id = created_user["user_id"]

        metadata, err = get_metadata(user_id=user_id)
        self.assertIsNone(err, "Expected no error for valid user ID")
        self.assertEqual(metadata["username"], fake_username, "Username should match")
        self.assertEqual(metadata["user_bio"], fake_user_bio, "User bio should match")

    def test_get_metadata_invalid(self):
        """Test retrieving metadata with invalid parameters."""
        metadata, err = get_metadata()
        self.assertIsNotNone(err, "Expected an error for missing parameters")


class TestUpdateMetadata(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_update_metadata_valid(self):
        """Test updating metadata with valid data."""
        # Create an initial user
        original_username = self.fake.user_name()
        original_user_bio = self.fake.text()
        created_user, _ = create_user(original_username, original_user_bio)
        user_id = created_user["user_id"]
        user_key = created_user["user_key"]

        # New data for update
        new_username = self.fake.user_name()
        new_user_bio = self.fake.text()

        # Update user data
        updated_user, err = update_metadata(
            user_id, user_key, new_username, new_user_bio
        )
        self.assertIsNone(err, "Expected no error for valid update")
        self.assertEqual(
            updated_user["username"], new_username, "Username should be updated"
        )
        self.assertEqual(
            updated_user["user_bio"], new_user_bio, "User bio should be updated"
        )

    def test_update_metadata_invalid_user_id(self):
        """Test updating metadata with an invalid user ID."""
        invalid_user_id = 99999  # Assuming this ID doesn't exist
        user_key = "some_key"
        new_username = self.fake.user_name()
        new_user_bio = self.fake.text()

        updated_user, err = update_metadata(
            invalid_user_id, user_key, new_username, new_user_bio
        )
        self.assertIsNotNone(err, "Expected an error for invalid user ID")

    def test_update_metadata_wrong_key(self):
        """Test updating metadata with a wrong user key."""
        # Create an initial user
        original_username = self.fake.user_name()
        original_user_bio = self.fake.text()
        created_user, _ = create_user(original_username, original_user_bio)
        user_id = created_user["user_id"]

        # Attempt to update with a wrong key
        wrong_key = "wrong_key"
        new_username = self.fake.user_name()
        new_user_bio = self.fake.text()

        updated_user, err = update_metadata(
            user_id, wrong_key, new_username, new_user_bio
        )
        self.assertIsNotNone(err, "Expected an error for wrong user key")

    def test_update_metadata_duplicate_username(self):
        """Test updating metadata with a username that already exists."""
        # Create two users
        first_username = self.fake.user_name()
        second_username = self.fake.user_name()
        user_bio = self.fake.text()
        first_user, _ = create_user(first_username, user_bio)
        second_user, _ = create_user(second_username, user_bio)

        # Attempt to update the second user's username to the first user's username
        updated_user, err = update_metadata(
            second_user["user_id"], second_user["user_key"], first_username, user_bio
        )
        self.assertIsNotNone(err, "Expected an error for duplicate username")


if __name__ == "__main__":
    unittest.main()
