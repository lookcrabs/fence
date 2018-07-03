#: ``CONFIG_SEARCH_FOLDERS: List(str)``
#: Folders to look in for the *config.yaml for fence
CONFIG_SEARCH_FOLDERS = [
    '/var/www/fence',
    '/etc/gen3/fence'
]

#: ``ACCESS_TOKEN_COOKIE_NAME: str``
#: The name of the browser cookie in which the access token will be stored.
ACCESS_TOKEN_COOKIE_NAME = 'access_token'

#: ``SESSION_COOKIE_NAME: str``
#: The name of the browser cookie in which the session token will be stored.
#: Note that the session token also stores information for the
#: ``flask.session`` in the ``context`` field of the token.
SESSION_COOKIE_NAME = 'fence'

#: ``ACCESS_TOKEN_EXPIRES_IN: int``
#: The number of seconds after an access token is issued until it expires.
ACCESS_TOKEN_EXPIRES_IN = 1200

#: ``REFRESH_TOKEN_EXPIRES_IN: int``
#: The number of seconds after a refresh token is issued until it expires.
REFRESH_TOKEN_EXPIRES_IN = 2592000

#: ``SESSION_TIMEOUT: int``
#: The number of seconds after which a browser session is considered stale.
SESSION_TIMEOUT = 1800

#: ``SESSION_LIFETIME: int``
#: The maximum session lifetime in seconds.
SESSION_LIFETIME = 28800

#: ``GOOGLE_SERVICE_ACCOUNT_KEY_FOR_URL_SIGNING_EXPIRES_IN: int``
#: The number of seconds the user's Google service account key used for
#: url signing will last before being expired/rotated
#: 30 days = 2592000 seconds
GOOGLE_SERVICE_ACCOUNT_KEY_FOR_URL_SIGNING_EXPIRES_IN = 2592000

#: ``GOOGLE_ACCOUNT_ACCESS_EXPIRES_IN: int``
#: The number of seconds after a User's Google account is added to bucket
#: access until it expires.
GOOGLE_ACCOUNT_ACCESS_EXPIRES_IN = 86400

#: ``MAX_PRESIGNED_URL_TTL: int``
#: The number of seconds after a pre-signed url is issued until it expires.
MAX_PRESIGNED_URL_TTL = 3600

#: ``MAX_API_KEY_TTL: int``
#: The number of seconds after an API KEY is issued until it expires.
MAX_API_KEY_TTL = 2592000

#: ``MAX_ACCESS_TOKEN_TTL: int``
#: The number of seconds after an access token is issued until it expires.
MAX_ACCESS_TOKEN_TTL = 3600

AWS_CREDENTIALS = {
    "CRED1": {
        'aws_access_key_id': '',
        'aws_secret_access_key': ''
    },
    "CRED2": {
        'aws_access_key_id': '',
        'aws_secret_access_key': ''
    }
}

ASSUMED_ROLES = {
}

S3_BUCKETS = {
    # 'cdis-presigned-url-test': {
    #     'cred': 'fence-bot',
    #     'type': 'internal'
    # },
    'bucket1': {
        'cred': 'CRED1',
    },
    'bucket2': {
        'cred': 'CRED2',
    },
    'bucket3': {
        'cred': 'CRED1',
    },
    'bucket4': {
        'cred': '*',
    },
    'bucket5': {
        'cred': 'CRED2',
        'role-arn': 'arn:aws:iam::707767160287:role/bucket_reader_writer_to_cdistest-presigned-url_role',
    }
}

# S3_BUCKETS = {
#     "bucket1": "CRED1",
#     "bucket2": "CRED2",
#     "bucket3": "CRED1",
#     "bucket4": "*",
# }

ENABLED_IDENTITY_PROVIDERS = {
    # ID for which of the providers to default to.
    'default': 'google',
    # Information for identity providers.
    'providers': {
        'fence': {
            'name': 'Fence Multi-Tenant OAuth',
        },
        'google': {
            'name': 'Google OAuth',
        },
        'shibboleth': {
            'name': 'NIH Login',
        },
    },
}

SHIBBOLETH_HEADER = 'persistent_id'

OPENID_CONNECT = {
    'google': {
        'client_id': '',
        'client_secret': '',
        'redirect_url': ''
    },
}

GOOGLE_GROUP_PREFIX = 'test'

CIRRUS_CFG = {}
