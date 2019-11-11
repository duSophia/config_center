# -*- coding: utf-8 -*-

import datetime
import decimal
import json
from enum import Enum
from functools import wraps

from flask import Response


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, Enum):
            return str(o.value)
        else:
            return super(JSONEncoder, self).default(o)


def response_wrapper(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        resp_obj = func(*args, **kwargs)
        return Response(json.dumps(resp_obj, cls=JSONEncoder), status=200, mimetype='application/json')

    return decorated
