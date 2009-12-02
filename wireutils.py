#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright @ 2009, Waverz.com - BSD license - Information wants to be free!

# misc utilities

def webrequest(method, host, url, headers, payload):
    """Request an HTTPS page, either via the appengine api, or using httplib"""
    import urllib
    
    def fetch_urllib2(method, host, url, headers, payload):
        """use urllib2 to fetch a wave"""
        import httplib
        connection = httplib.HTTPSConnection(host)
        connection.request(method, url, payload, headers)
        http_response = connection.getresponse() 
        http_data = http_response.read()
        connection.close()
        return http_data

    if (isinstance(payload, dict)):
        payload = urllib.urlencode(payload)
    if ((method == "POST")) & (not ("Content-Type" in headers)):
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    if not ("User-Agent" in headers):
        headers['User-Agent'] = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/4.0.249.11 Safari/525.13"
    return fetch_urllib2(method,host,url,headers,payload)



if (__name__ == "__main__"):
    session = "503282974482375274562"
    cookie = "DQAAAI8AAADqGuAdyCS0oaSk8PE4FDZZUl_KCmr0Gj6AVICpeE9WScTxIjM5CJLrNI23neGAQtXEDs51NkaLaxoik-IRUyLxwpzwa5Q3sUeRJ9Xo1Zh-6bpZlckaS242zuacV_Fk7qLULp2JRf1I5YbFalpolOU2_BzyBenDi9pf_22hhBJWQwXWm9c4YYQOlynF2fLI08Q"
    waveid = "googlewave.com!w+fkvUXIemA"
    print webrequest("GET", "wave.google.com", "/wave/wfe/fetch/"+waveid+"/"+session+"?v=3",
                     {'Cookie': "WAVE="+cookie}, None)
