import unittest

from config import RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET, RDIO_TEST_OAUTH_TOKEN
from lib.charter import Charter
from lib.rdio import Rdio

class CharterRdioAPITests(unittest.TestCase):

  def setUp(self):
    self.rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET),
                     RDIO_TEST_OAUTH_TOKEN)
    test_playlist = self.rdio.call('createPlaylist',
                                   {'name': 'charter test',
                                    'description': 'test charts',
                                    'tracks': 't10016979,t28083363,t7357573'})
    self.playlist = test_playlist['result']
    self.playlist_key = self.playlist['key']
    self.charter = Charter(rdio=self.rdio)

  def tearDown(self):
    self.rdio.call('deletePlaylist', {'playlist': self.playlist_key})

  def test_changing_order(self):
    expected_update = ['t28083363', 't7357573', 't10016979']
    self.charter.updatePlaylist(self.playlist_key, expected_update)
    playlist = self.rdio.call('get', params={'keys': self.playlist_key,
                                             'extras': '-*,name,trackKeys'})
    actual_tracks = playlist['result'][self.playlist_key]['trackKeys']
    self.assertListEqual(actual_tracks, expected_update)

  
