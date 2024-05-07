from api.v1.general.paginations import BasePagination

from .constants import PROFILES_PAGE_SIZE


class ProfilesPagination(BasePagination):
    page_size = PROFILES_PAGE_SIZE
