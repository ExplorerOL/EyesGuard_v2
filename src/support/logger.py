import sys as __sys

import loguru as __loguru

from support.paths import app_dir

__LOG_LEVEL_DEBUG = 'DEBUG'
__LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | '
    '{file}:{line}: <level><b>{message}</b></level>'
)

__LOG_FILE = app_dir() / 'logs' / 'log.log'

__LOG_ROTATION = '5 MB'
__LOG_RETENTION = 5

logger = __loguru.logger

try:
    logger.add(
        sink=__LOG_FILE,
        level=__LOG_LEVEL_DEBUG,
        format=__LOG_FORMAT,
        colorize=False,
        backtrace=True,
        diagnose=True,
        encoding='utf8',
        rotation=__LOG_ROTATION,
        retention=__LOG_RETENTION,
    )
except Exception as __error:  # noqa: BLE001 — logging setup must never crash the app
    # broken file sink (unwritable directory, disk full): fall back to stderr
    __sys.stderr.write(f'Failed to add file log sink {__LOG_FILE}: {__error!r}\n')
    logger.add(sink=__sys.stderr, level=__LOG_LEVEL_DEBUG, format=__LOG_FORMAT)


logger.debug('Logging started!')
