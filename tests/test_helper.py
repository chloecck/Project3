import unittest
from datetime import datetime
from helper import (
    extract_from_json,
    check_str,
    check_id,
    check_username,
    check_ts_iso,
    purge_key_info,
    deduplicate_dicts,
    dicts_intersection,
)
from faker import Faker


class TestExtractFromJson(unittest.TestCase):
    def setUp(self):
        fake = Faker()
        self.test_json = {
            "name": fake.name(),
            "age": fake.random_int(min=18, max=100),
            "email": fake.email(),
            "is_active": fake.boolean(),
        }

    def test_extract_existing_key(self):
        """Test extracting an existing key."""
        self.assertEqual(
            extract_from_json(self.test_json, "name"), self.test_json["name"]
        )

    def test_extract_key_with_type(self):
        """Test extracting a key with type validation."""
        self.assertEqual(
            extract_from_json(self.test_json, "age", vtype=int), self.test_json["age"]
        )

    def test_extract_optional_key(self):
        """Test extracting an optional key that does not exist."""
        self.assertIsNone(
            extract_from_json(self.test_json, "nonexistent", required=False)
        )

    def test_extract_required_key_not_present(self):
        """Test error when a required key is not present."""
        with self.assertRaises(AssertionError):
            extract_from_json(self.test_json, "nonexistent")

    def test_extract_with_wrong_type(self):
        """Test error when the type of the value does not match."""
        with self.assertRaises(AssertionError):
            extract_from_json(self.test_json, "age", vtype=str)

    def test_invalid_json_body(self):
        """Test error with an invalid JSON body (not a dict)."""
        with self.assertRaises(AssertionError):
            extract_from_json([], "name")

    def test_invalid_key_type(self):
        """Test error with an invalid key type (not a string)."""
        with self.assertRaises(AssertionError):
            extract_from_json(self.test_json, 123)

    def test_extract_with_dynamic_data(self):
        """Test extracting dynamically generated data."""
        fake = Faker()
        dynamic_key = fake.word()
        dynamic_value = fake.sentence()
        dynamic_json = {dynamic_key: dynamic_value}
        self.assertEqual(extract_from_json(dynamic_json, dynamic_key), dynamic_value)


