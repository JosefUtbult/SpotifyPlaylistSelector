from crypt import methods
from shutil import ExecError
import flask
from flask import request
import json
import logging
import spotipy

from spotify_handler import SpotifyHandler

LOGFILE = 'SpotifyPlaylistSelector.log'
SPOTIFY_CLIENT_REDIRECT_URI = "https://example.com/callback/"

app = flask.Flask(__name__)

def check_settings(required_keys, request):
    try:
        data = request.get_json(force=True)
    except ExecError:
        return False, None
    
    for instance in required_keys:
        if not instance in data:
            return False, None
        elif data[instance] == None:
            return False, None

    return True, data

@app.route('/', methods=['GET'])
def page():
    try:
        return flask.render_template('page.html', darkmode=True)
    except spotipy.oauth2.SpotifyOauthError as e:
        raise e
    except Exception as e:
        logger.error(e)
        return flask.abort(500)

@app.route('/get-playlist-name', methods=['POST'])
def get_playlist_name():
    status, data = check_settings(["spotify_client_id", "spotify_client_secret", "uri"], request)
    if not status:
        return flask.abort(400)

    return flask.jsonify({'name': sh.get_playlist_name(
        playlist_uri=data["uri"], 
        client_id=data["spotify_client_id"],
        client_secret=data["spotify_client_secret"],
        redirect_uri=SPOTIFY_CLIENT_REDIRECT_URI,
        headless=True
    )})
    

@app.route('/play', methods=['POST'])
def play():
    status, data = check_settings(["spotify_client_id", "spotify_client_secret", "uri"], request)
    if not status:
        return flask.abort(400)

    if not sh.play_playlist(
        playlist_uri=data["uri"],
        shuffle=True, 
        client_id=data["spotify_client_id"],
        client_secret=data["spotify_client_secret"],
        redirect_uri=SPOTIFY_CLIENT_REDIRECT_URI
    ):
        return flask.abort(500)
    return flask.jsonify([])


@app.route('/pause', methods=['POST'])
def pause():
    status, data = check_settings(["spotify_client_id", "spotify_client_secret"], request)
    if not status:
        return flask.abort(400)

    if not sh.pause(
        client_id=data["spotify_client_id"],
        client_secret=data["spotify_client_secret"],
        redirect_uri=SPOTIFY_CLIENT_REDIRECT_URI
    ):
        return flask.abort(500)
    return flask.jsonify([])
    

if __name__ == '__main__':
    # Use the same logger as flask for simplicity's sake
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)

    # Logging formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    # STDOUT logger. Add to both program logger and flask logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler logger. Add to both program logger and flask logger
    fh = logging.FileHandler(LOGFILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = SpotifyHandler(logger)

    app.run(debug=True, use_reloader=False, host='localhost', port=2000)
