#!/usr/bin/python
'''
LifeDrawer

by @kennydude
'''

from lifedrawer import ui

try:
	ui.start()
except KeyboardInterrupt:
	from gi.repository import Gtk
	Gtk.main_quit
