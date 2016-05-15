import base64
import requests
import time
from xml.dom import minidom

def call(answer):
	# Converting code to base64
	s = base64.b64encode(bytes(answer))
	# creating xml content for query posting
	xml = """<?xml version="1.0" encoding="utf-8" ?>
<uclassify xmlns="http://api.uclassify.com/1/RequestSchema" version="1.01">
  <texts>
    <textBase64 id="text_1">"""+s+"""</textBase64>
  </texts>
  <readCalls readApiKey="HoGp2i9XYbPy">
    <classify id="call_1" username="prfekt" classifierName="Tonality" textId="text_1"/>
  </readCalls>
</uclassify>"""
	# header for http request
	headers = {'Content-Type':'text/xml', 'charset':'utf-8'}
	# posting the request
	x = 0
	while(x == 0):
		try:
			r = requests.post("http://api.uclassify.com/", data = xml, headers = headers).text
			x = 1
		except:
			time.sleep(5)
			x = 0
	# parsing the response present in xml format in variable r
	xmldoc = minidom.parseString(r)
	itemlist = xmldoc.getElementsByTagName('class')
	num = 0.0
	deno = 0.0
	for s in itemlist:
		# print(s.attributes['className'].value + '\t' + s.attributes['p'].value)
		deno += float(s.attributes['p'].value)
		if s.attributes['className'].value == 'Corporate':
			num = float(s.attributes['p'].value)

	formalness = int(100*num/deno)
	return formalness
