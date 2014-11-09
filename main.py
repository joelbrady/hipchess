#!/usr/bin/python
import sqlite3
import requests
import base64
import json
import re

from bottle import route, post, get, run, request
from bottle import static_file

from view import render
from model import ChessGame, InvalidMove

BASE_URL = 'http://32d0ef22.ngrok.com/'

MOVE_COMMAND = '/chess move'
RESTART_COMMAND = '/chess restart'
VIEW_COMMAND = '/chess view'
HELP_COMMAND = '/chess help'

db = sqlite3.connect('chess.db')

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@post('/message')
def room():
    request_body = json.loads(request.body.read())
    print request_body

    user_name = request_body['item']['message']['from']['name']
    user_message = request_body['item']['message']['message']
    room_id = str(request_body['item']['room']['id'])

    user_message = re.sub(r'//.*', '', user_message)  # strip comments from messages

    if user_message.startswith(MOVE_COMMAND):
        command = user_message.replace(MOVE_COMMAND + ' ', '')
        try:
            ChessGame(room_id).move(command)
            send_board_image(room_id)
            send_message(user_name + ' moved ' + command + '.<br>' + ChessGame(room_id).turn + ' to move.', room_id)
        except InvalidMove as e:
            send_message('Invalid move: ' + e.value, room_id)

    elif user_message.startswith(RESTART_COMMAND):
        ChessGame(room_id).restart()
        send_board_image(room_id)
        send_message(ChessGame(room_id).turn + ' to move.', room_id)

    elif user_message.startswith(VIEW_COMMAND):
        send_board_image(room_id)
        send_message(ChessGame(room_id).turn + ' to move.', room_id)

    elif user_message.startswith(HELP_COMMAND):
        send_message(
            '<ul>' +
                '<li><pre>/chess help</pre>: This command</li>' +
                '<li><pre>/chess move a1 to h7</pre>: Move the piece at a1 to h7</li>' +
                '<li><pre>/chess restart</pre>: Restart the game</li>' +
            '</ul>' +
            'Repository URL: https://github.com/cyberdash/hipchess'
        , room_id)

def send_board_image(room_id):
    send_message('<img src="' + BASE_URL + 'game/' + room_id + '.png"></img>', room_id)

@post('/installable')
def install():
    install_configuration = request.body.read()
    install_configuration_json = json.loads(install_configuration)

    room_id = install_configuration_json['roomId']
    oauth_id = install_configuration_json['oauthId']
    oauth_secret = install_configuration_json['oauthSecret']

    db.execute('INSERT INTO rooms (room, oauthid, oauthsecret) VALUES (?, ?, ?)', (room_id, oauth_id, oauth_secret))

    db.commit()

@get('/game/<room_id>.png')
def render_game(room_id):
    game = ChessGame(room_id)

    image_path = 'dynamic-images/' + room_id + '.png'

    print 'Saving to ' + image_path
    render(game, image_path)

    return static_file(image_path, root='.')

def send_message(message, room_id):

    token = authorize_by_room(room_id)
    print 'Token : ' + str(token)
    message_params = {
        'message': message,
        'message_format': 'html',
        'color': 'green'
    }

    requests.post(
        'http://api.hipchat.com/v2/room/' + str(room_id) + '/notification?auth_token=' + token,
        json=message_params
    )

def authorize(oauth_id, oauth_secret):
    oauth_params = {
        'grant_type': 'client_credentials',
        'scope': 'admin_room send_notification'
    }

    oauth_headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(str(oauth_id) + ':' + str(oauth_secret))
    }
    webhook_oauth_request = requests.post(
        'http://api.hipchat.com/v2/oauth/token',
        params=oauth_params,
        headers=oauth_headers
    )
    print webhook_oauth_request.json()

    return webhook_oauth_request.json()['access_token']


def authorize_by_room(room_id):
    (_, oauth_id, oauth_secret) = db.execute('SELECT * FROM rooms WHERE room = ?', (room_id,)).fetchone()
    return authorize(oauth_id, oauth_secret)

run(host='localhost', port=3421)