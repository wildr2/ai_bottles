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