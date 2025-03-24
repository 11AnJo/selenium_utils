import zipfile
from urllib.parse import urlparse
import uuid

def parse_proxy(proxy_string):
    try:
        if proxy_string.startswith('socks5://'):
            raise Exception('Socks5 proxy not supported')

        if not proxy_string.startswith(('http://', 'https://')):
            proxy_string = 'http://' + proxy_string  # Add dummy scheme for parsing

        parsed = urlparse(proxy_string)

        host = parsed.hostname
        port = parsed.port
        username = parsed.username
        password = parsed.password

        return host, port, username, password
    except Exception as e:
        print(f'Error parsing proxy: {e}')
        raise
        

def get_proxy_plugin(proxy_string):
    """
    Supports formats:
    - http://username:password@host:port
    - http://host:port
    - host:port
    - username:password@host:port
    """

    host, port, username, password = parse_proxy(proxy_string)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 3,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "storage",
            "webRequest",
            "webRequestAuthProvider"
        ],
        "host_permissions": [
            "<all_urls>"
        ],
        "background": {
            "service_worker": "background.js"
        },
        "minimum_chrome_version": "88.0.0"
    }
    """

    background_js = """
    const config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
        }
    };
    
    chrome.proxy.settings.set({ value: config, scope: "regular" }, function () {});
    
    chrome.webRequest.onAuthRequired.addListener(
        function (details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        },
        { urls: ["<all_urls>"] },
        ["blocking"]
    );
    """ % (host, port, username, password)

    pluginfile = f'proxy_auth_plugin_{uuid.uuid4()}.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile


def delete_proxy_plugin(pluginfile):
    import os
    os.remove(pluginfile)