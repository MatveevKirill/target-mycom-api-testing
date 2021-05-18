import os


class NotFoundCredsFileException(Exception):
    pass


class Credentials:
    LOGIN: str = None
    PASSWORD: str = None

    def __init__(self):
        if os.path.exists('creds'):
            with open('creds', 'r') as f:
                self.LOGIN, self.PASSWORD = f.read().split(':')
        else:
            raise NotFoundCredsFileException('File "creds" not found.')
