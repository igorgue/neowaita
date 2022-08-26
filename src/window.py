# window.py
#
# Copyright 2022 Igor Guerrero
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
import pynvim

from gi.repository import Gtk, Pango, Gdk, GLib, Vte, Gdk


@Gtk.Template(resource_path='/org/igorgue/NvimPythonUI/window.ui')
class NvimPythonUiWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NvimPythonUiWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.set_child(box)

        # self.nvim = pynvim.attach('child', argv=["/bin/env", "nvim", "--embed", "/home/igor/Code/liviano/Makefile"])

        self.terminal = Vte.Terminal()
        self.pty = Vte.Pty.new_sync(Vte.PtyFlags.DEFAULT)
        self.terminal.set_pty(self.pty)

        self.terminal.set_color_background(Gdk.RGBA())
        self.terminal.set_font(Pango.FontDescription.from_string('Iosevka 14'))
        self.terminal.set_rewrap_on_resize(True)

        self.pty.spawn_async(
            None,
            ["/bin/env", "nvim", "--listen", "/tmp/nvim-python-ui.socket"],
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            self.ready
        )

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_child(self.terminal)

        box.append(scrolled)

        # self.nvim.ui_attach(width, height)
    def ready(self, pty, task):
        self.nvim = pynvim.attach('socket', path='/tmp/nvim-python-ui.socket')

        self.nvim.ui_try_resize(self.get_allocated_width(), self.get_allocated_height())
        self.nvim.command("vsp")


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = 'nvim-python-ui'
        self.props.version = "0.1.0"
        self.props.authors = ['Igor Guerrero']
        self.props.copyright = '2022 Igor Guerrero'
        self.props.logo_icon_name = 'org.igorgue.NvimPythonUI'
        self.props.modal = True
        self.set_transient_for(parent)
