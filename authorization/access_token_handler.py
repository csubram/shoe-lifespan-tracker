import requests
import webbrowser
import http.server
import socketserver
import threading
import os
from datetime import datetime
from authorization.json_utils import *
from authorization.tcp_request_handler import TCPRequestHandler


DOMAIN = 'localhost'
PORT = 8000
CLIENT_INFO_FILE = 'authorization/client_info.json'
TOKENS_OUTPUT_FILE = 'authorization/access_tokens.json'


class AccessTokenHandler():

    def __init__(self):
        self.client_info = read_from_json_file_named(CLIENT_INFO_FILE)

    def _get_authorization_request_url(self, client_id):
        query = 'https://www.strava.com/oauth/authorize'
        params = {
            'client_id': self.client_info['client_id'],
            'redirect_uri': 'http://{0}:{1}'.format(DOMAIN, PORT),
            'response_type': 'code',
            'approval_prompt': 'auto',
            'scope': 'activity:read_all'
        }

        auth_request = requests.Request('GET', query, params=params).prepare()
        return auth_request.url

    def _open_web_browser_to_page(self, url):
        edge_path = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
        webbrowser.register('WindowsDefault', None, webbrowser.BackgroundBrowser(edge_path))
        webbrowser.get('WindowsDefault').open(url)

    def _start_local_server(self):
        my_server = socketserver.TCPServer((DOMAIN, PORT), TCPRequestHandler)
        my_server.handle_request()

    def _request_to_refresh_token(self, refresh_token):
        query = 'https://www.strava.com/oauth/token'
        params = {
            'client_id': self.client_info['client_id'],
            'client_secret': self.client_info['client_secret'],
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(query, params=params)
        return response.json()

    def get_existing_access_token(self):
        with open(TOKENS_OUTPUT_FILE, 'r') as token_file:
            token_dict = json.load(token_file)

        return token_dict['access_token']

    def create_new_access_token(self):
        daemon_localhost_thread = threading.Thread(target=self._start_local_server)
        daemon_localhost_thread.start()

        auth_request_url = self._get_authorization_request_url(
            self.client_info['client_id'])
        self._open_web_browser_to_page(auth_request_url)

    def refresh_existing_access_token(self):
        access_token_info = read_from_json_file_named(TOKENS_OUTPUT_FILE)
        auth_response = self._request_to_refresh_token(access_token_info['refresh_token'])
        write_data_to_json_file(
            data=auth_response, filename=TOKENS_OUTPUT_FILE)

    def acquire_permissions(self):
        if (os.path.exists(TOKENS_OUTPUT_FILE)):
            with open(TOKENS_OUTPUT_FILE, 'r') as token_file:
                token_dict = json.load(token_file)
                token_expiry = token_dict['expires_at']
                
            if (datetime.now().timestamp() > token_expiry):
                print('Tokens already exist, refreshing existing access token.')
                self.refresh_existing_access_token()
        else:
            print('Tokens don\'t exist, creating new tokens')
            self.create_new_access_token()
