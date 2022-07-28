import os
import sqlite3

from client import MyClient
from console import get_int_choice, get_line_data, get_user_action, get_user_language, show_variants
from datatypes import User


def db_connect(func, need_commit: bool = True, need_foreign_keys: bool = True):
    def _db_connect(*args, **kwargs):
        cursor = connection.cursor()
        if need_foreign_keys:
            cursor.execute('PRAGMA foreign_keys=on;')

        result = func(cursor, *args, **kwargs)

        if need_commit:
            connection.commit()
        cursor.close()
        return result

    return _db_connect


@db_connect
def add_log(cursor: sqlite3.Cursor, user_id: str, action: str, query: str, result: str):
    from datetime import datetime
    date = datetime.now().timestamp()
    cursor.execute('INSERT INTO history (user_id, date, action, query, result) \
                                         VALUES(:user_id, :date, :action, :query, :result);',
                   {'user_id': user_id, 'date': date, 'action': action, 'query': query, 'result': result})


@db_connect
def initialisation_database(cursor: sqlite3.Cursor):
    cursor.executescript('CREATE table users(id INTEGER PRIMARY KEY,\
                                             name TEXT,\
                                             lang TEXT,\
                                             api_key TEXT,\
                                             secret_key TEXT);\
                          CREATE table history(id INTEGER PRIMARY KEY,\
                                             user_id INTEGER,\
                                             date TEXT,\
                                             action TEXT,\
                                             query TEXT,\
                                             result TEXT,\
                                             FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE);')


@db_connect
def get_users_names(cursor: sqlite3.Cursor):
    names = cursor.execute('SELECT name FROM users;')
    names = names.fetchall()
    names = [name[0] for name in names]
    return names


@db_connect
def get_user(cursor: sqlite3.Cursor, name: str):
    user = cursor.execute('SELECT * FROM users WHERE name = :name;', {'name': name})
    user = user.fetchone()
    add_log(user[0], 'login', 'null', 'ok')
    return user


@db_connect
def get_history(cursor: sqlite3.Cursor, username: str):
    data = cursor.execute('SELECT history.* FROM history\
                           INNER JOIN users ON (history.user_id = users.id)\
                           WHERE name = :name;',
                          {'name': username})
    data = data.fetchall()
    return data


@db_connect
def add_user(cursor: sqlite3.Cursor, name: str, lang: str, api_key: str, secret_key: str):
    cursor.execute('INSERT INTO users (name, lang, api_key, secret_key) \
                                VALUES(:name, :lang, :api_key, :secret_key);',
                   {'name': name, 'lang': lang, 'api_key': api_key, 'secret_key': secret_key})


def main():
    global connection
    user_lang = 'ru'
    db_name = 'database.db'
    need_init_db = not os.path.isfile(db_name)
    connection = sqlite3.connect(db_name)
    if need_init_db:
        initialisation_database()
        list_users = []
    else:
        list_users = get_users_names()

    username = get_line_data(user_lang, 'username')

    if username not in list_users:
        user_lang = get_user_language()
        user_api = get_line_data(user_lang, 'API')
        user_secret_key = get_line_data(user_lang, 'secret_key')
        add_user(username, user_lang, user_api, user_secret_key)
    user = User(*get_user(username))

    dadata_client = MyClient(user)
    users_actions = [dadata_client.suggest, get_history]

    jumper_action = False
    jumper_new_address = True

    while True:
        if not jumper_action:
            message_action = {
                'ru': ['Получить координаты из адреса', 'История'],
                'en': ['Get coordinates by address', 'History'],
            }
            index_action = get_user_action(user.lang, message_action)

        jumper_action = False

        if index_action == 0:
            if jumper_new_address:
                user_query = get_line_data(user.lang, 'адрес' if user.lang == 'ru' else 'address')
            jumper_new_address = True
            user_action = 'suggestion'
            raw_data = users_actions[index_action](user_query)
            data = raw_data['suggestions']
            data = [item['unrestricted_value'] for item in data]
            show_variants(data)
            print('0. Выбрать другой адрес' if user.lang == 'ru' else \
                      '0. Choice other address')
            mid_index = get_int_choice(range(len(data) + 1), user.lang) - 1
            if mid_index == -1:
                jumper_action = True
            else:
                print(data[mid_index])
                user_query = data[mid_index]
                message_edit = {
                    'ru': ['Получить координаты этого места', 'Уточнить адрес'],
                    'en': ['Get coordinates this place', 'Clarify address'],
                }
                last_index = get_user_action(user.lang, message_edit)
                if last_index == 0:
                    longitude = raw_data['suggestions'][mid_index]['data']['geo_lon']
                    latitude = raw_data['suggestions'][mid_index]['data']['geo_lat']
                    user_result = f'lat: {latitude}, long: {longitude}'
                    add_log(user.id, user_action, user_query, user_result)
                    print(f'{latitude = }\t{longitude = }\n\n')
                elif last_index == 1:
                    jumper_action = True
                    jumper_new_address = False
                    address_adder = get_line_data(user.lang, '')
                    user_query = f'{user_query}, {address_adder}'

        elif index_action == 1:
            data = users_actions[index_action](user.name)
            show_variants(data)
            print('\n\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
