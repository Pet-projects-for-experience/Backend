PROJECT_PREVIEW_MAIN_PAGE_SIZE = 6
PROJECT_PAGE_SIZE = 7

PROJECT_PARTICIPATION_REQUEST_DESTROY_ONLY_FIELDS = (
    "user__id",
    "project__project_status",
)
PROJECT_PARTICIPATION_REQUEST_LIST_ONLY_FIELDS = (
    *PROJECT_PARTICIPATION_REQUEST_DESTROY_ONLY_FIELDS,
    "project__creator__id",
    "project__owner__id",
    "project__name",
    "project__directions",
    "request_status",
    "position__is_required",
    "position__profession",
    "position__count",
    "position__level",
    "is_viewed",
    "created",
)
PROJECT_PARTICIPATION_REQUEST_RETRIEVE_ONLY_FIELDS = (
    *PROJECT_PARTICIPATION_REQUEST_LIST_ONLY_FIELDS,
    "answer",
    "cover_letter",
)
PROJECT_PARTICIPATION_REQUEST_ONLY_FIELDS = {
    "destroy": PROJECT_PARTICIPATION_REQUEST_DESTROY_ONLY_FIELDS,
    "list": PROJECT_PARTICIPATION_REQUEST_LIST_ONLY_FIELDS,
    # "retrieve": PROJECT_PARTICIPATION_REQUEST_RETRIEVE_ONLY_FIELDS,
}
ALLOWED_TAGS_BY_FRONT = [
    "ol",
    "ul",
    "li",
    "em",
    "strong",
    "u",
    "br",
    "p",
    "span",
    # разрешенные теги котоыре не нужно очищать
]
ALLOWED_ATTRIBUTES_BY_FRONT = {
    "span": ["class", "style", "contenteditable"],
    # разрещенные атрибуты.
}
