# -*- coding: utf-8 -*-
from __future__ import print_function
from plugin_manager import PluginManager
from slackclient import SlackClient
from tomorrow import threads
from inspect import isgenerator
import time
import sys
from socket import error as SocketError


class SlackBot(object):
    def __init__(self, login_token):
        self.LOGIN_TOKEN = login_token
        self.channel_data = None
        self.user_data = None
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_plugins()

    def _connect(self):
        self.sc = SlackClient(self.LOGIN_TOKEN)
        if self.sc.rtm_connect():
            return True
        else:
            return None

    def _get_team_data(self):
        self.channel_data = self.sc.api_call("channels.list",
                                             token=self.LOGIN_TOKEN)
        self.user_data = self.sc.api_call("users.list",
                                          token=self.LOGIN_TOKEN)
        return None

    def _send_rtm_msg(self, chan, msg):
        self.sc.rtm_send_message(chan, msg)
        return None

    def connect(self):
        print('Connecting to Slack...')
        while True:
            try:
                if self._connect():
                    print('Succesfully connected to Slack!')
                    print('Retrieving channel and user data...')
                    self._get_team_data()
                    print('Starting rtm session...')
                    print('-' * 64)
                    return None
                else:
                    print('Connection failed, trying again...')
            except KeyboardInterrupt:
                print('\nShutting down...')
                sys.exit(1)
            return None

    def get_message(self):
        try:
            data = self.sc.rtm_read()
        except SocketError:
            return None

        if data and 'type' in data[0]:
            if data[0]['type'] == 'message' and 'text' in data[0]:
                return data[0]['text'], data[0]['user'], data[0]['channel']
        return None

    @threads(5, timeout=30)
    def async_plugin_query(self, message, user, channel):
        response = self.plugin_manager.plugin_query(message, user, channel)
        if response is None:
            return None
        if isgenerator(response):
            for sub_response in response:
                if isgenerator(sub_response):
                    for sub_sub_response in sub_response:
                        if sub_sub_response is None:
                            continue
                        output_message, output_channel = sub_sub_response
                        print(output_channel, output_message)
                        self._send_rtm_msg(output_channel, output_message)
                else:
                    if sub_response is None:
                        continue
                    output_message, output_channel = sub_response
                    print(output_channel, output_message)
                    self._send_rtm_msg(output_channel, output_message)
        else:
            output_message, output_channel = response
            print(output_channel, output_message)
            self.__send_rtm_msg(output_channel, output_message)
        return None

    ''' Slack API doesn't send you real room and user names via sc.rtm_read().
        It sends their ids instead. However, you can use both ids
        or room names/usernames when sending data back.
        When storing room names/usernames in human-readable form is necessary,
        we need to additionally download channel and user lists and then
        replace channel and user ids with their actual names with that data.

        Channel and user lists can be obtained using channels.list and
        users.list methods respectively.
        https://api.slack.com/methods/channels.list
        https://api.slack.com/methods/users.list
    '''

    def resolve_username(self, user_id):
        for user in self.user_data['members']:
            if user['id'] == user_id:
                return user['name']
        return user_id

    def resolve_channel_name(self, channel_id):
        for room in self.channel_data['channels']:
            if room['id'] == channel_id:
                return room['name']
        return channel_id

    def run(self):
        self.connect()
        try:
            while True:
                msg = self.get_message()
                if msg:
                    message, user_id, channel_id = msg
                    user = self.resolve_username(user_id)
                    channel = self.resolve_channel_name(channel_id)
                    print(channel, user, message)
                    self.async_plugin_query(
                        message,
                        user,
                        channel
                    )
                time.sleep(0.1)  # preventing lags
        except KeyboardInterrupt:
            print('\nShutting down...')
            sys.exit(1)
            return None
        return None
