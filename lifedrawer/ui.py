'''
LifeDrawer UI for GTK
'''

from gi.repository import Gtk, Pango, GObject
import datetime, threading
from lifedrawer import utils, backend

class MainWindow(object):
	html_table = {
		"b" : "bold",
		"u" : "underline",
		"blockquote" : "blockquote",
		"i" : "italic"
	}
	
	def __init__(self):
		self.t = None
		self.date = datetime.date.today()
		
		self.builder = Gtk.Builder()
		self.uifile = "lifedrawer/main-window.ui"
		self.builder.add_from_file(self.uifile)
		self.window = self.builder.get_object ("MainWindow")
		self.window.connect ("destroy", Gtk.main_quit)

		self.title = self.builder.get_object("dateLabel")
		self.title.set_use_markup(True)
		
		self.calendar = self.builder.get_object("calendar")
		self.calendar.select_month(self.date.month - 1, self.date.year)
		self.calendar.select_day(self.date.day)
		self.calendar.connect("day_selected", self.date_selected)

		self.textBuffer = Gtk.TextBuffer()

		self.editor = self.builder.get_object("textview")
		self.editor.set_buffer(self.textBuffer)
		self.editor.connect_after('move-cursor', self.updateToggles)
		self.editor.connect('button-release-event', self.updateToggles)
		self.textBuffer.connect_after('insert-text', self.updateToggles)
		self.editor.connect_after('backspace', self.updateToggles)

		' Now we add all of the buttons '
		self.toolbar = self.builder.get_object("editBar")
		
		self.textBuffer.create_tag("bold", weight=Pango.Weight.BOLD)
		self.boldButton = Gtk.ToggleToolButton()
		self.boldButton.set_icon_name(Gtk.STOCK_BOLD)
		self.boldButton.set_label("Bold")
		self.boldButton.connect("toggled", self.setTag, "bold")
		self.toolbar.insert(self.boldButton, 0)

		self.textBuffer.create_tag("italic", style=Pango.Style.ITALIC)
		self.italicButton = Gtk.ToggleToolButton()
		self.italicButton.set_icon_name(Gtk.STOCK_ITALIC)
		self.italicButton.set_label("Italic")
		self.italicButton.connect("toggled", self.setTag, "italic")
		self.toolbar.insert(self.italicButton, 1)

		self.textBuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
		self.underlineButton = Gtk.ToggleToolButton()
		self.underlineButton.set_icon_name(Gtk.STOCK_UNDERLINE)
		self.underlineButton.set_label("Underline")
		self.underlineButton.connect("toggled", self.setTag, "underline")
		self.toolbar.insert(self.underlineButton, 2)

		self.textBuffer.create_tag("blockquote", left_margin=10, pixels_above_lines=10, pixels_below_lines=10)
		self.quoteButton = Gtk.ToggleToolButton()
		self.quoteButton.set_icon_name("document-revert")
		self.quoteButton.set_label("Quote")
		self.quoteButton.connect("toggled", self.setTag, "blockquote")
		self.toolbar.insert(self.quoteButton, 3)
		
		self.updateDate()		
	
		self.window.show_all()

		self.loadContent()

	def date_selected(self, widget):
		(year, month, day) = widget.get_date()
		self.saveContent()
		self.date = self.date.replace(year, month + 1, day)
		self.updateDate()
		self.loadContent()
	
	def saveContent(self):
		if self.t is not None:
			GObject.source_remove(self.t)
		# We save 1second after we stop typing to reduce Disk IO
		self.t = GObject.timeout_add(1000 * 1, self.real_saveContent)

	def real_saveContent(self):
		' define stuff and then convert to bare HTML '
		tags = []
		utils.debug("Saving content....")
		
		for (html, tag) in self.html_table.iteritems():
			tags.append( ( self.textBuffer.get_tag_table().lookup(tag), html ) )
		
		content = ''
		end = self.textBuffer.get_end_iter().get_offset()
		for i in range(0, end):
			it = self.textBuffer.get_iter_at_offset(i)

			for (tag, html) in tags:
				if it.begins_tag(tag):
					content += '<%s>' % html
				elif it.ends_tag(tag):
					content += '</%s>' % html
			
			content += it.get_char()
		
		backend.save_content(self.date, content)

	def loadContent(self):
		(content, tags) = backend.get_content(self.date)
		if content != None:
			self.textBuffer.set_text(content)
			for tag in tags:
				s = self.textBuffer.get_iter_at_offset(tag['starts'])
				e = self.textBuffer.get_iter_at_offset(tag['ends'])
				self.textBuffer.apply_tag_by_name(self.html_table[tag['name']], s, e)
		else:
			self.textBuffer.set_text('')

	def updateDate(self):
		self.title.set_label("<span font='40.5'>%s<sup>%s</sup></span>\n%s" % ( self.date.day, utils.getEnglishDateSuffix(self.date), '%s %s' % (self.date.strftime('%B'), self.date.year) ))

	def updateToggles(self, widget=None, event=None, tmpVar=None, tmpVar2=None, beginWord=None, endWord=None):
		curIter = self.textBuffer.get_iter_at_mark(self.textBuffer.get_insert())
		curIter.backward_char()
		curTags = curIter.get_tags()
		bag = []
		for tag in curTags:
			bag.append( tag.get_property("name") )
		
		self.boldButton.set_active("bold" in bag)
		self.italicButton.set_active("italic" in bag)
		self.underlineButton.set_active("underline" in bag)
		self.quoteButton.set_active("quote" in bag)
		self.saveContent()

	def setTag(self, widget, data=None):
		'''
		Set a tag. For buttons
		'''
		if widget.get_active():
			if self.textBuffer.get_selection_bounds() != ():
				start, end = self.textBuffer.get_selection_bounds()
				self.textBuffer.apply_tag_by_name(data, start, end)
		else:
			if self.textBuffer.get_selection_bounds() != ():
				start,end = self.textBuffer.get_selection_bounds()
				self.textBuffer.remove_tag_by_name(data, start, end)

def start():
	MainWindow()
	Gtk.main()
