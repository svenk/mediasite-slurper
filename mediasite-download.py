#!/usr/bin/python
# (c) 2015 GPL SvenK

# This is Python >2.7 with some Python3 compatibility.
from __future__ import print_function
def printerr(*objs): print(*objs, file=sys.stderr)

# dependencies
from requests import get, post
from pyquery import PyQuery as pq

# python builtin
from urlparse import urlparse
import urllib2
import json
import inspect
import argparse, sys
import datetime


def redux(compl_lst):
	simpl_lst = [item for sublist in compl_lst for item in sublist]
	if len(simpl_lst)>1: return simpl_lst
	if len(simpl_lst)==1: return simpl_lst[0]
	else: return not_found

"""
MediaSiteDownload offers methods to extract videos and information out of the SonicFoundry
MediaSite video portal. This relys on the observation that there is some JSONified API
(probably RestFul). Authentification is not included, but masquerade as a browser
(User Agent). The code is extensible and the program can be called as standalone.
"""
class MediaSiteDownloader:
	def __init__(self):
		# setup some defaults
		self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0'
		self.base = None
		self.not_found = "-Not found-"
		self.empty = "-empty-"
		self.servicePath = None;

		self.mapper = {
			'duration': lambda p: p['Duration'],
			'title':  lambda p: p['Title'],

			# If only one chapter, display as subtitle, else extract chapter titles
			'chapters': lambda p: [c['Text'] for c in p['Chapters']] if len(p['Chapters']) > 1 else self.empty,
			'subtitle': lambda p: p['Chapters'][0]['Text'] if len(p['Chapters'])==1 else self.empty,

			# the most valuable information
			'video_url': lambda p: redux([ [video['Location'] for video in stream['VideoUrls'] if  video['MimeType'] == "video/mp4"] \
					 for stream in p['Streams']  if not stream['HasSlideContent'] ]),

			# It is possible to download all slides as JPGs in the following way:
			# 1. filter for stream['HasSlideContent']
			# 2. Save b = stream['SlideBaseUrl']
			# 3. Consider stream['AspectRatio'] and decide for a wanted width x height in px
			# 3. Use p = stream['SlideImageFileNameTemplate'], replace {0:D4} by '%4d_%d_%d' % (slide['Number'], width, height in px)
			# 4. Download slide in stream['Slides'] as "http://base/$b/$p" with your desired width x height.
		}

	def parse_video_page(self, url):
		if not self.base:
			parsed_uri = urlparse(url) # can raise a valueerror or so
			self.base = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
			printerr("Using MediaSite base server %s" % self.base)

		r = get(url, headers={'User-Agent': self.user_agent})
		html = r.text

		q = pq(html) # construct PyQuery
		ressourceId = q("#ResourceId").text()
		if not self.servicePath:
			self.servicePath = q('#ServicePath').text()
			printerr("Using ServicePath %s" % self.servicePath)

		return ressourceId

	def get_video_information(self, ressourceId):
		if not self.base:
			raise ValueError("Did not set Base server name yet. You can use parse_video_page to do so")

		playerOptions = self.base + self.servicePath + "/GetPlayerOptions"

		payload = {"getPlayerOptionsRequest": {
			"ResourceId": ressourceId,
			"QueryString":"",
			"UseScreenReader":False,
			"UrlReferrer":""}}

		headers = {
			'Content-type': 'application/json',
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'User-Agent': self.user_agent
		}

		r = post(playerOptions, data=json.dumps(payload), headers=headers)
		data = r.json()
		target = {}

		for k, m in self.mapper.iteritems():
			try:
				target[k] = m(data['d']['Presentation'])
			except KeyError, e:
				target[k] = not_found
			except IndexError, e:
				target[k] = not_found
			#except Exception, e:
			#	raise e
			#	printerr("Got another error: " + str(e))
		return target

	def format_html(self, d):
		s = "<h1>%(title)s <small>%(format_duration)s</small></h1> %(subtitle)s %(list_chapters)s <p><a href='%(video_url)s'>Download video (MP4)</a>"
		d.update({
			'format_duration': str(datetime.timedelta(seconds=d['duration']/1000)),
			'list_chapters': "\n<li>".join(d['chapters']) if not d['chapters'] == self.empty else '',
			'subtitle': d['subtitle'] if not d['subtitle'] == self.empty else '',
		})
		return s % d

	def run(self):
		parser = argparse.ArgumentParser(description='Python API Scraper for SonicFoundry MediaSite installations')

		# This is a bit fancy and should not be overstreched in usage:
		# Scalar/Stringy class attributes can be set directly from the command line.
		# Can be helpful for setting "empty", "not_found", "user_agent", etc.
		params = parser.add_argument_group('Class parameters', 'Arguments of the class')
		class_params = [i for i in dir(self) if not callable(getattr(self,i)) and not i.startswith('_')]
		for i in class_params:
			params.add_argument('--%s' % i, type=str, action='store', help="Set parameter %s, see code for details" % i)

		# These parameters actually trigger something
		actions = parser.add_argument_group('Actions', 'What to do')
		actions.add_argument('--parse', dest='url_to_parse', type=str, metavar='url', help='Give an URL to fetch')
		output_filters = {
			'json': lambda data: print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))), # pretty print
			'text': lambda data: [print("%10s: %s" % (k,v)) for k,v in data.iteritems()],
			'html': lambda data: print(self.format_html(data))
		}


		actions.add_argument('--format', dest='output_format', choices=output_filters.keys(), help="How to format output", default=output_filters.keys()[0])

		parser.parse_args(namespace=self)

		# Starting
		ressourceId = self.parse_video_page(self.url_to_parse)
		res = self.get_video_information(ressourceId)
		output_filters[self.output_format](res)


if __name__ == '__main__':
	MediaSiteDownloader().run()

