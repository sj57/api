import json
import logging
from functools import wraps
from urllib import request
from http import HTTPStatus
import os

DISCORD_WEBHOOK = os.environ['DISCORD_WEBHOOK']
API_KEY = os.environ['API_KEY']
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


def validate_api_token():
    def decorator(f):
        @wraps(f)
        def decorated_function(event, context):
            response_headers = {
                "content-type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE,HEAD"
            }
            try:
                api_token = event['headers'].get('Authorization')
                is_valid_api_token = not api_token or api_token != API_KEY
                if is_valid_api_token:
                    return {'statusCode': HTTPStatus.UNAUTHORIZED, 'body': json.dumps({"error": 'invalid token'}), "headers": response_headers}

                data = f(event, context)
                data = json.dumps(data)
                return {'statusCode': HTTPStatus.OK, 'body': data, "headers": response_headers}
            except:
                logging.exception('unexpected error')
                return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'body': json.dumps({"error": 'unexpected error'}), "headers": response_headers}

        return decorated_function

    return decorator


@validate_api_token()
def handler_open_garage(event, context) -> dict:
    send_discord_message(f'open from aws', DISCORD_WEBHOOK)
    return {}
