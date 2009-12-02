#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright @ 2009, Waverz.com - BSD license - Information wants to be free!

# direct wave wire channel implementation:
# reads the public stream

import random
from wireutils import webrequest
from waveapi import simplejson

class WaveChannel():
    """Wave channel reader"""
    session = "503282974482375274562"
    # point of interest: cookie should contain both WAVE, and wave-dollhouse
    cookie = "WAVE=DQAAAI4AAAAqzyhQfVz06gWu2rprdEoyTTkHawFHr7xg82OU1Pqy9wHVJWsK7WxOC3wYkKVdFzHLboFucnbVdP3ANr-xdaqm4SYzchZi8ASF36Ns4NYPa7GNwnRasvL0fe8O_YifmLQ28TI3CZDJMVn5EXNAu0VoaC9ZgNHTCeCgTbd-3xxU5DaFFwDtK4jC5kkJ1hbtLlg;S=wave-dollhouse=tetTwcpcgLAMT5f9aKFJag;"
    crid = random.randint(0, 100000)
    
    
    def parse_response(self, r):
        """returns a native python object from the JSON mess spit by wave"""
        data = ("".join(r.split("\n")[1:])).replace(",]","]")
        obj = simplejson.loads(data)
        return obj
        
    def test_signal(self, data = "MODE=init"):
        """sends a test request"""
        zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
        resdat = webrequest("GET", "wave.google.com",
                            "/wave/wfe/test?VER=6&"+data+"&zx="+zx+"&t=1",
                            {'Cookie': self.cookie},
                            None )
        return resdat
        
    def get_sid(self):
        """returns a wave-usable SID"""
        self.crid += 1
        zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
        resdat = webrequest("POST", "wave.google.com", 
                            "/wave/wfe/channel?VER=6&RID="+str(self.crid)+
                            "&CVER=3&zx="+zx+"&t=1",
                            {'Cookie': self.cookie},
                            {"count" : "0"} )
        print resdat
        resdat = self.parse_response(resdat)
        if (resdat[0][1][0] != "c"):
            return None
        sid = resdat[0][1][1]
        return sid
        
    def search(self, sid, group):
        """returns search result for all group messages"""
        self.crid += 1
        zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
        resdat = webrequest("POST", "wave.google.com", 
                            "/wave/wfe/channel?VER=6&"+
                            "SID="+sid+"&RID="+str(self.crid)+
                            "&zx="+zx+"&t=1",
                            {'Cookie': self.cookie},
                            {"count" : "2",
                             "req0_key" : '{"a":"kA-_jfrF","r":"0","t":2007,"p":{"1000":[0,0],"2":"kA-_jfrF0"}}',
                             "req1_key" : '{"a":"kA-_jfrF","r":"1","t":2602,"p":{"1000":[0,0],"2":"kA-_jfrF2","3":"","4":{"2":25,"1":0},"6":"public@a.gwave.com"}}'} )
        print resdat
        pass
    
        
    def process_stream(self, sid, f):
        """process an incoming stream referenced from SID; calls back f(data)"""
        zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
        import httplib
        connection = httplib.HTTPSConnection("wave.google.com")
        connection.request("GET", "/wave/wfe/channel?VER=6&RID=rpc&SID="+sid+
                           "&CI=0&AID=0&TYPE=xmlhttp&zx="+zx+"&t=1", None, 
                           {'Cookie': self.cookie, 
                            'User-Agent' : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/4.0.249.11 Safari/525.13"}
                           )
        http_response = connection.getresponse() 
        http_data = http_response.read(120)
        print http_data
        exit()
        connection.close()
        
    def retrieve(self, sid):
        """fetch the currently seeked result"""
        zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
        resdat = webrequest("GET", "wave.google.com", 
                            "/wave/wfe/channel?VER=6&RID=rpc&SID="+sid+
                            "&CI=0&AID=0&TYPE=xmlhttp&zx="+zx+"&t=1",
                            {'Cookie': self.cookie},
                            None)
        file("./tempdata","w+").write(resdat)
        print resdat

        
        
    def __init__(self):
        pass
    
#t = webrequest("GET", "wave.google.com",
#               "/wave/wfe/channel?VER=6&RID=rpc&SID=3E8CF847DD1CE8A6&CI=0&AID=0&TYPE=xmlhttp&zx=u5kkqba3qj1z&t=1",
#               {'Cookie': "WAVE=DQAAAI4AAADv5UPduZqKEiF4eInHebThSZJE3P0iX6NDWL4NFMvbuY5Jcw6cYLzivgmSfTp921fdgI5Yj2-OIRYSceu8lHrgPh553raYIJ_F82UulGKm2yazA2syXNoIia0M1goqBnGBKub7Bmd5CKgIvVMLJ5edE5On-8dABj3m6DDcZtxYTX141VlBhvO4gCcJSGxX2VQ; S=wave-dollhouse=jsl7loIsv6FVZ0tEEETcIQ"},
#               None)
#print t
#exit()

w = WaveChannel()
#print w.test_signal("MODE=init")
#print w.test_signal("TYPE=xmlhttp")
sid = w.get_sid()
print "sid: "+sid
print w.search(sid,"public@a.gwave.com")
print w.process_stream(sid, None)
exit()

print w.retrieve(sid)
exit()
