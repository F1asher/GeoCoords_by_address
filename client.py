import requests

from datatypes import User


class MyClient:
    suggest_url = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address'

    def __init__(self, user: User):
        self.user = user
        self.session = requests.Session()
        self.session.headers['Content-type'] = 'application/json'
        self.session.headers['Accept'] = 'application/json'
        self.session.headers['Authorization'] = f'Token {user.api_key}'
        self.session.headers['X-Secret'] = user.secret_key
        # self.session.headers[''] = ''

    def _post(self, url: str, my_json: dict):
        response = self.session.post(url, json=my_json)
        return response.json() if response.status_code == 200 else None

    def suggest(self, address: str):
        my_json = {'query': address, 'count': 10, 'language': self.user.lang}
        return self._post(self.suggest_url, my_json)
