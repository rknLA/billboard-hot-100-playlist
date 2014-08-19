import datetime
import logging
import uuid
import urllib2

from flask import Flask, redirect, render_template, request, session, url_for

from billboard import scraper
from charter import Charter
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

def rdioFromSession(session):
  if 'uuid' in session and session['uuid'] in memory_store:
    session_data = memory_store[session['uuid']]
    if 'at' in session_data and 'ats' in session_data:
      return Rdio(RDIO_CREDS, (session_data['at'], session_data['ats']))
  return None

def clearSession(session):
  session_id = session.pop('uuid', None)
  if session_id is not None and session_id in memory_store:
    del memory_store[session_id]


@app.route("/")
def home():
  rdio = rdioFromSession(session)
  if rdio is None:
    # user is not logged in yet, render index
    clearSession(session)
    session['uuid'] = uuid.uuid4().hex
    return render_template('index.html')

  # else render logged in view
  return redirect(url_for('charts'))
  return render_template('authenticated.html', username=currentUser['username'], playlists=userPlaylists)

@app.route("/login")
def login():
  session_id = session['uuid']
  removeFromStore(session_id)
  rdio = Rdio(RDIO_CREDS)
  auth_url = rdio.begin_authentication(callback_url=url_for('rdio_callback', _external=True),
                                       mode='redirect')
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
  clearSession(session)
  return redirect(url_for('home'))

@app.route("/charts")
def charts():
  charts = scraper.chartList()
  try:
    rdio = rdioFromSession(session)
    currentUser = rdio.call('currentUser', {'extras': '-*,username'})['result']
  except urllib2.HTTPError:
    return redirect(url_for('logout'))
  return render_template('chart_list.html', username=currentUser['username'], charts=charts)

@app.route("/charts/<billboard_uri>")
def get_chart(billboard_uri):
  try:
    rdio = rdioFromSession(session)
    currentUser = rdio.call('currentUser', {'extras': '-*,username'})['result']
    userPlaylists = rdio.call('getPlaylists', {'extras': '-*,name,key'})['result']['owned']
  except urllib2.HTTPError:
    return redirect(url_for('logout'))

  chart = scraper.scrapeChart(billboard_uri)

  if len(chart['keys']) == 0:
    logging.warn("Empty chart at %s" % billboard_uri)
    return render_template('error.html', chart=chart)

  return render_template('save_chart.html',
                         username=currentUser['username'],
                         playlists=userPlaylists,
                         chart=chart)


@app.route("/save")
def save():
  rdio = rdioFromSession(session)
  if rdio is None:
    clearSession(session)
    return redirect(url_for('home'))

  try:
    target_playlist = request.args.get('destination', None)
    playlist_name = request.args.get('name', 'Billboard Playlist')
    tracks = request.args.get('tracks', None)
    if target_playlist is None:
      new_playlist = rdio.call('createPlaylist', {'name': "Billboard " + playlist_name,
                                                  'description': '',
                                                  'tracks': 't123'})['result']
      target_playlist = new_playlist['key']

    if tracks is None:
      return render_template('error.html')
    result = Charter(rdio=rdio).updatePlaylist(target_playlist, tracks)
    if result['status'] != 'ok':
      raise urllib2.HTTPError()
  except urllib2.HTTPError:
    return render_template('error.html')

  return render_template('complete.html', result=result['result'])
  

if __name__ == "__main__":
  app.run(port=3030)
