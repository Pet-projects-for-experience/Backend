MAX_LENGTH_NAME = 30
MAX_LENGTH_COUNTRY = 255
MAX_LENGTH_CITY = 255
MAX_LENGTH_ABOUT = 750
MAX_LENGTH_URL = 256
MAX_LENGTH_URL_MESSAGE = "Введите корректный URL"
MIN_LENGTH_NAME = 2
MIN_LENGTH_NAME_MESSAGE = "Должно быть минимум символов"
MIN_LENGTH_ABOUT = 50
MIN_LENGTH_PORTFOLIO = 5
REGEX_PROFILE_NAME = r"^[a-zA-Zа-яА-Я -]+$"
REGEX_PROFILE_NAME_MESSAGE = "Введите кириллицу или латиницу"
REGEX_PROFILE_ABOUT = r"^[a-zA-Zа-яА-Я0-9\s!@#$%^&*()-_+=<>?]+$"
REGEX_PROFILE_ABOUT_MESSAGE = "Введите кириллицу или латиницу"
MAX_SPECIALISTS = 2
MAX_BIRTHDAY_MESSAGE = "Дата не может быть в будущем."
MAX_SPECIALISTS_MESSAGE = (
    "У одного профиля может быть не более {} специальностей."
)
