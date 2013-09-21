import logging

from lib.rdio import Rdio

class Charter(object):

  def __init__(self, rdio=None):
    self.rdio = rdio

  def updatePlaylist(self, playlist_key, new_tracks):
    if self.rdio is None:
      logging.error('You tried to update a playlist without assigning Charter an Rdio instance')
      return

    existing = self.rdio.call('get', {'keys': playlist_key, 'extras': '-*,trackKeys,length'})['result'][playlist_key]
    removal_result = self.rdio.call('removeFromPlaylist', {'playlist': playlist_key,
                                                           'index': 0,
                                                           'count': existing['length'],
                                                           'tracks': ','.join(existing['trackKeys'])})

    # removal_result will be the playlist data, the length should be 0 at this point
    updated = self.rdio.call('addToPlaylist', {'playlist': playlist_key,
                                               'tracks': ','.join(new_tracks)})
    return updated

