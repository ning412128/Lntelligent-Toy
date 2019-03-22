from flask import Flask,request
import json
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from geventwebsocket.websocket import WebSocket

ws_serv = Flask(__name__)

user_socket_dict = {}

@ws_serv.route("/toy/<toy_id>")
def toy(toy_id):
    user_socket = request.environ.get("wsgi.websocket") # type:WebSocket
    if user_socket:
        user_socket_dict[toy_id] = user_socket

    while 1:
        message = user_socket.receive()
        msg_dict = json.loads(message)
        print(msg_dict)
        # {to_user:123,music:2739568486.mp3,from_user:"345"}
        app_socket = user_socket_dict.get(msg_dict.pop("to_user"))
        # msg_dict["from_user"] = app_id
        app_socket.send(json.dumps(msg_dict))


@ws_serv.route("/app/<app_id>")
def app(app_id):
    user_socket = request.environ.get("wsgi.websocket") # type:WebSocket
    if user_socket:
        user_socket_dict[app_id] = user_socket

    while 1:
        message = user_socket.receive()
        msg_dict = json.loads(message)
        print(msg_dict)
        # {to_user:123,music:2739568486.mp3,from_user:"345"}
        toy_socket = user_socket_dict.get(msg_dict.pop("to_user"))
        # msg_dict["from_user"] = app_id
        toy_socket.send(json.dumps(msg_dict))


if __name__ == '__main__':
    http_serv = WSGIServer(("0.0.0.0",8000),ws_serv,handler_class=WebSocketHandler)
    http_serv.serve_forever()