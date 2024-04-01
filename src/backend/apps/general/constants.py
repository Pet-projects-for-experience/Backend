MAX_LENGTH_SKILL_NAME = 100

MAX_LENGTH_SPECIALIZATION_NAME = 100
MIN_LENGTH_SPECIALIZATION_NAME = 2
LENGTH_SPECIALIZATION_NAME_ERROR_TEXT = (
    f"Длина поля от {MIN_LENGTH_SPECIALIZATION_NAME} до "
    f"{MAX_LENGTH_SPECIALIZATION_NAME} символов."
)
REGEX_SPECIALIZATION_NAME = r"(^[A-Za-zА-Яа-яЁё\s\/]+)\Z"
REGEX_SPECIALIZATION_NAME_ERROR_TEXT = (
    "Специализация может содержать: кириллические и латинские символы,пробелы "
    "и символ /"
)

MAX_LENGTH_SPECIALTY_NAME = 50
MIN_LENGTH_SPECIALTY_NAME = 2
LENGTH_SPECIALTY_NAME_ERROR_TEXT = (
    f"Длина поля от {MIN_LENGTH_SPECIALTY_NAME} до "
    f"{MAX_LENGTH_SPECIALTY_NAME} символов."
)
REGEX_SPECIALTY_NAME = r"(^[A-Za-zА-Яа-яЁё]+)\Z"
REGEX_SPECIALTY_NAME_ERROR_TEXT = (
    "Специальность может содержать: кириллические и латинские символы."
)

MAX_LENGTH_TITLE = 100

MAX_LENGTH_DESCRIPTION = 250

MAX_LENGTH_EMAIL = 256

MAX_LENGTH_PHONE_NUMBER = 12
PHONE_NUMBER_REGEX = r"^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$"
PHONE_NUMBER_REGEX_ERROR_TEXT = (
    "Телефон может содержать: цифры, спецсимволы, длина не должна превышать "
    "12 символов"
)

MAX_LENGTH_TELEGRAM_NICK = 32
MIN_LENGTH_TELEGRAM_NICK = 5
LENGTH_TELEGRAM_NICK_ERROR_TEXT = (
    f"Длина поля от {MIN_LENGTH_TELEGRAM_NICK} до "
    f"{MAX_LENGTH_TELEGRAM_NICK} символов."
)
REGEX_TELEGRAM_NICK = r"^[a-zA-Z0-9_]+$"
REGEX_TELEGRAM_NICK_ERROR_TEXT = (
    "Введите корректное имя пользователя. Оно может состоять из латинских "
    "букв, цифр и символа подчеркивания."
)
LEVEL_CHOICES = (
    (1, "intern"),
    (2, "junior"),
    (3, "middle"),
    (4, "senior"),
    (5, "lead"),
)
