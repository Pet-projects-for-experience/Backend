from api.v1.general.paginations import BasePagination

from .constants import PROJECT_PAGE_SIZE, PROJECT_PREVIEW_MAIN_PAGE_SIZE


class ProjectPreviewMainPagination(BasePagination):
    page_size = PROJECT_PREVIEW_MAIN_PAGE_SIZE


class ProjectPagination(BasePagination):
    page_size = PROJECT_PAGE_SIZE
