import os
from dotenv import load_dotenv

load_dotenv()

# Accurate API Token credentials
# API Token  : obtained from the user's Accurate Store > API Token page
# Sig Secret : "Signature Secret" shown in Developer Area > Application > API Token tab
ACCURATE_API_TOKEN       = os.getenv("ACCURATE_API_TOKEN", "")
ACCURATE_SIGNATURE_SECRET = os.getenv("ACCURATE_SIGNATURE_SECRET", "")

# Base host for the company's Accurate database
# e.g. https://zeus.accurate.id  (the host shown in the API Token JSON response)
ACCURATE_HOST = os.getenv("ACCURATE_HOST", "https://yoursubdomain.accurate.id")

# ClickHouse Database
CH_HOST     = os.getenv("CH_HOST", "localhost")
CH_PORT     = int(os.getenv("CH_PORT", "8123"))   # HTTP port (native: 9000)
CH_DATABASE = os.getenv("CH_DATABASE", "accurate_data")
CH_USER     = os.getenv("CH_USER", "default")
CH_PASSWORD = os.getenv("CH_PASSWORD", "")
CH_SECURE   = os.getenv("CH_SECURE", "false").lower() == "true"

# Sync settings
PAGE_SIZE             = int(os.getenv("PAGE_SIZE", "100"))
SYNC_INTERVAL_MINUTES = int(os.getenv("SYNC_INTERVAL_MINUTES", "60"))
