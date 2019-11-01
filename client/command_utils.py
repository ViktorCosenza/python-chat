import re, json
from protocol import ClientProtocol


MSG_COMMANDS = [r"(/msg) (.+)"]

AUTH_COMMANDS = [
    r"(/login) ([a-zA-Z]+) ([a-zA-Z]+)",
    r"(/signup) ([a-zA-Z]+) ([a-zA-Z]+)",
]


def parse(raw, expect):
    for pattern in expect:
        match = re.match(pattern, raw)
        if match:
            return match.groups()
    else:
        raise AssertionError(f"Invalid input {raw}, Use one of {' '.join(expect)}")


def parse_command(raw, expect=MSG_COMMANDS):
    [command, msg] = parse(raw, expect=MSG_COMMANDS)
    return ClientProtocol.new_payload(command, {"message": msg, "by": "user"})


def parse_auth(raw, expect=AUTH_COMMANDS):
    command, username, password = parse(raw, expect)
    return ClientProtocol.new_payload(
        command, {"username": username, "password": password}
    )
