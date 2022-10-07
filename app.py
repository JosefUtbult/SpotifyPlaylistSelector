from crypt import methods
import flask
from flask import request
import json
import logging
import spotipy

from spotify_handler import SpotifyHandler

LOGFILE = 'SpotifyPlaylistSelector.log'

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def page():
    try:
        playlists = [{'name': sh.get_playlist_name(uri), 'uri': uri} for uri in settings['playlists']]
        return flask.render_template('page.html', playlists=playlists, darkmode=settings['darkmode'])
    except spotipy.oauth2.SpotifyOauthError as e:
        raise e
    except Exception as e:
        logger.error(e)
        return flask.abort(500)


@app.route('/play', methods=['POST'])
def play():
    if not sh.play_playlist(request.get_json(force=True)['uri'], shuffle=True):
        return flask.abort(500)
    return flask.jsonify([])


@app.route('/pause', methods=['POST'])
def pause():
    if not sh.pause():
        return flask.abort(500)
    return flask.jsonify([])


@app.route('/setcookie', methods = ['POST'])
def setcookie():
    try:
        settings = request.get_json(force=True)

        resp = flask.make_response(flask.jsonify([]))
        resp.set_cookie('settings', settings)

        return resp
    except Exception as e:
        logger.warning(e)
        return flask.abort(400)


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

    
    try:
        with open('settings.json') as file:
            settings = json.load(fp=file)
    except FileNotFoundError:
        print("settings.json does not exist")
        exit(1)
    except json.JSONDecodeError:
        print("Invalid settings file")
        exit(2)
    

    sh = SpotifyHandler(
        logger,
        client_id=settings['spotify_client_id'],
        client_secret=settings['spotify_client_secret'],
        headless=True 
    )

    app.run(debug=True, use_reloader=False, host='localhost', port=2000)
