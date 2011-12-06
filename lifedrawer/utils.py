'''
Utils
'''
from lifedrawer import config

def getEnglishDateSuffix(date):
	'''
	http://stackoverflow.com/questions/739241/python-date-ordinal-output
	'''
	day = date.day
	
	if 4 <= day <= 20 or 24 <= day <= 30:
		return "th"
	else:
		return ["st", "nd", "rd"][day % 10 - 1]

def debug(*args):
	if config.debug:
		for arg in args:
			print arg
