import os
import logging
logger = logging.getLogger(__name__)
from fastapi.templating import Jinja2Templates
# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define BASE_DIR and templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "tuition", "templates"))

# Check if template exists
template_path = os.path.join(BASE_DIR, 'tuition', 'student', 'crud.py')
if not os.path.exists(template_path):
    logger.error(f"Template file does not exist: {template_path}")
else:
    logger.info(f"Template file found: {template_path}")

# BASE_DIR = Path(__file__).resolve().parent
BASE_DIR = os.path.dirname(os.path.abspath(__file__))