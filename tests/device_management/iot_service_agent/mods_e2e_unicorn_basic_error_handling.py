# responsible: johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-95

import unicorn
import requests
from requests.auth import HTTPBasicAuth
import json
import tests.device_management.iot_service_agent.mods_e2e_unicorn_server_config as server_config
from core.basetest import BaseTest
import sys
from dstl.auxiliary import init
from dstl.auxiliary.write_json_result_file import *

testkey = "UNISIM01-95"

class Test(BaseTest):
    """
    Class to test the response of misconfigured requests sent to the MODS server.
    Tested operations: authentication/connection/URL error cases
    """
    auth = HTTPBasicAuth(server_config.USER, server_config.PASSWORD)
    wrong_auth = HTTPBasicAuth('invalidUser', 'invalidPassword')

    headers = {
        'Accept': 'application/json'
    }

    wrong_headers = {
        'Accept': 'nothing'
    }

    proxies = server_config.PROXIES
    wrong_proxies = {
        'http': '1.1.1.1:3128',
        'https': '1.1.1.1:3128',
    }

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.dut.dstl_detect()
        pass

    def run(test):
        # case 1: authentication OK, invalid URL => status_code 404
        test.log.info(
            f'{40 * "*"} Case 1: authentication OK, invalid URL => status_code 404 {40 * "*"}')
        url = server_config.DEVICE_API + "_invalidURL"
        r = requests.get(url, verify=False, headers=test.headers, auth=test.auth,
                         proxies=test.proxies)

        test.log.info(f'{r.request.method} {url}')
        test.log.info(f'URL access status: {r.status_code}')
        test.expect(r.status_code == 404)

        # case 2: authentication wrong => status_code 401
        test.log.info(f'{40 * "*"} Case 2: authentication wrong => status_code 401 {40 * "*"}')
        url = server_config.DEVICE_API
        r = requests.get(url, verify=False, headers=test.headers, auth=test.wrong_auth,
                         proxies=test.proxies)

        test.log.info(f'{r.request.method} {url}')
        test.log.info(f'URL access status: {r.status_code}')
        test.expect(r.status_code == 401)

        # case 3: wrong header -> status_code 406
        test.log.info(f'{40 * "*"} Case 3: wrong header -> status_code 406 {40 * "*"}')
        url = server_config.DEVICE_API
        r = requests.get(url, verify=False, headers=test.wrong_headers, auth=test.auth,
                         proxies=test.proxies)
        test.log.info(f'{r.request.method} {url}')
        test.log.info(f'URL access status: {r.status_code}')
        test.expect(r.status_code == 406)

        # case 4: wrong proxy settings -> ProxyError exception
        test.log.info(f'{40 * "*"} Case 4: wrong proxy settings -> ProxyError exception {40 * "*"}')
        url = server_config.DEVICE_API
        try:
            r = requests.get(url, verify=False, headers=test.headers, auth=test.auth,
                             proxies=test.wrong_proxies)
        except requests.exceptions.ProxyError as e:
            test.log.info(f'{e}')
            test.log.info(f'URL access status: {r.status_code}')
            test.expect(r.status_code == 406)
            test.expect(True)
        else:
            test.log.info("Unexpected exception:", sys.exc_info()[0])
            test.expect(False)

    def cleanup(test):

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
