"""the main entry for all waverz sites"""

import os
import sys
import datetime
import wsgiref.handlers 
from operator import itemgetter
import logging

# google toolset
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

class SplashPage(webapp.RequestHandler):
    def get(self,*args):
        """default get"""
        from wirechannel import WaveChannel
        w = WaveChannel()
        sid = w.get_sid()
        logging.info("sid: "+sid)
        logging.info(w.search(sid,"public@a.gwave.com"))
        logging.info(w.process_stream(sid, None))
        return
    

def main():
    """main entry point for all requests"""
    capp = webapp.WSGIApplication([
        ('/', SplashPage)
        ], debug = True)
    wsgiref.handlers.CGIHandler().run(capp)
    pass

if __name__ == '__main__':
    main()
