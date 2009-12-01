# direct wave wire reader implementation

"""Load wave data directly from wire"""

import datetime

from waveapi import simplejson
import logging
import urllib
import datetime 
from math import floor

def human_readable_quantity(n):
    """returns '1.2M' representation of a number"""
    n = int(n)
    cnum = 1000 * 1000 * 1000
    ctags = ["G","M","K"]
    for i in xrange(0,len(ctags)):
        if (n >= cnum):
            ckn = float(n) / cnum
            return (str(int(floor(ckn))) +"."+str((ckn - floor(ckn))*10)[0]  + ctags[i])
        cnum = cnum / 1000
    return str(n)


def human_readable_timediff(ctime):
    if (ctime == None):
        return ""
    td = datetime.datetime.now() - ctime
    lm = ""
    if (td.days > 0):
        ch = (td.seconds / 3600)
        lm = str(td.days)+" day" + ("s" if (td.days > 1) else "")
        if (ch > 0):
            lm += " " +str(ch)+" hour" + ("s" if (ch > 1) else "")
    elif (td.seconds > 3600):
        ch = (td.seconds / 3600)
        lm = str(ch)+" hour" + ("s" if (ch > 1) else "")
    elif (td.seconds > 60):
        cm = (td.seconds / 60)
        lm = str(cm)+" min" + ("s" if (cm > 1) else "")
    else:
        return "just now"
    return lm+" ago"


class DefaultWaveRenderer():
    """Pre-formats wave content"""

    def render_blip_header(self, data):
	"""render blip's header info"""
	fr = ""
	fr = '<div style="background-color:lightgray;padding-left:60px">'
	fr += '<div style="float:left">';
	fr += '<a name="#'+data["id"]+'">&nbsp;</a>'
	fr += '<b>Last modified:</b> '+str(data["last_modified"])+" ("+human_readable_timediff(data["last_modified"])+") <br />"
	fr += "<a href=\"#"+data["id"]+"\" onclick=\"javascript:switch_div('p_"+data["id"]+"');\">"
	fr += '<b>Contributors ('+str(len(data["contributors"]))+'):</b></a> '+", ".join(data["contributors"][0:2])+'<br />'
	fr += '</div>'
	for c in data["contributors"][0:2]:
	    if (c.endswith("@googlewave.com")):
		r = c.split("@")
		fr += '<img src="http://archive.waverz.com/avatar/'+r[0]+'" style="border:0px; width:40px" />'
	if (len(data["contributors"]) > 2):
	    fr += "<div style=\"float:left; background-color:lightgray;\">"
	    fr += '<div id="p_'+data["id"]+'" style="display:none">'
	    fr += ", ".join(data["contributors"][2:])
	    
	    for c in data["contributors"][2:]:
		if (c.endswith("@googlewave.com")):
		    r = c.split("@")
		    fr += '<img src="http://archive.waverz.com/avatar/'+r[0]+'" style="border:0px; width:40px" />'
	    fr += '</div><div style="clear:both"></div> </div>'
	fr += '</div>'
	return fr
    
    def render_attachment(self, data, cid):
	"""Renders a wave attachment"""
	res = []
	if not "attachment_url" in data:
	    return ""
	if not "filename" in data:
	    data["filename"] = "unnamed file"
	res.append('<br /><div style="display: block; border:1px solid black; padding:8px" id="'+cid+'">')
	res.append('<a href="https://wave.googleusercontent.com/wave'+data["attachment_url"]+'">')
	if ("thumbnail_url" in data):
	    res.append('<img src="https://wave.googleusercontent.com/wave'+data["thumbnail_url"]+'" alt="Download" />')
	else:
	    res.append("Download")
	res.append("</a><br />")
	res.append('<b>File Attachment:</b> '+data["filename"]+'<br />')
	res.append('<b>Creator:</b> '+data["creator"]+"<br />")
	res.append('<b>Size:</b> '+human_readable_quantity(data["attachment_size"])+"B<br/>")
	res.append("</div>")
	return "".join(res)

    def render_wave(self, wavelet_meta, innerhtml):
	"""Renders the main wave frame"""
	res = "<h1>" + wavelet_meta["title"] + "</h1>"
	res += """
	<script language="javascript">function switch_div(id) { document.getElementById(id).style.display = ((document.getElementById(id).style.display == "none")?("inline"):("none")); }</script>
	"""
	res += '<b>Last modified:</b> '+human_readable_timediff(wavelet_meta["last_modified"])+"<br />"
	ps = wavelet_meta["participants"][:min(3,len(wavelet_meta["participants"]))]
	logging.info(ps)
	res += '<b>Participants ('+str(len(wavelet_meta["participants"]))
	res += '):</b> '+unicode(", ".join(ps))+("" if len(wavelet_meta["participants"]) <= 3 else ("..."))+"<br />"
	res += '</div><div style="clear:both"></div><br />'
	res += '<div style="font-size:110%; width:100%">'
	res += innerhtml
	return res
    
