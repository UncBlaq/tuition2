import logging
from logging.handlers import SysLogHandler

from tuition.config import Config

PAPERTRAIL_HOST = Config.PAPERTRAIL_HOST
PAPERTRAIL_PORT =  Config.PAPERTRAIL_PORT

handler = SysLogHandler(address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))

formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
handler.setFormatter(formatter)

# Setup root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add Papertrail handler
logger.addHandler(handler)
