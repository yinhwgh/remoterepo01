# Server credentials and api urls.

# Unicorn organization on staging server
USER = 'nz5njbbM9akfYUc3YA2B'
PASSWORD = 'pWuUsML9aFpYOl0PLzJQhEcOXtcQJ7Gzc06sVt$R'

# UnicornDEV organization on Development server
#USER = 'WAyIIWYzezOf9qV9cDny'
#PASSWORD = 'MNy2EVur0H4eq3usSifHxmagsoDZm3PPYYz$tifS'


# Elisa organization
#USER = 'S1gwCNuGcuowkI2xU4Hl'
#PASSWORD = '1sefCLKpRdaBjpU8h083a4WeLtLR3k9vLtnqwmvW'

VERIFY_CERT = True

PROXIES = {
    'http': '10.50.101.10:3128',
    'https': '10.50.101.10:3128',
}

# URL for staging server:
# BASE_URL = 'https://partners-mods.gemalto.io'
# since 10.09.2021
BASE_URL = 'https://partners.iot-suite.thalescloud.io'
# URL for development server:
#BASE_URL = 'https://mods.modsng.ew1.msi-dev03.acloud.gemalto.com'
# URL for production server:
#BASE_URL = 'https://iot-suite.thalescloud.io'

DEVICE_API = f'{BASE_URL}/api/v1/devices'
JOB_API = f'{BASE_URL}/api/v1/jobs'
CONNECTIVITY_API = f'{BASE_URL}/api/v1/connectivity'
RULES_API = f'{BASE_URL}/api/v1/connectivity/rules'
SUBSCRIPTIONS_API = f'{BASE_URL}/api/v1/connectivity/subscriptions'
APN_PROFILES_API = f'{BASE_URL}/api/v1/connectivity/apnProfiles'
PACKAGE_MANAGEMENT_API = f'{BASE_URL}/api/v1/packages/firmwares'
