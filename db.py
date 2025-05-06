import json

from config import starboard_file


try:
    with open(starboard_file, 'r') as file:
        starboard_messages = json.load(file)
except FileNotFoundError:
    starboard_messages = {}


def get_starboard_message_id(orig_mid):
    return starboard_messages.get(str(orig_mid), None)

# Сохранение или обновление информации о сообщении в JSON файле
def save_starboard_message(orig_mid, star_mid) -> None:
    starboard_messages[str(orig_mid)] = star_mid
    save_starboard_messages()

# Удаление записи из JSON файла
def delete_starboard_message(orig_mid) -> None:
    if str(orig_mid) in starboard_messages:
        del starboard_messages[str(orig_mid)]
        save_starboard_messages()

# Сохранение данных в JSON файл
def save_starboard_messages() -> None:
    with open(starboard_file, 'w') as f:
        json.dump(starboard_messages, f, indent=4)