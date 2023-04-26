from authorization.json_utils import *
import requests
import socketserver


CLIENT_INFO_FILE = 'authorization/client_info.json'
TOKENS_OUTPUT_FILE = 'authorization/access_tokens.json'


class TCPRequestHandler(socketserver.StreamRequestHandler):

    def _get_auth_code_from_msg(self, msg):
        auth_code_query_parameter = msg.decode().split('&')[1]
        auth_code = auth_code_query_parameter.split('=')[1]
        return auth_code

    def _post_authorization_code(self, client_info, auth_code):
        query = 'https://www.strava.com/oauth/token'
        params = {
            'client_id': client_info['client_id'],
            'client_secret': client_info['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code'
        }

        response = requests.post(query, params=params)
        return response.json()

    def handle(self):
        msg = self.rfile.readline().strip()
        auth_code = self._get_auth_code_from_msg(msg)
        client_info = read_from_json_file_named(CLIENT_INFO_FILE)

        auth_response = self._post_authorization_code(client_info, auth_code)
        write_data_to_json_file(
            data=auth_response, filename=TOKENS_OUTPUT_FILE)
