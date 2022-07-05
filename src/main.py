# main.py
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

import sys
import gi
import pynvim

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw

gi.require_version('Vte', '3.91')

from gi.repository import Vte

from .window import NvimPythonUiWindow, AboutDialog


class Nvim_python_uiApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='org.igorgue.NvimPythonUI',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.quit, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = NvimPythonUiWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = AboutDialog(self.props.active_window)
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

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
    assert version

    app = Nvim_python_uiApplication()

    return app.run(sys.argv)


# tmp_dir = f"{os.environ.get('XDG_RUNTIME_DIR')}/app/{os.environ.get('FLATPAK_ID')}"
# socket_file = f"{tmp_dir}/nvim-ui"
# socket_host = "127.0.0.1:6666"
# ld_library_path = f"{os.environ.get('LD_LIBRARY_PATH')}:/run/host/usr/lib:/run/host/usr/lib/x86_64-linux-gnu"

# env = dict(os.environ, **{
#     "NVIM_LISTEN_ADDRESS": socket_file,
#     "PATH": f"{os.environ.get('PATH')}:/run/host/usr/bin",
#     "LD_LIBRARY_PATH": ld_library_path
# })

# print(env)

# process = subprocess.Popen([f"nvim", "--headless --embed --listen {socket_host}"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# (pid, stdin, stdout, stderr) = GLib.spawn_async(
#     ["/run/host/usr/bin/nvim", "--listen", f"{socket_host}"],
#     envp=['{}={}'.format(k, v) for k, v in env.items()],
#     standard_input=True,
#     standard_output=True,
#     standard_error=True
# )

# import time
# time.sleep(3)
# print(nvim)
# print(socket_file)

# editor = pynvim.attach("tcp", address="127.0.0.1", port=6666)
# editor = pynvim.attach('child', argv=["/run/host/usr/bin/env", "nvim", "--embed"])

# buffer = editor.current.buffer # Get the current buffer
# buffer[0] = 'replace first line'
# buffer[:] = ['replace whole buffer']
# editor.command('vsplit')
# editor.windows[1].width = 10
