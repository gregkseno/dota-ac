from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import json
import pandas as pd
import time

from game_classes import Game, Map, Hero
import game_info


class GSIServer(HTTPServer):
    def __init__(self, server_address):
        super(GSIServer, self).__init__(server_address, RequestHandler)
        self.game = Game()
        self.parser = game_info.GameJSONParser()

        self.running = False

    def start_server(self):
        try:
            thread = Thread(target=self.serve_forever)
            thread.start()
            if not self.running:
                print("Dota 2 GSI Server starting..")
        except:
            print("Could not start server.")


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length).decode("utf-8")  # read JSON
        game_json = json.loads(body)  # parse JSON
        self.server.parser.parse_game_json(game_json, self.server.game)
        time.sleep(1)

