import logging
from logging.handlers import SysLogHandler

PAPERTRAIL_HOST = "logs2.papertrailapp.com"
PAPERTRAIL_PORT =  35336

handler = SysLogHandler(address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))

formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
handler.setFormatter(formatter)

# Setup root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add Papertrail handler
logger.addHandler(handler)


