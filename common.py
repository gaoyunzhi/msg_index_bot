from telegram.ext import Updater
from telegram_util import isCN, tryDelete
import hanzidentifier
import os
import time

with open('token') as f:
	token = f.read().strip()
tele = Updater(token, use_context=True)  # @msg_index_bot
debug_group = tele.bot.get_chat(420074357)

def isSimplified(text):
	cn = sum([isCN(c) + hanzidentifier.is_simplified(c) for c in text])
	for c in text:
		if isCN(c) and not hanzidentifier.is_simplified(c):
			return False
	return cn * 2 >= len(text)

last_debug_message = None

def sendDebugMessage(*args, persistent=False):
	print(*args)
	message = ' '.join([os.uname()[1].split('-')[0]] + 
		[str(x) for x in args])
	if persistent:
		debug_group.send_message(message)
		return
	global last_debug_message
	if last_debug_message:
		tryDelete(last_debug_message)
	last_debug_message = debug_group.send_message(message)

def log_call():
	def decorate(f):
		def applicator(*args, **kwargs):
			new_args = [f.__name__] + list(args) + ['start']
			sendDebugMessage(*new_args)
			f(*args,**kwargs)
			new_args[-1] = 'end'
			sendDebugMessage(*new_args)
		return applicator
	return decorate

def log_time():
	def decorate(f):
		def applicator(*args, **kwargs):
			start = time.time()
			f(*args,**kwargs)
			to_print = [f.__name__] + list(args) + [int(time.time() - start)]
			print(*to_print)
		return applicator
	return decorate