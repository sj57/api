import json
import logging
from urllib import request
from http import HTTPStatus
import os

DISCORD_WEBHOOK = os.environ['DISCORD_WEBHOOK']
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')


def send_discord_message(message, discord_webhook):
    data = {
        'content': message
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'postman'
    }
    data = json.dumps(data)
    data = data.encode()
    req = request.Request(discord_webhook, data, headers, method='POST')
    with request.urlopen(req) as response:
        return response.read(), response.getheaders()


def handler_open_garage(event, context) -> dict:
    try:
        send_discord_message(f'open from aws', DISCORD_WEBHOOK)
        data = {}
        data = json.dumps(data, indent=2)
        return {'statusCode': HTTPStatus.OK, 'body': data, "headers": {"content-type": "application/json"}}
    except Exception as e:
        logging.exception('unexpected error')
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'body': f'unexpected error "{str(e)}"'}
