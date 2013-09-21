import unittest

from config import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET, RDIO_TEST_OAUTH_TOKEN
from lib.charter import Charter
from lib.rdio import Rdio

class CharterRdioAPITests(unittest.TestCase):

  def setUp(self):
    self.rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET),
                     RDIO_TEST_OAUTH_TOKEN)
    test_playlist = rdio.call('createPlaylist',
                              {'name': 'charter test',
                               'description': 'test charts',
                               'tracks': 't10016979,t28083363,t7357573'})
    self.playlist = test_playlist['result']
    
    chart_updater = Charter()
    chart_updater.authenticate()

  def tearDown(self):
    rdio.call('deletePlaylist', {'playlist': self.playlist['key']})

  def test_updating_a_playlist(self):
    new_list = ['
    chart_updater.update(playlist=RDIO_TEST_PLAYLIST_KEY, )

  
