from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')


DELAYS = {
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
}

PROXY_TYPES = {
    "TG": "http",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
    "REQUESTS": "http"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
}

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
