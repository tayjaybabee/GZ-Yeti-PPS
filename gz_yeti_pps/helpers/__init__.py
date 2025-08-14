import requests
from typing import Union
from ..common.constants import TRUE_VALUES, FALSE_VALUES, DEFAULT_API_STUB as DEFAULT_STUB


def parse_truthy_value(value: Union[bool, int, str]) -> Union[0, 1]:
    if isinstance(value, str):
        value = value.lower()

    if isinstance(value, float):
        value = int(value)

    if value in TRUE_VALUES:
        return 1
    elif value in FALSE_VALUES:
        return 0

    raise ValueError(f"Value {value} is not a valid truthy value!")


def attempt_connection(url: str = None, raise_on_fail: bool = False, timeout=5) -> bool:
    """
    Attempts to connect to the given URL.
    """
    if not url:
        url = DEFAULT_STUB
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if raise_on_fail:
            raise ConnectionError(f"Failed to connect to {url}: {e}") from e
        return False
