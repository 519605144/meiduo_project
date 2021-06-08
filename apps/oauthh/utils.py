from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_project import settings

def generate_access_token(openid):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    data = {
        'openid': openid,
    }

    token = s.dumps(data)

    return token.decode()

def get_access_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    data = s.loads(token)

    result = data.get('openid')
    return result
