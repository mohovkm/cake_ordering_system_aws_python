import json
from pydantic import ValidationError
from functools import wraps
import base64


def response_builder(status_code: int, message: dict):
    """Response builder
    """
    return {
        'statusCode': status_code,
        'body': json.dumps(message)
    }


def validate_http_request(validation_model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            event = args[0]

            # Validating input data
            try:
                validation_model(**event)
            except ValidationError as e:
                detail = {
                    'detail': f'Validation error: [{str(e)}]'
                }
                return response_builder(400, detail)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def parse_kinesis_payload(record: dict):
    """Decoding base64 kinesis payload
    """
    payload = record.get('kinesis', {}).get('data', '')

    payload = base64.b64decode(payload).decode('utf-8')

    payload = json.loads(payload)

    return payload



