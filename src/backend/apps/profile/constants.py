MAX_LENGTH_NAME = 30
MAX_LENGTH_COUNTRY = 255
MAX_LENGTH_CITY = 255
MAX_LENGTH_ABOUT = 1500

MAX_LENGTH_PORTFOLIO_URL = 256
MIN_LENGTH_PORTFOLIO_URL = 5
LENGTH_PORTFOLIO_URL_MESSAGE = (
    f"Длинна URL-адреса должна быть от {MIN_LENGTH_PORTFOLIO_URL} до "
    f"{MAX_LENGTH_PORTFOLIO_URL} символов."
)

MIN_LENGTH_NAME = 2
MIN_LENGTH_NAME_MESSAGE = "Должно быть минимум символов"
MIN_LENGTH_ABOUT = 20
REGEX_PROFILE_NAME = r"^[a-zA-Zа-яА-ЯёЁ-]+$"
REGEX_PROFILE_NAME_MESSAGE = "Введите кириллицу или латиницу"
REGEX_PROFILE_ABOUT = (
    r"^[\wа-яА-ЯёЁ0-9\s<>,.?!'\"/\-+:;@#\$%\^&\*\(\)\[\]\{\}]*$|^<.*>$"
)
REGEX_PROFILE_ABOUT_MESSAGE = "Введите кириллицу или латиницу"
MAX_SPECIALISTS = 2
MAX_BIRTHDAY_MESSAGE = "Дата не может быть в будущем."
MAX_SPECIALISTS_MESSAGE = (
    f"У одного профиля может быть не более "
    f"{MAX_SPECIALISTS} специальностей."
)
