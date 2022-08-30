from os import remove
from os.path import exists, expanduser, join
from typing import Optional
from uuid import uuid4

socket_uuid: Optional[str] = None


def is_flatpak() -> bool:
    return exists("/.flatpak-info")

def get_socket_file() -> str:
    return _get_socket_file()

def _get_socket_file() -> str:
    return join(_get_home(), f"neowaita-{_get_uuid()}.socket")

def _get_uuid() -> str:
    global socket_uuid

    if socket_uuid is not None:
        return socket_uuid

    socket_uuid = str(uuid4())

    return socket_uuid
_ = _get_uuid()

def clean_socket() -> None:
    socket_file = _get_socket_file()

    if exists(socket_file):
        remove(socket_file)

def _get_home() -> str:
    # FIXME on flatpak this returns an empty string
    return expanduser("~")
