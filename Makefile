DEFAULT_GOAL := run

run:
	meson . build --prefix=$(HOME)/.var/app/org.igorgue.NvimPythonUI
	cd build && ninja install
	$(HOME)/.var/app/org.igorgue.NvimPythonUI/bin/nvim-python-ui
