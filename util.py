import time

def get_spinner():
	interval = 0.1
	chrs = "|/-\\"
	i = int(time.time() / interval) % len(chrs)
	return chrs[i]