class TestCheckStr(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_valid_str(self):
        """Test with valid strings."""
        valid_str = self.fake.sentence()
        checked_str, err = check_str(valid_str, "test")
        self.assertEqual(
            checked_str,
            valid_str.strip(),
            "Should return the original string, stripped",
        )
        self.assertIsNone(err, "Expected no error for a valid string")

    def test_empty_str(self):
        """Test with an empty string."""
        empty_str = ""
        checked_str, err = check_str(empty_str, "test")
        self.assertIsNotNone(err, "Expected an error for an empty string")

    def test_whitespace_str(self):
        """Test with a string containing only whitespace."""
        whitespace_str = "   "
        checked_str, err = check_str(whitespace_str, "test")
        self.assertIsNotNone(err, "Expected an error for a whitespace-only string")

    def test_non_string_input(self):
        """Test with non-string inputs."""
        non_str_input = self.fake.random_int()
        checked_str, err = check_str(non_str_input, "test")
        self.assertIsNotNone(err, "Expected an error for non-string input")


class TestCheckId(unittest.TestCase):
    def test_valid_id(self):
        """Test with a valid ID."""
        valid_id = 123
        checked_id, err = check_id(valid_id)
        self.assertEqual(checked_id, valid_id, "Should return the original ID")
        self.assertIsNone(err, "Expected no error for a valid ID")

    def test_negative_id(self):
        """Test with a negative ID."""
        negative_id = -123
        _, err = check_id(negative_id)
        self.assertIsNotNone(err, "Expected an error for a negative ID")

    def test_non_integer_id(self):
        """Test with non-integer ID."""
        non_integer_id = "123"
        _, err = check_id(non_integer_id)
        self.assertIsNotNone(err, "Expected an error for non-integer ID")

    def test_zero_id(self):
        """Test with zero as ID."""
        zero_id = 0
        checked_id, err = check_id(zero_id)
        self.assertEqual(checked_id, zero_id, "Should return zero as ID")
        self.assertIsNone(err, "Expected no error for zero as ID")


class TestCheckUsername(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_valid_username(self):
        """Test with a valid username."""
        valid_username = self.fake.user_name()
        checked_username, err = check_username(valid_username)
        self.assertEqual(
            checked_username, valid_username, "Should return the original username"
        )
        self.assertIsNone(err, "Expected no error for a valid username")

    def test_short_username(self):
        """Test with a short username."""
        short_username = "ab"
        _, err = check_username(short_username)
        self.assertIsNotNone(err, "Expected an error for a short username")

    def test_long_username(self):
        """Test with a long username."""
        long_username = "a" * 31  # 21 characters
        _, err = check_username(long_username)
        self.assertIsNotNone(err, "Expected an error for a long username")

    def test_username_with_invalid_characters(self):
        """Test with a username containing invalid characters."""
        invalid_username = "john*doe"
        _, err = check_username(invalid_username)
        self.assertIsNotNone(
            err, "Expected an error for invalid characters in username"
        )


class TestCheckTsIso(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_valid_ts_iso(self):
        """Test with a valid ISO timestamp."""
        valid_ts = self.fake.iso8601()
        ts, err = check_ts_iso(valid_ts)
        self.assertIsNone(err, "Expected no error for a valid ISO timestamp")
        self.assertTrue(
            isinstance(ts, datetime), "Returned object should be a datetime"
        )

    def test_invalid_ts_iso(self):
        """Test with an invalid ISO timestamp."""
        invalid_ts = "20210314T150926"  # Not ISO format
        _, err = check_ts_iso(invalid_ts)
        self.assertIsNotNone(err, "Expected an error for an invalid ISO timestamp")

    def test_empty_ts_iso(self):
        """Test with an empty string."""
        empty_ts = ""
        _, err = check_ts_iso(empty_ts)
        self.assertIsNotNone(err, "Expected an error for an empty string")


class TestPurgeKeyInfo(unittest.TestCase):
    def test_purge_keys(self):
        """Test purging of keys containing 'key'."""
        test_dict = {"name": "John", "apikey": "12345", "user_key": "abc123", "id": 1}
        purged_dict, err = purge_key_info(test_dict)
        self.assertIsNone(err, "Expected no error during purging")
        self.assertNotIn("apikey", purged_dict, "Key 'apikey' should be purged")
        self.assertNotIn("user_key", purged_dict, "Key 'user_key' should be purged")
        self.assertIn("name", purged_dict, "Key 'name' should not be purged")
        self.assertIn("id", purged_dict, "Key 'id' should not be purged")

    def test_invalid_input(self):
        """Test with invalid input (not a dictionary)."""
        _, err = purge_key_info("invalid_input")
        self.assertIsNotNone(err, "Expected an error for invalid input type")


class TestDeduplicateDicts(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_deduplicate_with_duplicates(self):
        """Test deduplication of dictionaries where duplicates exist."""
        dict_a = [{"name": "John"}, {"age": 30}]
        dict_b = [{"name": "John"}, {"city": "New York"}]
        deduplicated, err = deduplicate_dicts(dict_a, dict_b)
        self.assertIsNone(err, "Expected no error during deduplication")
        self.assertEqual(len(deduplicated), 3, "Should have 3 unique items")
        self.assertIn({"name": "John"}, deduplicated)
        self.assertIn({"age": 30}, deduplicated)
        self.assertIn({"city": "New York"}, deduplicated)

    def test_deduplicate_without_duplicates(self):
        """Test deduplication of dictionaries with no duplicates."""
        dict_a = [{"name": "John"}, {"age": 30}]
        dict_b = [{"city": "New York"}, {"country": "USA"}]
        deduplicated, err = deduplicate_dicts(dict_a, dict_b)
        self.assertIsNone(err, "Expected no error during deduplication")
        self.assertEqual(len(deduplicated), 4, "Should have 4 unique items")

    def test_deduplicate_empty_lists(self):
        """Test deduplication with empty lists."""
        deduplicated, err = deduplicate_dicts([], [])
        self.assertIsNone(err, "Expected no error with empty lists")
        self.assertEqual(len(deduplicated), 0, "Should have 0 items for empty lists")

    def test_invalid_input_non_list(self):
        """Test with invalid input where one input is not a list."""
        invalid_input = "not_a_list"
        _, err = deduplicate_dicts(invalid_input, [])
        self.assertIsNotNone(err, "Expected an error for non-list input")

    def test_invalid_input_non_dict_elements(self):
        """Test with invalid input where elements in the list are not dicts."""
        invalid_input = ["not_a_dict"]
        _, err = deduplicate_dicts(invalid_input, [])
        self.assertIsNotNone(err, "Expected an error for non-dict elements in the list")


class TestDictsIntersection(unittest.TestCase):
    def test_intersection_with_common_dicts(self):
        """Test finding the intersection of two lists with common dictionaries."""
        list_a = [{"name": "Alice"}, {"age": 30}]
        list_b = [{"name": "Alice"}, {"city": "New York"}]
        intersection, err = dicts_intersection(list_a, list_b)
        self.assertIsNone(err)
        self.assertEqual(len(intersection), 1)
        self.assertIn({"name": "Alice"}, intersection)

    def test_intersection_with_no_common_dicts(self):
        """Test finding the intersection of two lists with no common dictionaries."""
        list_a = [{"name": "Alice"}, {"age": 30}]
        list_b = [{"name": "Bob"}, {"city": "New York"}]
        intersection, err = dicts_intersection(list_a, list_b)
        self.assertIsNone(err)
        self.assertEqual(len(intersection), 0)

    def test_invalid_input_non_list(self):
        """Test with invalid input where one input is not a list."""
        invalid_input = "not_a_list"
        _, err = dicts_intersection(invalid_input, [])
        self.assertIsNotNone(err, "Expected an error for non-list input")

    def test_invalid_input_non_dict_elements(self):
        """Test with invalid input where elements in the list are not dicts."""
        invalid_input = ["not_a_dict"]
        _, err = dicts_intersection(invalid_input, [])
        self.assertIsNotNone(err, "Expected an error for non-dict elements in the list")

    def test_empty_lists(self):
        """Test the intersection of two empty lists."""
        intersection, err = dicts_intersection([], [])
        self.assertIsNone(err)
        self.assertEqual(len(intersection), 0)

    def test_intersection_with_identical_lists(self):
        """Test finding the intersection of two identical lists."""
        list_a = [{"name": "Alice"}, {"age": 30}]
        intersection, err = dicts_intersection(list_a, list_a.copy())
        self.assertIsNone(err)
        self.assertEqual(len(intersection), len(list_a))
        self.assertCountEqual(intersection, list_a)

    def test_intersection_with_subset(self):
        """Test finding the intersection where one list is a subset of the other."""
        list_a = [{"name": "Alice"}, {"age": 30}]
        list_b = [{"name": "Alice"}]
        intersection, err = dicts_intersection(list_a, list_b)
        self.assertIsNone(err)
        self.assertEqual(len(intersection), len(list_b))
        self.assertIn({"name": "Alice"}, intersection)

    def test_intersection_with_empty_and_nonempty_list(self):
        """Test the intersection of an empty list with a non-empty list."""
        list_a = []
        list_b = [{"name": "Alice"}, {"age": 30}]
        intersection, err = dicts_intersection(list_a, list_b)
        self.assertIsNone(err)
        self.assertEqual(len(intersection), 0)

    def test_intersection_with_different_structures(self):
        """Test the intersection of lists with different dictionary structures."""
        list_a = [{"name": "Alice", "age": 30}]
        list_b = [{"name": "Alice"}]
        intersection, err = dicts_intersection(list_a, list_b)
        self.assertIsNone(err)
        self.assertEqual(len(intersection), 0)

    def test_intersection_with_complex_dictionaries(self):
        """Test the intersection with more complex dictionary structures."""
        list_a = [{"data": {"id": 1, "value": "test"}, "active": True}]
        list_b = [{"data": {"id": 1, "value": "test"}, "active": True}]
        intersection, err = dicts_intersection(list_a, list_b)
        self.assertIsNone(err)
        self.assertEqual(len(intersection), 1)
        self.assertIn(
            {"data": {"id": 1, "value": "test"}, "active": True}, intersection
        )


if __name__ == "__main__":
    unittest.main()
