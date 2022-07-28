from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    lang: str
    api_key: str
    secret_key: str

    def __init__(self, user_id: int, name: str, lang: str, api_key: str, secret_key: str):
        self.id = user_id
        self.name = name
        self.lang = lang
        self.api_key = api_key
        self.secret_key = secret_key
