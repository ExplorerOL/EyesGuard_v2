from pathlib import Path as __Path

import loguru as __loguru

from support.paths import app_dir

__LOG_LEVEL_DEBUG = 'DEBUG'
__LOG_LEVEL_TRACE = 'TRACE'
__LOG_LEVEL_WARNING = 'WARNING'
__LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | '
    '{file}:{line}: <level><b>{message}</b></level>'
)

__LOG_FILE = app_dir() / 'logs' / 'log.log'

log_file_path = __Path(__LOG_FILE)
if log_file_path.exists():
    log_file_path.unlink(missing_ok=True)

logger = __loguru.logger

logger.add(
    sink=__LOG_FILE,
    level=__LOG_LEVEL_WARNING,
    format=__LOG_FORMAT,
    colorize=False,
    backtrace=True,
    diagnose=True,
    encoding='utf8',
)


logger.debug('Logging started!')
