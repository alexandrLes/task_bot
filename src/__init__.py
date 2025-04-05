from .handlers import common, authors, executors
from . import keyboards, models, database, middlewares, utils

# Делаем основные компоненты доступными при импорте task_bot.bot
__all__ = [
    'common',
    'authors',
    'executors',
    'keyboards',
    'models',
    'database',
    'middlewares',
    'utils',
    'main'
]