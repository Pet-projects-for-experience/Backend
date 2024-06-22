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
MIN_LENGTH_EMAIL = 5
LENGTH_EMAIL_ERROR_TEXT = (
    f"Длина поля от {MIN_LENGTH_EMAIL} до {MAX_LENGTH_EMAIL} символов."
)

MAX_LENGTH_PHONE_NUMBER = 12
REGEX_PHONE_NUMBER = r"^\+7\d{10}$"
REGEX_PHONE_NUMBER_ERROR_TEXT = (
    "Допустимый формат +7XXXXXXXXXX, где X - цифры."
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
    (1, "junior"),
    (2, "middle"),
    (3, "senior"),
    (4, "lead"),
)

MAX_LENGTH_BASE_TEXT_FIELD = 750
MIN_LENGTH_BASE_TEXT_FIELD = 5
LENGTH_BASE_TEXT_FIELD_ERROR_TEXT = (
    f"Длина поля от {MIN_LENGTH_BASE_TEXT_FIELD} до "
    f"{MAX_LENGTH_BASE_TEXT_FIELD} символов."
)
REGEX_BASE_TEXT_FIELD = r"(^[-%!#$&*'+/=?^_;():@,.<>`{|}~-«»0-9A-ZА-ЯЁ\s]+)\Z"
REGEX_BASE_TEXT_FIELD_ERROR_TEXT = (
    "Поле может содержать: кириллические и латинские символы, цифры и "
    "спецсимовлы -!#$%%&'*+/=?^_;():@,.<>`{}~«»"
)

MAX_SKILLS = 15
MAX_SKILLS_MESSAGE = (
    f"У одной специальности может быть не более {MAX_SKILLS} навыков."
)

MAX_LENGTH_URL = 256
