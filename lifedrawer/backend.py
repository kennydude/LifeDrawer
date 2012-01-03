'''
Backend >:]
'''
import os, os.path
from lifedrawer import utils, config
import xml.parsers.expat

def get_attachment_path(date):
	return os.path.join(config.drawer, str(date.year), str(date.month))

def get_filename(date):
	return os.path.join(config.drawer, str(date.year), str(date.month), str(date.day) + ".html")

class DocParser(object):
	'''
		Parses HTML doc
	'''
	content = ''
	tags = []
	i = 0
	cur_tag = {}
	bag = ['b', 'u', 'i', 'blockquote']

	def start_element(self, name, attrs):
		if name in self.bag:
			self.cur_tag = {
				"name" : name,
				"starts" : self.i
			}
		elif name == "img":
			print "Reading tag"
			self.tags.append({
				"name" : "img",
				"src" : attrs['src'],
				"starts" : self.i
			})
	def end_element(self, name):
		if name in self.bag:
			self.cur_tag['ends'] = self.i
			self.tags.append(self.cur_tag)
	def char_data(self, data):
		self.content += data
		self.i += len(data)

	def parse(self, filename):		
		p = xml.parsers.expat.ParserCreate()
		
		p.StartElementHandler = self.start_element
		p.EndElementHandler = self.end_element
		p.CharacterDataHandler = self.char_data
		
		p.Parse(open(filename, 'r').read())

def get_content(date):
	filename = get_filename(date)
	if os.path.exists(filename):
		d = DocParser()
		d.parse(filename)
		
		return (d.content, d.tags)
	return (None, None)

def save_content(date, data):
	if data == '':
		return
	d = os.path.dirname(get_filename(date))
	if not os.path.exists(d):
		os.makedirs(d)
	f = open(get_filename(date), 'w')
	f.write( '<content>%s</content>' % data )
	f.close()
