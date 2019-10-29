from imports import re, json
from protocol import ClientProtocol


def parse_auth(raw, expect):
    for pattern in expect:
        match = re.match(pattern, raw)
        if match:
            command, username, password = match.groups()
            break
    else:
        raise AssertionError(f"Invalid input {raw}, Use one of {' '.join(expect)}")
    return ClientProtocol.new_payload(
        command, {"username": username, "password": password}
    )
