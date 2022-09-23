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
import random
import threading
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")
from gi.repository import Gtk, Gio, Adw, Pango, Gdk, GLib, Vte

from .utils import is_flatpak, get_socket_file, clean_socket


@Gtk.Template(resource_path='/org/igorgue/NeoWaita/window.ui')
class NeowaitaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'NeowaitaWindow'

    pid = -1

    command = ["/bin/env", "nvim", "--listen", get_socket_file()]
    env = []
    default_font = "Iosevka 14"

    terminal = Gtk.Template.Child()
    revealer = Gtk.Template.Child()
    headerbar = Gtk.Template.Child()
    overlay = Gtk.Template.Child()
    new_tab_button = Gtk.Template.Child()

    cancellable = Gio.Cancellable.new()
    pty = Vte.Pty()
    event_controller_motion = Gtk.EventControllerMotion()
    css_provider = Gtk.CssProvider()
    settings = Gtk.Settings.get_default()
    cwd = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # FIXME This hack makes double click work in the vte terminal
        # but it also makes the window titlebar not work and I rather
        # have the titlebar than double click on the terminal
        # maybe try when I'm done with the tab bar and we no longer
        # have a label as the titlebar.
        # self.settings.set_property("gtk-double-click-distance", 0)
        # self.settings.set_property("gtk-double-click-time", 800)

        self.terminal.set_pty(self.pty)
        self.terminal.set_font(Pango.FontDescription.from_string(self.default_font))
        self.terminal.set_size(80, 24)
        self.terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.SYSTEM)
        self.terminal.set_cursor_shape(Vte.CursorShape.BLOCK)
        self.terminal.set_scrollback_lines(-1)
        self.terminal.set_audible_bell(False)
        self.terminal.set_mouse_autohide(True)
        self.terminal.set_rewrap_on_resize(True)
        self.terminal.set_scroll_on_output(True)
        self.terminal.set_scroll_on_keystroke(True)
        self.terminal.set_allow_bold(True)

        self.terminal.connect("window-title-changed", self.on_terminal_window_title_changed)

        if is_flatpak():
            self.command = [
                "/usr/bin/flatpak-spawn",
                "--host",
                "--watch-bus",
                *self.command
            ]

        clean_socket()

        self.event_controller_motion.connect("motion", self.overlay_motioned)

        self.add_controller(self.event_controller_motion)

        self.terminal.set_pty(self.pty)
        self.terminal.set_color_background(Gdk.RGBA())
        self.terminal.set_font(Pango.FontDescription.from_string(self.default_font))

        self.cancellable.connect(self.pty_cancelled)

        self.terminal.spawn_async(
            Vte.PtyFlags.NO_CTTY,
            self.cwd,
            self.command,
            self.env,
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            self.pid,
            self.cancellable,
            self.pty_ready,
            None
        )

        self.new_tab_button.connect("clicked", self.new_tab_clicked)

        style_context = self.get_style_context()
        display = Gdk.Display.get_default()

        style_context.add_provider_for_display(display, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def overlay_motioned(self, _, *cords):
        if cords[1] < 40:
            self.revealer.set_visible(True)
            self.revealer.set_reveal_child(True)
        else:
            GLib.timeout_add(314.16, self.revealer.set_visible, False)
            GLib.timeout_add(314.16, self.revealer.set_reveal_child, False)

    def pty_ready(self, terminal, pid, *_):
        self.pid = pid

        self.terminal = terminal

        self.terminal.watch_child(self.pid)
        self.terminal.connect("child-exited", self.terminal_done)

        self.nvim = pynvim.attach("socket", path=get_socket_file())
        self.cid = self.nvim.channel_id
        self.nvim.ui_attach(self.win_width, self.win_height)

        self.setup_nvim_loop()

        self.connect("notify", self.notified)
        self.terminal.grab_focus()

    def setup_nvim_loop(self):
        notification_types = ["color-scheme"]
        def setup_cb():
            cmd = f"autocmd ColorScheme * call rpcnotify({self.cid}, 'color-scheme')"
            self.nvim.command(cmd)

            self.overide_css_from_colorscheme()

        def request_cb(*args):
            print(f"request_cb: {args}")

            pass

        def notification_cb(name, _):
            if name not in notification_types:
                return

            print(f"[notification_cb] {name}")

            self.overide_css_from_colorscheme()

        def error_cb(msg):
            print(f"[error_cb] {msg}")

        thread = threading.Thread(target=lambda: self.nvim.run_loop(request_cb, notification_cb, setup_cb, error_cb))
        thread.setDaemon(True)
        thread.start()

    def overide_css_from_colorscheme(self):
        self.nvim.command("let g:neowaita_fg1 = synIDattr(synIDtrans(hlID('Normal')), 'fg#')")
        self.nvim.command("let g:neowaita_fg2 = synIDattr(synIDtrans(hlID('PMenu')), 'fg#')")
        self.nvim.command("let g:neowaita_bg1 = synIDattr(synIDtrans(hlID('Normal')), 'bg#')")
        self.nvim.command("let g:neowaita_bg2 = synIDattr(synIDtrans(hlID('CursorLine')), 'bg#')")

        fg1 = self.nvim.vars["neowaita_fg1"]
        fg2 = self.nvim.vars["neowaita_fg2"]
        bg1 = self.nvim.vars["neowaita_bg1"]
        bg2 = self.nvim.vars["neowaita_bg2"]

        self.overide_css(fg1, fg2, bg1, bg2)

    def on_terminal_window_title_changed(self, *args):
        print(f"on_terminal_window_title_changed {args}")

        pass

    def overide_css(self, fg1, fg2, bg1, bg2):
        tpl = f"""
            headerbar {{
              background-image: linear-gradient(180deg, darker({bg2}), transparent 31.41%);
            }}

            headerbar:backdrop windowhandle {{
              filter: none;
              background-color: {bg1};
              background-image: linear-gradient(180deg, darker(darker({bg2})), transparent 31.41%);
            }}

            button {{
              color: {fg2};
            }}

            label {{
              color: {fg1};
            }}

            window {{
              background-color: {bg1};
            }}
        """.strip()

        css = str.encode(tpl)

        self.css_provider.load_from_data(css)


    def pty_cancelled(self, *args):
        print(f"pty_cancelled {args}")

        self.terminal_done()

    def random_color_hex(self):
        return f"#{random.randint(0, 0xffffff):06x}"

    def new_tab_clicked(self, _):
        self.nvim.async_call(lambda: self.nvim.command("tabnew"))

    def terminal_ready(self, *args):
        print(f"on_terminal_window_title_changed {args}")

        pass

    def terminal_done(self, *_):
        self.nvim.async_call(lambda: self.nvim.close())
        self.close()

    def notified(self, _, param):
        if param.name in ["default-width", "default-height", "maximized"]:
            self.resized()

    def resized(self):
        self.nvim.async_call(
            lambda: self.nvim.ui_try_resize(self.win_width, self.win_height)
        )

    # XXX I think there must be a better way to get the win's width and height
    @property
    def win_width(self):
        w = self.get_allocated_width()

        return w if w > 0 else self.props.default_width

    @property
    def win_height(self):
        h = self.get_allocated_height()

        return h if h > 0 else self.props.default_height
