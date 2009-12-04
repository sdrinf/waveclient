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
    cookie = "WAVE=DQAAAI4AAAClmviXI_qcmfKrOFRlzavG3F3F1ViC2poDibS2GJ-da7aplbNOAboGSinNKVWEvNg0KWYhlID6hIJcPqwewG07BHF31hJnnWiTw4fa-40z1lCG9di1lvt4xh6YKT4WjSw5-7R55gJY7o2NjeQ0w5N4YJ6FFqPYInFAXqZwcMFETNFcws71_iOGFmgR1cwFZII;S=wave-dollhouse=XJrhIyRTydCq41uejLibIw;"
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
        a = "".join([chr(random.randint(97,122)) for i in xrange(0, 8)])
        resdat = webrequest("POST", "wave.google.com", 
                            "/wave/wfe/channel?VER=6&"+
                            "SID="+sid+"&RID="+str(self.crid)+
                            "&zx="+zx+"&t=1",
                            {'Cookie': self.cookie},
                            {"count" : "2",
                             "req0_key" : '{"a":"'+a+'","r":"0","t":2007,"p":{"1000":[0,0],"2":"'+a+'0"}}',
                             "req1_key" : '{"a":"'+a+'","r":"1","t":2602,"p":{"1000":[0,0],"2":"'+a+'2","3":"","4":{"2":15,"1":0},"6":"public@a.gwave.com"}}'} )
        print resdat
        pass
    
        
    def process_readline(self, response):
        """reads a line from given socket"""
        res = ""
        r = ""
        while r != "\n":
            r = response.read(1)
            res += r
        return res
    
    def process_stream(self, sid, f):
        """process an incoming stream referenced from SID; calls back f(data)"""
        zx = "".join([chr(random.randint(97,122)) for i in xrange(0, 11)])
        import httplib
        connection = httplib.HTTPSConnection("wave.google.com")
        # connection.set_debuglevel(1)
        connection.request("GET", "/wave/wfe/channel?VER=6&RID=rpc&SID="+sid+
                           "&CI=0&AID=0&TYPE=xmlhttp&zx="+zx+"&t=1", None, 
                           {'Cookie': self.cookie, 
                            'User-Agent' : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/4.0.249.11 Safari/525.13",
                            # "transfer-encoding" : "chunked"
                            }
                           )
        http_response = connection.getresponse() 
        while (True):
            l = self.process_readline(http_response).strip() # first line is always packet length
            print "new packet length: "+str(l)
            plen = int(l)
            cpacket = ""
            while (len(cpacket) < plen):
                cpacket += self.process_readline(http_response)
                #print "BReading: "+cpacket+" - size: "+str(len(cpacket))
            #print "finished BR"
            while (True):
                # print http_response.fp.tell()
                try:
                    cobj = simplejson.loads(cpacket)
                    break # packet is finished, and readable
                except simplejson.decoder.JSONDecodeError, e:
                    # there is probably more to it
                    cline = self.process_readline(http_response).strip()
                    # print "+reading: "+str(cline)
                    cpacket += cline
                    continue
            self.process_single_packet(cobj)
        # print http_data
        exit()
        connection.close()
        
    def dump_object(self, obj, tab = 0, key = None):
        res = "\t".join(["" for i in xrange(0,tab)])+(key+" => " if key != None else "")
        if (isinstance(obj, list)):
            res += "list ("+str(len(obj))+"):\n"
            for o in obj:
                res += self.dump_object(o,tab+1)
        elif (isinstance(obj, dict)):
            res += "dict:\n"
            for k,v in obj.iteritems():
                res += self.dump_object(v,tab+1,k)
        elif (isinstance(obj, bool)) | (isinstance(obj,int)):
            res += str(obj)+"\n"
        elif (isinstance(obj, unicode)) :
            res += obj.encode("ASCII","ignore")+"\n"
        else:
            res += unicode(obj,"UTF-8","ignore")+"\n"
        return res
    
    def process_single_packet(self, obj):
        file("./stream.txt","a+").write(str(obj)+"\n")
        for packs in obj:
            pid, pcont = packs
            if (pcont[0] != 'wfe'):
                continue
            innerobj = simplejson.loads(pcont[1])
            file("./streamb.txt","a+").write(str(innerobj)+"\n")
            file("./streamc.txt","a+").write("----------------------------\n")
            file("./streamc.txt","a+").write(self.dump_object(innerobj))
            if isinstance(innerobj["p"]["1"],list):
                for w in innerobj["p"]["1"]:
                    ctitle = w["9"]["1"].encode("ASCII","ignore")
                    content = w["10"][0]["1"].encode("ASCII","ignore")
                    waveid = w["1"].encode("ASCII","ignore")
                    print waveid+" : " + ctitle + " "+content[0:10]
        return
    
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
    
    
if (__name__ == "__main__"):
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
