from urllib.parse import urljoin
from servers.models import Server
import requests
from requests.auth import HTTPBasicAuth


def get_api_request_url(server_api, server_endpoint):
    return urljoin(server_api, server_endpoint)


def api_request_to_server(host, endpoint):
    server = Server.objects.filter(url__contains=host).first()
    if not server:
        print("No server endpoint registered")
        return None

    server_api = server.api_location
    server_user = server.remote_server_user
    server_pass = server.remote_server_pass

    if not server_api or not server_user or not server_pass:
        print("No server api location or credentials")
        return None

    api_request_url = get_api_request_url(server_api, endpoint)

    response = requests.get(
        api_request_url,
        auth=HTTPBasicAuth(server_user, server_pass)
    )

    if response.status_code != 200:
        print("%s - unable to complete request." % (response.status_code))
        return None

    return response.json()
