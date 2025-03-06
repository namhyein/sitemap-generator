from typing import Optional
from datetime import datetime, timezone, timedelta

from chalicelib.settings import SERVICE_URL, IMAGE_URL


def utc_now(_format: str = "%Y-%m-%d") -> str:
    return datetime.now(timezone.utc).strftime(_format)


def n_days_before(n, _format: str = "%Y-%m-%d") -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime(_format)


def convert_timestamp_to_string(timestamp: int, _format: str = "%Y-%m-%d") -> str:
    return datetime.fromtimestamp(timestamp).strftime(_format)


def cleanse_image_url(url: Optional[str]) -> str:
    if not url:
        return f'{IMAGE_URL}/default/ogImage.png'

    if not url.startswith(IMAGE_URL) and url.startswith("https://"):
        return f'{IMAGE_URL}/{url.replace("https://", "").split("/", 1)[1]}'

    return f'{IMAGE_URL.rstrip("/")}/{url.lstrip("/")}' # 중복 슬래시 생기지 않도록 처리


def cleanse_loc(url: Optional[str]) -> str:
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url  # 이미 전체 URL인 경우 그대로 반환

    return f'{SERVICE_URL.rstrip("/")}/{url.lstrip("/")}' # 중복 슬래시 생기지 않도록 처리

def save_xml_string(xml_string, filename):
    """
    Parameters:
    - xml_string: str
    - filename: str
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(xml_string)