# Google Play privacy policy downloader
# Author: Rocky Slavin
# Date: 5/1/2015

import urllib2
import socket
from urllib2 import URLError
import urllib
import re
import csv

file = "../case study/testApk.list"
urlPrefix = "https://play.google.com/store/apps/details?id="
urlSuffix = "&hl=en"
outputDirectory = "../case study/policies/"
socket.setdefaulttimeout(15)

csv = csv.writer(open("../case study/policies.csv", "wb"))
csv.writerow(["App Name", "Policy", "Keywords"])
f = open(file, "r")

line = f.readline().rstrip("\n")

while line:
	print "Retreiving policy for " + line
	try:
		policyURL = urlPrefix + re.sub('\.apk$', '', line) + urlSuffix
		response = urllib2.urlopen(policyURL)
	except urllib2.HTTPError, e:
		if e.code == 404:
			csv.writerow([line, policyURL, "APPSTORE 404 ERROR"])
			print "BAD LINK"
			line = f.readline().rstrip("\n")
			continue
		else:
			csbv.writerow([line, policyURL, "HTTP ERROR: " + e.code])
	m = re.search('url\?q=(((?!href|&).)*)&(((?!href).)*)\" rel=\"nofollow\" target=\"_blank\"> Privacy Policy', response.read())
	if m:
		policyURL = m.group(1)
		try:
			urllib.urlretrieve(policyURL, outputDirectory + line + ".html")
		except URLError, e:
			if e.code == 404:
				csv.writerow([line, policyURL, "404 ERROR"])
				print "BAD LINK"
			else:
				csv.writerow([line, policyURL, "UNKNOWN ERROR"])
				print "ERROR RETRIEVING POLICY"
		except IOError, e:
			csv.writerow([line, policyURL, "TIMED OUT"])
			print "TIMEOUT"
		csv.writerow([line, policyURL])
	else:
		csv.writerow([line, "", "NO POLICY LINK"])
		policyURL = "NO POLICY FOUND"
	line = f.readline().rstrip("\n")

