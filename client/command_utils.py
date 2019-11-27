import re, json
from protocol import ClientProtocol


MSG_COMMANDS = [
    r"(/msg) (.+)", 
    r"(/private) (.+:.+)",
    r"(/exit)"
]

AUTH_COMMANDS = [
    r"(/login) ([a-zA-Z]+) ([a-zA-Z]+)",
    r"(/signup) ([a-zA-Z]+) ([a-zA-Z]+)",
    r"(/exit)"
]


def parse(raw, expect):
    for pattern in expect:
        match = re.match(pattern, raw)
        if match:
            return match.groups()
    else:
        raise AssertionError(f"Invalid input {raw}, Use one of {' '.join(expect)}")


def parse_command(raw, expect=MSG_COMMANDS):
    command, *message = parse(raw, expect)

    payload = ClientProtocol.new_payload(command, {"message": message[0] if message else None, "by": "user"})
    return payload


def parse_auth(raw, expect=AUTH_COMMANDS):
    command, *rest = parse(raw, expect)
    if len(rest) == 0:
        username = password = None
    else: 
        username, password = rest
    return ClientProtocol.new_payload(
        command, {"username": username, "password": password}
    )
