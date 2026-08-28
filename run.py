import socket

# Force socket to resolve ONLY IPv4 (AF_INET) addresses on Render
_orig_getaddrinfo = socket.getaddrinfo

def _getaddrinfo_ipv4_only(*args, **kwargs):
    responses = _orig_getaddrinfo(*args, **kwargs)
    ipv4_responses = [res for res in responses if res[0] == socket.AF_INET]
    return ipv4_responses if ipv4_responses else responses

socket.getaddrinfo = _getaddrinfo_ipv4_only
import os
from app import create_app

env_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(env_name)

if __name__ == '__main__':
    app.run()
