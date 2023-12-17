import json
import re
from datetime import datetime
from secrets import token_hex
from typing import Any, Callable, Dict, List, Tuple, Type


def extract_from_json(
    body: dict, key: str, /, *, vtype: Type[Any] = None, required: bool = True
) -> Any:
    assert isinstance(body, dict), "Body was not a dict"
    assert body, "Body was empty"
    assert isinstance(key, str), f"{key}: 'key' was not a string"
    assert isinstance(required, bool), "'required' should be a boolean"

    if required:
        assert key in body, f"{key}: not found in body"

    value = body.get(key)
    if vtype is not None:
        if required or value is not None:
            assert isinstance(vtype, type), "'vtype' should be a class"
            assert isinstance(value, vtype), f"{key}: value was not {vtype.__name__}"

    return value


def id_generator() -> Callable:
    last_id = 0

    def next_id():
        nonlocal last_id
        last_id += 1
        return last_id

    return next_id


def generate_secret_key() -> str:
    return token_hex(16)


def ts_iso() -> str:
    return datetime.now().isoformat()


def check_str(s: str, what: str) -> Tuple[int, Tuple[Dict, int]]:
    if not isinstance(s, str):
        return s, ({"err": f"{s}: {what} should be a string"}, 400)

    s = s.strip()

    if not s:
        return s, ({"err": f"{what} should not be empty"}, 400)
    return s, None


def check_id(id: int, what: str = "id") -> Tuple[int, Tuple[Dict, int]]:
    if not isinstance(id, int):
        return id, ({"err": f"{what} should be an int"}, 400)
    if id < 0:
        return id, ({"err": f"{what} should be a non-negative int"}, 400)
    return id, None


def check_username(
    username: str, what: str = "username"
) -> Tuple[str, Tuple[Dict, int]]:
    username, err = check_str(username, what)
    if err:
        return username, err

    if not 3 <= len(username) <= 30:
        return username, ({"err": f"{what} length should be in range [3,30]"}, 400)
    if not re.fullmatch(r"(?i)[a-z0-9_.$]+", username):
        return username, (
            {
                "err": f"{what} should only consist of letters, numbers, underscores, dots or $"
            },
            400,
        )

    return username, None


def check_ts_iso(ts: str, what: str = "timestamp") -> Tuple[datetime, Tuple[Dict, int]]:
    ts, err = check_str(ts, what)
    if err:
        return ts, err

    if not re.fullmatch(
        r"(?:\d{4}-[01]\d-[0-3]\d[T ][0-2]\d:[0-5]\d:[0-5]\d(\.\d{3}|\.\d{6})?)(?:[Zz]|([+\-][0-2]\d:[0-5]\d))?",
        ts,
    ):
        return ts, ({"err": f"{ts}: {what} is not valid iso format"}, 400)

    if ts.endswith("Z"):
        ts = ts[:-1]

    try:
        ts = datetime.fromisoformat(ts)
    except ValueError as e:
        return ts, ({"err": str(e)}, 400)

    return ts, None


def purge_key_info(d: Dict) -> Tuple[Dict, Tuple[Dict, int]]:
    if not isinstance(d, dict):
        return d, ({"err": "Input is not a dictionary"}, 500)

    res = d.copy()
    keys_to_delete = [k for k in res if isinstance(k, str) and re.search(r"key", k)]
    for k in keys_to_delete:
        del res[k]

    return res, None


def deduplicate_dicts(
    a: List[Dict], b: List[Dict]
) -> Tuple[List[Dict], Tuple[Dict, int]]:
    if not isinstance(a, list):
        return [], ({"err": f"{a} was not a list"}, 500)
    if not all(isinstance(e, dict) for e in a):
        return [], ({"err": f"{a} was not a list of dicts"}, 500)
    if not isinstance(b, list):
        return [], ({"err": f"{b} was not a list"}, 500)
    if not all(isinstance(e, dict) for e in a):
        return [], ({"err": f"{b} was not a list of dicts"}, 500)

    json_str_deduplicated = set(json.dumps(d, sort_keys=True) for d in a + b)

    return [json.loads(js) for js in json_str_deduplicated], None


def dicts_intersection(
    a: List[Dict], b: List[Dict]
) -> Tuple[List[Dict], Tuple[Dict, int]]:
    if not isinstance(a, list):
        return [], ({"err": f"{a} was not a list"}, 500)
    if not all(isinstance(e, dict) for e in a):
        return [], ({"err": f"{a} was not a list of dicts"}, 500)
    if not isinstance(b, list):
        return [], ({"err": f"{b} was not a list"}, 500)
    if not all(isinstance(e, dict) for e in a):
        return [], ({"err": f"{b} was not a list of dicts"}, 500)

    intersection = {json.dumps(d, sort_keys=True) for d in a} & {
        json.dumps(d, sort_keys=True) for d in b
    }

    return [json.loads(d) for d in intersection], None
