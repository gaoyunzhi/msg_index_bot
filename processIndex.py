from db import db
from channel import Channel
from datetime import datetime
from common import getCompact

def getPostLinkBubble(item):
	try:
		result = item.find('a', class_='tgme_widget_message_forwarded_from_name')['href']
		int(result.strip('/').split('/')[-1])
		return result
	except:
		return item.find('a', class_='tgme_widget_message_date')['href']

def getOrigChannel(item):
	orig_link = item.find('a', class_='tgme_widget_message_date')['href']
	return orig_link.strip('/').split('/')[-2]

def addMentionedChannel(item, referer):
	for link in item.find_all('a'):
		link = link.get('href', '')
		if link.find('/t.me/') == -1:
			continue
		Channel(link.strip('/').split('/')[-1]).save(db, referer)

def getText(item, class_name):
	try:
		return item.find('div', class_=class_name).text
	except:
		return ''

def getMainText(text_fields):
	if text_fields[0] and len(text_fields[0]) > 5:
		return text_fields[0]
	for x in text_fields[1:] + [text_fields[0]]:
		if x:
			return x

def getTime(item):
	try:
		s = (item.find('a', class_='tgme_widget_message_date').
				find('time')['datetime'][:-6])
	except:
		print(item.find('a', class_='tgme_widget_message_date'))
		return 0
	format = '%Y-%m-%dT%H:%M:%S'
	return datetime.strptime(s, format).timestamp()

def processBubble(item):
	post_link = getPostLinkBubble(item)
	channel = post_link.split('/')[0]
	Channel(channel).save(db, getOrigChannel(item))
	addMentionedChannel(item)
	text_fields_name = [
		'link_preview_title',
		'tgme_widget_message_text', 
		'tgme_widget_message_document_title', 
		'link_preview_description']
	text_fields = [getText(item, field) for field in text_fields_name]
	if ''.join(text_fields) == '':
		return
	[db.addIndex(post_link, text) for text in text_fields]
	db.setMainText(post_link, getCompact(getMainText(text_fields)))
	db.setTime(post_link, getTime(item))