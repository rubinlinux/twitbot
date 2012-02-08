#!/usr/bin/python
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



from exceptions import IOError
import twitter
from oyoyo.client import IRCClient, IRCApp
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import logging

# I store the twitter.Api object in a dictionary, in case I want to add more
# objects for other networks.
api = {}
api['ChannelAfternet'] = twitter.Api(consumer_key='xxx',
      consumer_secret='xxx',
      access_token_key='xxx',
      access_token_secret='xxx')


# logging.basicConfig(level=logging.DEBUG)

def connect_callback(cli):
    # Join the channel
    helpers.join(cli, "#nosnam")

class MyHandler(DefaultCommandHandler):
    def endofmotd(self, *kwargs):
        '''I am relying on Afternet's endofmotd to signal when the bot
        has finished connecting to the network, rather than using oyoyo's
        default connect_callback, because oyoyo calls it too soon and the
        server ignores the join command.'''
        connect_callback(cli)

    def topic(self, nick, chan, topic):
        '''Called whenever a channel topic is changed. Should eventually
        have handlers instead of conditionals'''
        if chan.lower() == '#nosnam':
            self.chanAfternetTopic(chan, topic)

    def chanAfternetTopic(self, chan, topic):
        '''Update ChanAfternet topic'''
        newTopic = str(topic)

        # Split the new topic into segments
        newSegments = [item.strip() for item in newTopic.split('-')]

        # Fetch old topic segments, if any exist
        try:
            f = open('%s.txt' % chan, 'r')
            oldSegments = [item.strip() for item in f.readlines()]
            f.close()
        except IOError:
            oldSegments = []

        # Save and tweet new segments
        for newSegment in newSegments:
            if newSegment not in oldSegments:
                f = open('%s.txt' % chan, 'a')
                f.write(newSegment + '\n')
                f.close()
                api['ChannelAfternet'].PostUpdate(newSegment)
        
cli = IRCClient(MyHandler, host="irc.afternet.org", port=6667, nick="TwitterBot")
cli.blocking = True

app = IRCApp()
app.addClient(cli)
app.run()
