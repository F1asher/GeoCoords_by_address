from typing import Iterable


def input_handler(message: str = ''):
    data = input(message)
    if '.exit' in data or '.выход' in data:
        exit()
    return data


def show_variants(data: Iterable[str]):
    for pos, item in enumerate(data, 1):
        print(f'{pos}. {item}')


def get_int_choice(success_values: range, user_lang: str):
    error_message = {
        'ru': 'Упс... Попробуйте снова',
        'en': 'Oops... Try again',
    }
    choice_message = {
        'ru': 'Выберите номер',
        'en': 'Choice number',
    }
    user_choice = None
    while user_choice not in success_values:
        if user_choice is not None:
            print(error_message[user_lang])
        user_choice = input_handler(f'{choice_message[user_lang]}\n')
        try:
            user_choice = int(user_choice)
        except ValueError:
            pass
    return user_choice


def get_user_language():
    languages = (
        ('ru', 'Русский'),
        ('en', 'English'),
    )
    print('Выберите язык')
    show_variants([lang[1] for lang in languages])
    lang_index = get_int_choice(range(1, len(languages) + 1), 'ru')
    return languages[lang_index - 1][0]


def show_message(user_lang: str):
    message = {
        'ru': 'Введите',
        'en': 'Enter',
    }
    print(f'{message[user_lang]} ', end='')


def get_line_data(user_lang: str, name_data: str):
    show_message(user_lang)
    print(name_data)
    username = input_handler().strip().lower().replace(' ', '_').replace('\\', '')
    return username


def get_user_action(user_lang: str, message_by_lang: dict):
    show_variants(message_by_lang[user_lang])
    index_action = get_int_choice(range(1, len(message_by_lang[user_lang]) + 1), user_lang) - 1
    return index_action
