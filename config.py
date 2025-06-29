import os

from dotenv import load_dotenv

load_dotenv()  

DATABASE_URL = os.getenv("DATABASE_URL")
USE_SEARCH_SERVICE = os.getenv("USE_SEARCH_SERVICE", "true").lower() == "true"


