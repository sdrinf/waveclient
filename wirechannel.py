#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright @ 2009, Waverz.com - BSD license - Information wants to be free!

# direct wave wire channel implementation:
# reads the public stream

import random
from wireutils import webrequest
from waveapi import simplejson

def refresh_search():
    session = "503282974482375274562"
    cookie = "DQAAAI8AAADqGuAdyCS0oaSk8PE4FDZZUl_KCmr0Gj6AVICpeE9WScTxIjM5CJLrNI23neGAQtXEDs51NkaLaxoik-IRUyLxwpzwa5Q3sUeRJ9Xo1Zh-6bpZlckaS242zuacV_Fk7qLULp2JRf1I5YbFalpolOU2_BzyBenDi9pf_22hhBJWQwXWm9c4YYQOlynF2fLI08Q"
    rid = random.randint(0, 100000)
    zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
    resdat = webrequest("POST", "wave.google.com", 
                        "/wave/wfe/channel?VER=6&RID="+str(rid)+
                        "&CVER=3&zx="+zx+"&t=1",
                        {'Cookie': "WAVE="+cookie},
                        {"count" : "0"} )
    print resdat


def refresh_searchpublic():
    session = "503282974482375274562"
    cookie = "DQAAAI8AAADqGuAdyCS0oaSk8PE4FDZZUl_KCmr0Gj6AVICpeE9WScTxIjM5CJLrNI23neGAQtXEDs51NkaLaxoik-IRUyLxwpzwa5Q3sUeRJ9Xo1Zh-6bpZlckaS242zuacV_Fk7qLULp2JRf1I5YbFalpolOU2_BzyBenDi9pf_22hhBJWQwXWm9c4YYQOlynF2fLI08Q"
    rid = random.randint(0, 100000)
    zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
    resdat = webrequest("POST", "wave.google.com", 
                        "/wave/wfe/channel?VER=6&RID="+str(rid)+
                        "&CVER=3&zx="+zx+"&t=1",
                        {'Cookie': "WAVE="+cookie},
                        {"count" : "2",
                         "req0_key" : '{"a":"RY3Rrawn","r":"e","t":2007,"p":{"1000":[0,0],"2":"RY3Rrawn0"}}',
                         "req1_key" : '{"a":"RY3Rrawn","r":"f","t":2602,"p":{"1000":[0,0],"2":"RY3Rrawn2","3":"","4":{"2":25,"1":0},"6":"public@a.gwave.com"}}'} )
    print resdat
    wiredata = "".join( resdat.split("\n")[1:])
    csid = wiredata[10:26]
    print "sid: "+csid
    zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
    resdat = webrequest("GET", "wave.google.com", 
                        "/wave/wfe/channel?VER=6&RID=rpc&SID="+csid+
                        "&CI=0&AID=99&TYPE=xmlhttp&zx="+zx+"&t=1",
                        {'Cookie': "WAVE="+cookie},
                        None)
    print resdat
    pass

print refresh_search()
