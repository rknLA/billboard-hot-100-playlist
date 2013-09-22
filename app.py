import datetime
import logging
import uuid

from flask import Flask, redirect, render_template, request, session, url_for

import config
from rdio.rdio import Rdio

app = Flask(__name__)
app.debug = True
app.secret_key = config.APP_SECRET_KEY

RDIO_CREDS = (config.RDIO_CONSUMER_KEY, config.RDIO_CONSUMER_SECRET)

STORE_DURATION = datetime.timedelta(hours=1)
memory_store = dict()

def removeFromStore(key):
  # store is expected to be a dict
  if key in memory_store:
    del memory_store[key]

def addToStore(key, data):
  if len(memory_store) > 100:
    pruneOldSessionData()
  memory_store[key] = data

def pruneOldSessionData():
  for key in memory_store.keys():
    if key in memory_store:
      data = memory_store[key]
      now = datetime.datetime.now()
      if now > data['expires']:
        del memory_store[key]


@app.route("/")
def home():
  if 'uuid' in session and session['uuid'] in memory_store:
    session_data = memory_store[session['uuid']]
    if 'at' in session_data and 'ats' in session_data:
      rdio = Rdio(RDIO_CREDS, (session_data['at'], session_data['ats']))
      try:
        currentUser = rdio.call('currentUser', {'extras': '-*,username'})['result']
        userPlaylists = rdio.call('getPlaylists', {'extras': '-*,name,key'})['result']['owned']
      except urllib2.HTTPError:
        return redirect(url_for('logout'))
      logging.debug("rdio user: %s", currentUser)
      logging.debug("playlists: %s", userPlaylists)
      return render_template('authenticated.html', username=currentUser['username'], playlists=userPlaylists)
  else:
    session['uuid'] = uuid.uuid4().hex
    return render_template('index.html')

@app.route("/login")
def login():
  session_id = session['uuid']
  removeFromStore(session_id)
  rdio = Rdio(RDIO_CREDS)
  auth_url = rdio.begin_authentication(callback_url=url_for('rdio_callback', _external=True))
  session_data = {'expires': datetime.datetime.now() + STORE_DURATION,
                  'rt': rdio.token[0],
                  'rts': rdio.token[1]}
  addToStore(session_id, session_data)
  return redirect(auth_url)

@app.route("/rdio_callback")
def rdio_callback():
  session_id = session['uuid']
  session_data = memory_store[session_id]
  request_token = session_data.get('rt', None)
  request_token_secret = session_data.get('rts', None)
  verifier = request.args.get('oauth_verifier', None)
  if verifier is None or request_token is None or request_token_secret is None:
    logging.warn("OAuth callback error")
    return redirect(url_for('logout'))
  rdio = Rdio(RDIO_CREDS, (request_token, request_token_secret))
  rdio.complete_authentication(verifier)
  session_data['at'] = rdio.token[0]
  session_data['ats'] = rdio.token[1]
  del session_data['rt']
  del session_data['rts']
  return redirect(url_for('home'))

@app.route("/logout")
def logout():
  session_id = session.pop('uuid', None)
  if session_id is not None:
    del memory_store[session_id]
  return redirect(url_for('index'))
  

if __name__ == "__main__":
  app.run()
