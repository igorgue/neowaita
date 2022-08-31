# window.py
#
# Copyright 2022 Igor
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written
# authorization.
#
# SPDX-License-Identifier: MIT
import pynvim

from gi.repository import Gtk, Gio, Adw, Pango, Gdk, GLib, Vte

from .utils import is_flatpak, get_socket_file, clean_socket


@Gtk.Template(resource_path='/org/igorgue/NeoWaita/window.ui')
class NeowaitaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'NeowaitaWindow'

    pid = -1
    pty = Vte.Pty.new_sync(Vte.PtyFlags.NO_CTTY)

    command = ["/bin/env", "nvim", "--listen", get_socket_file()]
    default_font = "Iosevka 14"

    terminal = Gtk.Template.Child()
    terminal_box = Gtk.Template.Child()

    cancellable = Gio.Cancellable.new()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        assert self.terminal
        assert self.terminal_box

        self.terminal.set_pty(self.pty)
        self.terminal.set_color_background(Gdk.RGBA())
        self.terminal.set_font(Pango.FontDescription.from_string(self.default_font))

        self.cancellable.connect(self.pty_cancelled)

        if is_flatpak():
            self.command = [
                "/usr/bin/flatpak-spawn",
                "--host",
                "--watch-bus",
                *self.command
            ]

        clean_socket()

        self.pty.spawn_async(
            None,
            self.command,
            None,
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            -1,
            self.cancellable,
            self.pty_ready
        )


    def pty_ready(self, pty, task):
        _, self.pid = pty.spawn_finish(task)

        self.terminal.watch_child(self.pid)
        self.terminal.connect("child-exited", self.terminal_done)

        self.nvim = pynvim.attach("socket", path=get_socket_file())
        self.nvim.ui_attach(self.box_width, self.box_height)

        self.connect("notify", self.notified)
        self.terminal.grab_focus()

    def pty_cancelled(self, pty):
        # TODO pty cancelled... TODO reconnection or error page")
        pass

    def terminal_done(self, terminal, error):
        self.nvim.close()
        self.close()

    def notified(self, app, param):
        if param.name in ["default-width", "default-height", "maximized"]:
            self.resized()

    def resized(self):
        self.nvim.ui_try_resize(self.box_width, self.box_height)

    # XXX I think there must be a better way to get the box's width
    @property
    def box_width(self):
        w = self.terminal_box.get_allocated_width()

        return w if w > 0 else self.props.default_width

    @property
    def box_height(self):
        h = self.terminal_box.get_allocated_height()

        return h if h > 0 else self.props.default_height

