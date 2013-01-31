import logging
import os
import json

from zeroinstall.support import basedir
from zeroinstall.injector import model, namespaces

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG) # NOCOMMIT

class FeedPlugins(object):
	_config_namespace = (namespaces.config_site, namespaces.config_prog, 'plugins')

	def __init__(self, url, plugins):
		self.url = url
		self.plugins = set(plugins)

	@classmethod
	def _config_filename(cls, url):
		return model._pretty_escape(url) + '.json'
	
	@property
	def _config_path(self):
		return os.path.join(basedir.save_config_path(*self._config_namespace), self._config_filename(self.url))

	@classmethod
	def load(cls, url):
		plugins = []
		for path in basedir.load_config_paths(*cls._config_namespace):
			json_path = os.path.join(path, cls._config_filename(url))
			if os.path.exists(json_path):
				LOGGER.debug("Found plugin file %s for %s", json_path, url)
				with open(json_path) as input_file:
					plugins = [Plugin(attrs) for attrs in json.load(input_file)]
				break
		else:
			LOGGER.debug("No plugin file found for %s", url)
		return cls(url, plugins)
	
	def save(self):
		with open(self._config_path, 'w') as output_file:
			json.dump([plugin.attrs for plugin in self.plugins], output_file, indent=2)
	
	def remove(self, url):
		found = set()
		for plugin in self.plugins:
			if plugin.url == url:
				found.append(plugin)

		if not found:
			raise KeyError(url)

		LOGGER.debug("removing plugins: %r" % (found,))
		self.plugins = self.plugins.difference(found)
	
	def add(self, url):
		new_plugin = Plugin.create(url)
		if new_plugin in self.plugins:
			raise SafeException("Feed %s already contains plugin: %s" % (self.url, new_plugin))
		self.plugins.add(new_plugin)


class Plugin(object):
	def __init__(self, attrs):
		self.attrs = attrs
	
	@classmethod
	def create(cls, url):
		return cls({'url': url})

	@property
	def url(self):
		return self.attrs['url']
	
	def __eq__(self, other):
		return self.attrs == other.attrs

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.url)
	
	def __str__(self):
		return self.url

	def __repr__(self):
		return "<Plugin: %s>" % (self,)

