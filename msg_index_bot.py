#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail
from common import debug_group, tele, log_call, sendDebugMessage
from command import setupCommand
import threading
import random
import backfill
import clean
import sys
import dbase
from dbase import channels, coreIndex
import webgram
import time

@log_on_fail(debug_group)
@log_call()
def indexingImp():
	for channel, score in channels.items():
		if score < 0 or random.random() > 1.0 / min(
				score ** 2.5 + 1, score ** 2 * 2 + 1):
			continue
		if 'test' in sys.argv and random.random() > 0.1:
			continue # better testing
		posts = webgram.getPosts(channel, 1) # force cache
		for post in posts:
			dbase.update(post)
		if len(posts) > 1: # save http call
			dbase.updateAll(webgram.getPosts(channel))
	sendDebugMessage(*(['indexingImpDuration'] + dbase.resetStatus()), persistent=True)

@log_on_fail(debug_group)
@log_call()
def indexBackfill():
	last_record = time.time()
	for channel, score in channels.items():
		backfill.backfill(channel)
		if time.time() - last_record > 60 * 60:
			last_record = time.time()
			sendDebugMessage(*(['indexBackfillDuration'] + dbase.resetStatus()), persistent=True)
	sendDebugMessage(*(['indexBackfillDuration'] + dbase.resetStatus()), persistent=True)

@log_on_fail(debug_group)
@log_call()
def outputChannels():
	fn = 'db/channel_output.html'
	with open(fn, 'w') as f:
		f.write('')
	for channel, score in dbase.channels.items():
		if not 0 <= score <= 2:
			continue
		key = channel + '/0'
		if dbase.timestamp.get(key, 0) < time.time() - 60 * 24 * 24 * 7:
			continue
		line = '%s https://t.me/%s %d %s\n\n' % (
			dbase.maintext.get(key, ''),
			channel, score,
			dbase.index.get(key, ''))
		with open(fn, 'a') as f:
			f.write(line)

@log_call()
def indexing():
	if len(coreIndex) == 0:
		dbase.fillCoreIndex()
	outputChannels()
	if len(dbase.maintext.items()) > 2500000:
		clean.indexClean()
	indexingImp() 
	indexBackfill()
	threading.Timer(1, indexing).start()

if __name__ == '__main__':
	setupCommand(tele.dispatcher)
	threading.Timer(1, indexing).start() 
	if 'nocommand' not in sys.argv:
		tele.start_polling()
		tele.idle()
