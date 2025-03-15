import sys
import os
import time
import textwrap

def get_spinner():
	interval = 0.1
	chrs = "|/-\\"
	i = int(time.time() / interval) % len(chrs)
	return chrs[i]

def wraptext(text, width):
	wrapped = ""
	lines = text.splitlines(keepends=True)
	for line in lines:
		if line:
			clean_line = line.rstrip()
			linebreak = line[len(clean_line):]
			wrapped += textwrap.fill(clean_line, width, break_long_words=False, replace_whitespace=False)
			wrapped += linebreak

	return wrapped

def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)