class WaveReader():
  # wavereader from here
    session = "503282974482375274562"
    cookie = "DQAAAI8AAADqGuAdyCS0oaSk8PE4FDZZUl_KCmr0Gj6AVICpeE9WScTxIjM5CJLrNI23neGAQtXEDs51NkaLaxoik-IRUyLxwpzwa5Q3sUeRJ9Xo1Zh-6bpZlckaS242zuacV_Fk7qLULp2JRf1I5YbFalpolOU2_BzyBenDi9pf_22hhBJWQwXWm9c4YYQOlynF2fLI08Q"

    
    anntags = {"conv/title" : {"start": "", "end" : ""},
          "style/fontWeight" : {"start": '<font style="font-weight:<%value%>">', "end" : '</font>'},
          "style/fontSize" : {"start": '<font style="font-size:<%value%>">', "end" : '</font>'},
          "style/fontStyle" : {"start": '<font style="font-style:<%value%>">', "end" : '</font>'},
          "style/fontFamily" : {"start": '<font style="font-family:<%value%>">', "end" : '</font>'},
          "style/textDecoration" : {"start": '<font style="text-decoration:<%value%>">', "end" : '</font>'},
          "style/color" : {"start": '<font style="color:<%value%>">', "end" : '</font>'},
          "style/backgroundColor" : {"start": '<font style="background-color:<%value%>">', "end" : '</font>'},
          
          "link/manual" : {"start": '<a href="<%value%>">', "end" : '</a>'},
          "link/auto" : {"start": '<a href="<%value%>">', "end" : '</a>'},
          "link/wave" : {"start": '<a href="http://archive.waverz.com/<%value%>/">', "end" : '</a>'},
          
          "spell" : {"start": "", "end" : ""},
          "lang" : {"start": "", "end" : ""}
          }

    wiredata = "" # wire data
    wireobj = None # deserialized object
    title = "" # wave title
    plaintitle = "" # wave title in plaintext
    renderedHTML = ""
    participants = []
    last_modified = None
    tags = [] # wave tags
    blips = { } # blips data
    services = [] # list of users with @appspot.com suffix 
    waverenderer = DefaultWaveRenderer()
    rootwavelet = { }
    

    def refresh_wire_appengine(self, waveid):
	"""use google's appengine api to fetch a wave"""
	from google.appengine.api import urlfetch
	from google.appengine.api import urlfetch_errors
	url = "https://wave.google.com/wave/wfe/fetch/"+waveid+"/"+self.session+"?v=3"
	logging.info("fetching "+url)
	retry = 2
	while (retry > 0):
	    try:
		result = urlfetch.fetch(url = url, method = urlfetch.GET, 
					headers = {'Cookie': "WAVE="+self.cookie}) 
	    except urlfetch_errors.DownloadError, e:
		logging.info("fetch failed: "+str(e))
		retry -= 1
		if (retry == 0):
		    logging.info("Fetch: giving up")
		    return None
		continue
	    break
	logging.info("fetch success")
	return unicode(result.content[5:],"utf-8")
    
    def refresh_wire_urllib2(self, waveid):
	"""use urllib2 to fetch a wave"""
	import httplib
	connection = httplib.HTTPSConnection("wave.google.com")
	connection.request("GET", "/wave/wfe/fetch/"+waveid+"/"+self.session+"?v=3",
			   None,
			   {'Cookie': "WAVE="+self.cookie,
			    'User-Agent' : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/4.0.249.11 Safari/525.13"
			    } )
	http_response = connection.getresponse() 
	http_data = http_response.read()
	connection.close()
	return unicode(http_data[5:],"utf-8")
	
    def refresh_wire(self, waveid):
	"""demuxes GAE vs command line requests"""
	# todo: determine, if called from app engine, and call appropiate functions
	return self.refresh_wire_urllib2(waveid)
    
    
    def parse_time(self, num):
	return datetime.datetime.fromtimestamp( (1258408800000 + num) / 1000)
    
    def wavelet_parse(self, obj):
	return { "wave" : obj[1], 
		 "wavelet" : obj[2], 
		 "last_modified" : self.parse_time(obj[8][0]),
		 "created" : self.parse_time(obj[4][0]),
		 "root_blip" : obj[6] if (6 in obj) else "",
		 "content" : obj[16] if (16 in obj) else "",
		 "participants" : obj[5],
		 "raw" : obj }
    
    def blip_parse(self, obj):
        return {
          "id": obj[1],
          "creator": obj[2],
          "content": obj[16] if (16 in obj) else "",
          "children": obj[5],
          "last_modified": self.parse_time(obj[3][0]),
          "contributors": obj[7],
          "raw": obj
	}

    def parse_attach(self, obj):
	"""Parse an attachment's name-value pairs"""
	res = { }
	if (obj == None):
	    return res
	if (not 2 in obj):
	    return res
	for item in obj[2]:
	    if (5 in item):
		pass
	    elif (4 in item):
		if (item[4][1] == "node"):
		    res[item[4][2][0][2]] = item[4][2][1][2]				
	return res
    
    def apply_style(self, token, style, data):
	"""renders a wave style to HTML"""
	if not style in self.anntags:
	    logging.info("unknown style: "+style)
	    return token
	token = self.anntags[style]["start"].replace("<%value%>", unicode(data))+token+self.anntags[style]["end"]
	return token
	
    def get_blip_text(self, cid):
	"""returns the plain-text of a blip"""
	if not (cid in self.blips):
	    return ""
	if (cid.startswith("attach+")):
	    return ""
	res = []
	if (16 in self.blips[cid]["raw"]):
	    obj = self.blips[cid]["raw"][16]
	    for item in obj[2]:
		if (5 in item):
		    if item[5] == True:
			continue
		elif (2 in item):
		    token = item[2]
		    res.append(token)
		elif (4 in item):
		    if (item[4][1] == "line"):
			res.append("\n")
	bliptext = "".join(res)
	return bliptext

    def get_root_text(self):
	"""returns the plain text of the root blip"""
	return self.get_blip_text(self.rootwavelet["root_blip"])
    
    def render_blip_content(self, cid, recursive = True):
	res = []
	nextstyle = []
	if not (cid in self.blips):
	    return ""
	if (cid.startswith("attach+")):
	    data = self.parse_attach(self.blips[cid]["raw"][16])
	    logging.info("attachment: "+cid+" => "+str(data))
	    return self.waverenderer.render_attachment(data, cid)
	intitle = False
	if (16 in self.blips[cid]["raw"]):
	    obj = self.blips[cid]["raw"][16]
	    for item in obj[2]:
		# res.append(str(item))
		# continue
		if (5 in item):
		    if item[5] == True:
			continue
		elif (2 in item):
		    token = item[2]
		    if (intitle):
			self.plaintitle = self.plaintitle + token if (self.plaintitle != "") else token
		    for s in nextstyle:
			token = self.apply_style(token,s[1],s[3])
		    if (intitle):
			self.title = self.title + " " + token if (self.title != "") else token
		    else:
			res.append(token)
		    nextstyle = []
		    continue
		    # res.append(item[2])
		elif (4 in item):
		    if (item[4][1] == "line"):
			res.append("<br />")
			if (intitle):
			    intitle = False
			    for s in nextstyle:
				if s[1] == "conv/title":
				    intitle = True
				pass
			    pass
		    elif (item[4][1] == "w:image"):
			iblipid = "attach+"+item[4][2][0][2]
			res.append(self.render_blip_content(iblipid))
			if (iblipid in self.blips):
			    del self.blips[iblipid]
		    elif (item[4][1] == "w:gadget"):
			res.append("<!-- inline gadget / not yet implemented / --><br>")
		    elif (item[4][1] == "body"):
			#don't.
			pass
		    elif (item[4][1] == "reply"):
			if not recursive:
			    continue
			# res.append("<br/><h2> - inline reply : "+str(item[4][2][0][2])+" - </h2><br />")
			iblipid = item[4][2][0][2]
			res.append(self.render_blip(iblipid))
			if (iblipid in self.blips):
			    del self.blips[iblipid]
			# res.append(str(
		    elif (item[4][1] == "w:state"):
			# nothing to do for state information
			continue
		    else:
			logging.info("unprocessed: "+str(item[4][1]))
		elif (1 in item):
		    if (2 in item[1]):
			if (len(item[1][2]) > 0):
			    # deleted item
			    pass
		    if (3 in item[1]):
			if (len(item[1][3]) > 0):
			    nextstyle.extend(item[1][3])
			    for s in nextstyle:
				if s[1] == "conv/title":
				    intitle = True
			    # logging.info("styles: "+str(item[1][3]))
	bliphtml = "".join(res)
	return bliphtml
	
    def render_blip(self, cid, canframe = True, recursive = True):
	if not (cid in self.blips):
	    return ""
	isframed = False
	bliphtml = self.render_blip_content(cid, recursive)
	if (len(bliphtml) > 0):
	    # logging.info("rendering blip: "+cid)
	    if (canframe):
		header = '<div style="border:1px solid #000000; padding:0px; margin-left:82px">'
		bliphtml = header + self.waverenderer.render_blip_header(self.blips[cid]) + bliphtml
		isframed = True
	    else:
		bliphtml = self.waverenderer.render_blip_header(self.blips[cid]) + bliphtml + '<hr size="1" />'
	    # bliphtml += '</td></table>'
	    pass
	if not recursive:
	    return bliphtml
	
	# render chlidren
	childarray = [ (b[6] if 6 in b else "") for b in self.blips[cid]["children"]]
	childarray.reverse()
	dosubframe = False
	for i in xrange(0,len(childarray)):
	    if not childarray[i] in self.blips.keys():
		continue
	    ch = childarray[i]
	    if (i == len(childarray) - 1):
		bliphtml += self.render_blip(ch, False)
	    else:
		bliphtml += self.render_blip(ch, True)
	if (isframed):
	    bliphtml += '</div>'
	return bliphtml
    	
    
    def render(self, recursive = True, renderer = DefaultWaveRenderer() ):
	"""renders a wave's content"""
	cwn = ""
	i = 0
	while (cwn != "googlewave.com!conv+root"):
	    bliplist = self.wireobj[1][i][1][2]
	    wavelet_meta = self.wavelet_parse(self.wireobj[1][i][1][1])
	    cwn = wavelet_meta["wavelet"]
	    i += 1
	self.participants = wavelet_meta["participants"]
	self.last_modified = wavelet_meta["last_modified"]
	self.waverenderer = renderer
	bliprender = self.render_blip(wavelet_meta["root_blip"], False, recursive)
	wavelet_meta["title"] = self.title
	self.renderedHTML = renderer.render_wave(wavelet_meta, bliprender)
	return self.renderedHTML
	
    def get_tags(self):
	"""returns the list of tags"""
	res = []
	if not ("tags" in self.blips):
	    return []
	if not (16 in self.blips["tags"]["raw"]):
	    return []
	obj = self.blips["tags"]["raw"][16]
	for item in obj[2]:
	    if (2 in item):
		res.append(item[2])
	return res
    
    def json_postprocess(self, obj):
	if isinstance(obj, list):
	    res = []
	    for item in obj:
		res.append(self.json_postprocess(item))
	    return res
	if isinstance(obj, dict):
	    res = {}
	    for key,value in obj.iteritems():
		if (isinstance(key, str) | isinstance(key,unicode)):
		    if (key.isdigit()):
			i = int(key)
			res[i] = self.json_postprocess(value)
		else:
		    res[key] = self.json_postprocess(value)
	    return res
	return obj

    def read(self, wid):
	"""reads the wave content from wire"""
	self.wiredata = self.refresh_wire(wid)
	if (self.wiredata == ""):
	    return False
	self.wireobj = simplejson.loads(self.wiredata)
	if (self.wireobj == False):
	    return False
	self.wireobj = self.json_postprocess(self.wireobj)
	logging.info(str(self.wireobj))
	# read all blip information here
	cwn = ""
	i = -1
	while (cwn != "googlewave.com!conv+root"):
	    i += 1
	    bliplist = self.wireobj[1][i][1][2]
	    wavelet_meta = self.wavelet_parse(self.wireobj[1][i][1][1])
	    cwn = wavelet_meta["wavelet"]
	self.rootwavelet = wavelet_meta
	for blipraw in bliplist:
	    blip = self.blip_parse(blipraw)
	    cid = blip["id"]
	    self.blips[cid] = blip
	return True
    

    def find_content(self,s, subobj = None, tpos = ""):
	"""returns the array placement of content string s"""
	res = []
	if (subobj == None):
	    subobj = self.wireobj
	# logging.info("searching in: "+str(subobj))
	if (subobj == s):
	    res.append(tpos)
	    logging.info("found: "+str(tpos))
	elif (isinstance(subobj, list)):
	    for i in xrange(0,len(subobj)):
		res.extend(self.find_content(s,subobj[i], tpos+" -> "+str(i)))
	elif (isinstance(subobj, dict)):
	    for k,v in subobj.iteritems():
		res.extend(self.find_content(s,subobj[k], tpos+' -> "'+str(k)+'"'))
	elif (isinstance(subobj,str)) | (isinstance(subobj,unicode)):
	    pass
	else:
	    logging.info("uninterpreted tag: "+str(subobj))
		
	return res

if __name__ == '__main__':
    w = WaveReader()
    w.read("googlewave.com!w+lwnQgiOSA")
    w.render()
    print w.get_root_text()

