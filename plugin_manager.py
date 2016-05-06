# -*- coding: utf-8 -*-
from __future__ import print_function
import glob
import imp
import re


class PluginManager(object):
    def __init__(self):
        self.plugins_dir = 'plugins'
        self.plugins = {}

    def init_plugins(self):
        print('Searching for plugins...')
        module_paths = glob.glob("{0}/[!_]*.py".format(self.plugins_dir))
        print('Found {0} plugins.'.format(len(module_paths)))
        print('Loading plugins...')

        for module_path in module_paths:
            module_name = re.match(
                r'{0}\/(.*)\.py'.format(self.plugins_dir),
                module_path
            ).group(1)
            self.plugins[module_name] = imp.load_source(
                'slackbot_plugin_{0}'.format(module_name),
                module_path
            ).Plugin()
            print(' * Plugin "{0}" loaded.'.format(module_name))
        print('-' * 64)

        return None

    def plugin_query(self, input_msg, user, channel):
        for plugin_name in self.plugins:
            for rule in self.plugins[plugin_name].commands:
                if not re.match(rule, input_msg):
                    continue

                response = self.plugins[plugin_name].commands[rule](
                    input_msg,
                    user,
                    channel
                )

                if response is not None:
                    yield response
