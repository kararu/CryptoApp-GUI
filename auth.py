import re
import hashlib as hl
import secrets


FORMAT = 'utf-8'

stored_fmt = re.compile(r'(.+)\$(.+)\$(.{64})\n')


class AlreadyRegistered(Exception):
    pass


def gen_pass(password: str) -> str:
    return hl.sha256(password.encode(FORMAT)).hexdigest()


def sign_up(username: str, password: str):
    salt = secrets.token_urlsafe(32)
    pass_hash = gen_pass(salt + password)
    with open('passwords.txt', 'r') as f:
        for m in re.finditer(stored_fmt, stored := f.read()):
            if m.group(1) == username:
                raise AlreadyRegistered
    with open("passwords.txt", "a") as f:
        f.write('$'.join((username, salt, pass_hash)) + '\n')

def sign_in(username: str, password: str):
    pass_hash = gen_pass(password)
    with open("passwords.txt", "r") as f:
        for m in re.finditer(stored_fmt, stored := f.read()):
            if username == m.group(1):
                salt = m.group(2)
                stored_password = m.group(3)
                return gen_pass(salt + password) == stored_password
