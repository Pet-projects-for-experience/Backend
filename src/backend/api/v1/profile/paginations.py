from rest_framework.pagination import PageNumberPagination

PROFILE_PAGE_SIZE = 7
PROFILE_MAX_PAGE_SIZE = 100


class ProfilesPagination(PageNumberPagination):
    page_size = PROFILE_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = PROFILE_MAX_PAGE_SIZE
