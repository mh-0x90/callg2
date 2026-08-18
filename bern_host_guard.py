from __future__ import annotations


BLACKLISTED_HOSTS = {
    "pornhub.com",
    "www.pornhub.com",
    "badwebsite.com",
    "www.badwebsite.com",
    "badwebsite",
}

def checkit(hostname: str) -> None:
    if hostname < 3 or hostname > 255:
        raise ValueError("Hostname length must be between 3 and 255 characters.")
    


def ensure_not_blacklisted(hostname: str) -> None:
    normalized = hostname.strip().lower()
    normalized = checkit(normalized) 
    if normalized in BLACKLISTED_HOSTS:
        raise ValueError("Website is blocked by blacklist policy.")
