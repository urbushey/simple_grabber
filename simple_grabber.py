#!/usr/bin/python2.7
# simple_grabber.py
"""
Grabs the most recent Simple Desktop images from their RSS feed and
puts them in the rotation of desktop images. 

Writes a simple json cache to disk and only adds updates (won't repeat
	a download.)
"""

import feedparser
import json
import pickle
import requests
import os
from BeautifulSoup import BeautifulSoup
from datetime import datetime

FEED_URL  = 'feed://feeds.feedburner.com/simpledesktops'
BASE_URL  = 'http://simpledesktops.com'
BG_DIR    = '/Users/ubushey/Dropbox/Pictures/Wallpapers/Simple'
CACHEFILE = 'simple_grabber_cache.p'

def scrape_link(link):
	""" Scrapes the given linked site for a download link. """ 
	#html = urlopen(link).read()
	response = requests.get(link)
	html = response.text
	soup = BeautifulSoup(html)
	dl_div = soup.find("div", "desktop")
	a = dl_div.find("a")
	href = a["href"]
	dl_link = BASE_URL + href
	return dl_link

def download_image(image):
	""" Downloads an image, names it according to the image title from the RSS feed.
	Returns the datetime on which the image was downloaded"""
	filename = image['title'] + ".png"
	fullpath = os.path.join(BG_DIR, filename)
	response = requests.get(image['dl_link'])
	with open(fullpath, 'wb') as fh:
		fh.write(response.content)
	print "Downloaded " + fullpath
	now = datetime.now()
	return now

def main():
	# Get the feed 
	feed = feedparser.parse(FEED_URL)
	# Creates a list of dictionaries containing links to sites, titles 
	# from the feed.
	images = [dict(link=entry['link'], title=entry['title']) for entry in feed['entries']]
	# Scrape each page for the download link and add it to list of dictionaries
	for image in images:
		image['dl_link'] = scrape_link(image['link'])
	# Read or create cache
	try:
		with open(CACHEFILE) as fh:
			cache = pickle.load(fh)
	except IOError:
		print "No cache exists, downloading all files in RSS feed"
		cache = {}
	#download items that are not in cache:
	for image in images:
		if image['link'] not in cache.keys():
			# Set the datetime in the cache
			dt = download_image(image)
			cache[image['link']]=dt
		else:
			print image['title'] + " previously grabbed, skipping."
			pass
	# Save the pickle
	pickle.dump(cache, open(CACHEFILE, "wb"))

if __name__ == "__main__":
	main()



