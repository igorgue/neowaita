from os import remove
from os.path import exists, expanduser, join

def is_flatpak() -> bool:
    return exists("/.flatpak-info")

def get_socket_file() -> str:
    return _get_socket_file()

def _get_socket_file() -> str:
    return join(_get_home(), "neowaita.socket")

def clean_socket() -> None:
    socket_file = _get_socket_file()

    if exists(socket_file):
        remove(socket_file)

def _get_home() -> str:
    # FIXME on flatpak this returns an empty string
    return expanduser("~")
