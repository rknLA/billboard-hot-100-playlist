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
    self.playlist_key = self.playlist['key']
    self.charter = Charter(rdio=self.rdio)

  def tearDown(self):
    self.rdio.call('deletePlaylist', {'playlist': self.playlist_key})

  def test_changing_order(self):
    new_list = ['t28083363', 't7357573', 't10016979']
    self.charter.update_playlist(self.playlist_key, new_list)
    playlist = self.rdio.call('get', params={'keys': self.playlist_key,
                                             'extras': '-*,name,trackKeys'})
    new_tracks = playlist['result']['trackKeys']
    print new_tracks
    self.assertTrue(False)

  
