import json

# JSON Utils
JSON_CONTENT_TYPES = ('application/json', 'text/json', 'text/javascript')


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()

        return super(DateTimeJSONEncoder, self).default(obj)


class JSONDecoder(json.JSONDecoder):
    pass
