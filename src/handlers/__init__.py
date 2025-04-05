from .authors import router as authors_router
from .common import router as common_router
from .executors import router as executors_router

__all__ = [
    'common_router',
    'authors_router',
    'executors_router'
]