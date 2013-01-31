"""
The B{0install plugin} command-line interface.
"""

# Copyright (C) 2011, Thomas Leonard
# See the README file for details, or visit http://0install.net.

from __future__ import print_function

import os
import logging

from zeroinstall import SafeException, _
from zeroinstall.cmd import UsageError
from zeroinstall.injector import model
from zeroinstall.plugins import FeedPlugins

LOGGER = logging.getLogger(__name__)

syntax = "PROGRAM-FEED"

def add_options(parser):
	parser.add_option("-a", "--add", action='append', default=[], help=_("add a plugin"))
	parser.add_option("-r", "--remove", action='append', default=[], help=_("remove a plugin"))
	parser.add_option("--editor", help=_("use editor (default: $EDITOR)"), default=os.environ.get('EDITOR', 'vi'))
	parser.add_option("-l", "--list", action='store_true', help=_("list plugins"))

def handle(config, options, args):
	if len(args) == 0 and options.list:
		return list_all_plugins()

	if len(args) != 1: raise UsageError()
	feed_url = model.canonical_iface_uri(args[0])
	plugins = FeedPlugins.load(feed_url)

	for plugin_url in options.add:
		plugins.add(plugin_url)
		print("Added plugin: %s to feed: %s" %( plugin_url, feed_url))

	for plugin_url in options.remove:
		try:
			plugins.remove(plugin_url)
			print("Removed plugin: %s from feed: %s", plugin_url, feed_url)
		except KeyError:
			raise SafeException("Feed %s has no such plugin: %s" % (feed_url, plugin_url))
	
	if options.remove or options.add:
		plugins.save()
	
	if options.list:
		print("Plugins for %s:" % (feed_url))
		for plugin in plugins:
			print(" - %s" % (plugin.url))

def list_all_plugins():
	raise Exception("TODO...")
