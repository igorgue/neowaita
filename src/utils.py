import os
import stat

from os import path
from typing import Optional

socket_file: Optional[str] = None


def is_flatpak() -> bool:
    return path.exists("/.flatpak-info")

def get_socket_file() -> str:
    return _get_socket_file()

def clean_socket() -> None:
    socket_file = _get_socket_file()

    if path.exists(socket_file):
        os.remove(socket_file)

def _get_socket_file(n: int = 0) -> str:
    global socket_file

    if socket_file is not None:
        return socket_file

    home = _get_home()

    sufix = "" if n == 0 else f"-{n}"
    socket_file = path.join(home, f"neowaita{sufix}.socket")

    if path.exists(socket_file) and not stat.S_ISFIFO(os.stat(socket_file).st_mode):
        print("in use")
        n += 1

        socket_file = None
        return _get_socket_file(n + 1)
    else:
        print("not in use")
        return socket_file

def _get_home() -> str:
    return path.expanduser("~")

LICENSE = """© 2022 Igor Guerrero

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Except as contained in this notice, the name(s) of the above copyright
holders shall not be used in advertising or otherwise to promote the sale,
use or other dealings in this Software without prior written
authorization."""
