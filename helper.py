from secrets import token_hex
from typing import Any, Type
import re


def extract_from_json(body: dict, key: str, /, *, vtype: Type[Any]) -> Any:
    assert isinstance(body, dict), "Body was not a dict"
    assert body, "Body was empty"
    assert isinstance(key, str), f'{key}: "key" was not a string'
    assert isinstance(vtype, type), '"vtype" should be a class'
    assert key in body, f"{key}: not found in body"

    value = body.get(key)
    assert isinstance(value, vtype), f"{key}: value was not {vtype.__name__}"

    if vtype is str:
        value = value.strip()
        assert value, f"{key}: value was empty"

    return value


def id_generator():
    last_id = 0

    def next_id():
        nonlocal last_id
        last_id += 1
        return last_id

    return next_id


def generate_secret_key():
    return token_hex(16)


def check_username(username: str) -> str:
    assert isinstance(username, str), "username should be a string"
    username = username.strip()
    assert 3 <= len(username) <= 20, "username length should be in range [3,20]"
    assert re.fullmatch(
        r"(?i)[a-z0-9_.$]+", username
    ), "username should only consist of letters, numbers, underscores, dots or $"

    return username
