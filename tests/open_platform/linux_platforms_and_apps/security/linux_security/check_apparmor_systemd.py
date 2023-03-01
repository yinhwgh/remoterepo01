# responsible: thomas.hinze@thalesgroup.com
# location: Berlin
'''Check app-armor systemd support

    The intention of this test case is to ensure that the apparmor is
    properly supported and started by systemd.
'''

import re

from core.basetest import BaseTest, RetCode

class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        test.log.info("Check if apparmor service is available")
        test.dut.adb.send_and_receive("systemctl status apparmor")
        test.expect(test.dut.adb.last_retcode == 0)
        if test.test_result == RetCode.FAILED:
            test.log.error(f'adb response: {test.dut.adb.last_response}')
            test.abort("missing apparmor systemd service")


        test.log.info("Check if apparmor service was loaded")
        # Loaded: loaded (/lib/systemd/system/apparmor.service; enabled; vendor preset: enabled)
        regex = re.compile(r'.*Loaded: loaded \(.*/apparmor.service; enabled; vendor preset: enabled\)')
        match = regex.findall(test.dut.adb.last_response)
        test.log.info(f"match: {match}")
        test.expect(len(match) == 1)
        if test.test_result == RetCode.FAILED:
            test.abort(f'apparmor service was not loaded by systemd')


        test.log.info("Check if apparmor service is active")
        # Active: active (exited) since Wed 2021-06-09 10:16:15 UTC; 1h 50min ago
        regex = re.compile(r'.*Active: active \(exited\) since .*; .* ago')
        match = regex.findall(test.dut.adb.last_response)
        test.log.info(f"match: {match}")
        test.expect(len(match) == 1)
        if test.test_result == RetCode.FAILED:
            test.abort(f'apparmor service was not activated by systemd')

        test.log.info("Check if apparmor process has exited successful")
        # Active: active (exited) since Wed 2021-06-09 10:16:15 UTC; 1h 50min ago
        regex = re.compile(r'.*Main PID: .* \(code=exited, status=0/SUCCESS\)')
        match = regex.findall(test.dut.adb.last_response)
        test.log.info(f"match: {match}")
        test.expect(len(match) == 1)
        if test.test_result == RetCode.FAILED:
            test.abort(f'apparmor service did not exited successfully')

    def cleanup(test):
        pass
