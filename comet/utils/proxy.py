import base64
from functools import cache
from urllib.parse import quote_plus, urlparse, urlunparse

from comet.utils.models import settings


@cache
def has_proxy_url_template():
    return bool(settings.PROXY_URL_TEMPLATE)


@cache
def get_proxy_basic_auth_credential():
    if not settings.PROXY_BASIC_AUTH_CREDENTIAL:
        return None
    if ":" in settings.PROXY_BASIC_AUTH_CREDENTIAL:
        return base64.b64encode(settings.PROXY_BASIC_AUTH_CREDENTIAL.encode()).decode(
            "ascii"
        )
    return settings.PROXY_BASIC_AUTH_CREDENTIAL


def _set_proxy_auth_url_creds(url: str):
    cred = get_proxy_basic_auth_credential()
    if not cred:
        return url
    u = urlparse(url)
    netloc = f"{cred}@{u.hostname}"
    if u.port:
        netloc += f":{u.port}"
    return urlunparse(u._replace(netloc=netloc))


def get_proxy_url(url: str, include_credential=False):
    if not settings.PROXY_URL_TEMPLATE:
        return url
    url = settings.PROXY_URL_TEMPLATE.replace("{URL}", quote_plus(f"{url}"))
    if include_credential:
        return _set_proxy_auth_url_creds(url)
    return url


def set_proxy_auth_header(headers: dict):
    if not settings.PROXY_BASIC_AUTH_CREDENTIAL:
        return headers
    headers["Proxy-Authorization"] = f"Basic {get_proxy_basic_auth_credential()}"
    return headers
