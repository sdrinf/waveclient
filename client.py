#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright @ 2009, Waverz.com - BSD license - Information wants to be free!
# Command line tools for the waveclient

import os
import sys
import tempfile
from wirewave import WaveReader
import webbrowser

def viewwave(wid):
	print "rendering "+wid
	w = WaveReader()
	if not w.read(wid):
		print "Wave is not accessible, or not public"
		return
	w.render()
	(h,fn) = tempfile.mkstemp(".html","wave")
	os.write(h,w.renderedHTML.encode("UTF8"))
	os.close(h)
	webbrowser.open_new_tab(fn)
	pass

def showcode(wid):
	w = WaveReader()
	if not w.read(wid):
		print "Wave is not accessible, or not public"
		return
	code = w.get_root_text()
	code = code.replace("\n","\r\n")
	print code
	(h,fn) = tempfile.mkstemp(".txt","wave")
	os.write(h,code.encode("UTF8"))
	os.close(h)
	os.startfile(fn)
	pass

def printhelp():
	print """Usage: client.py [command] [arguments]
Usable wcmd commands:
	      view [waveid]\t-Displays a wave in default browser
	      showtext [waveid]\t-Displays text content only
"""

if (len(sys.argv) < 2):
	printhelp()
	exit()
	pass
if (sys.argv[1] == "--help"):
	printhelp()
elif (sys.argv[1] == "showcode"):
	showcode(sys.argv[2])
elif (sys.argv[1] == "view"):
	viewwave(sys.argv[2])
else:
	print "client: '"+sys.argv[1]+"' is not a valid command. See 'client.py --help'"
