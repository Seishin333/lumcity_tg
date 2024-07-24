# api id, hash
API_ID = 26299957
API_HASH = 'fbf2ca8a79b7510a7cd54f20283f540c'


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