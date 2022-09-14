# main.py
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

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Adw, Gio, GObject, Vte

from .window import NeowaitaWindow
from .utils import LICENSE, clean_socket

GObject.type_register(Vte.Terminal)

class NeowaitaApplication(Adw.Application):
    """The main application singleton class."""

    win: NeowaitaWindow

    def __init__(self):
        super().__init__(application_id="org.igorgue.NeoWaita",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.create_action("quit", self.quit, ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window

        if not self.win:
            self.win = NeowaitaWindow(application=self)

        self.win.present()


    def do_shutdown(self):
        quit(self.win)

    def quit(self, widget, _):
        self.win.nvim.ui_detach()

        # TODO Figure out closing errors on neovim

        clean_socket()

        Adw.Application.do_shutdown(self)

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.win,
                                application_name="neowaita",
                                application_icon="org.igorgue.NeoWaita",
                                developer_name="Igor Guerrero",
                                version="0.1.0",
                                developers=["Igor Guerrero - igorgue@protonmail.com"],
                                copyright=LICENSE)
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print("app.preferences action activated")

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    return NeowaitaApplication().run(sys.argv)
