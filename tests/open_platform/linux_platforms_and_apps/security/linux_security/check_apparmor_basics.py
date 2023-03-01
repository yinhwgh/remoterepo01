# responsible: thomas.hinze@thalesgroup.com
# location: Berlin
'''Check app-armor basics

    The intention of this test case is to ensure that the apparmor is
    available from user space and that is was started properly.
'''

from core.basetest import BaseTest, RetCode

class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        dut_cache_dir='/etc/apparmor.d/cache' # might differ on products

        test.log.info("Check if sysfs directory for apparmor exists")
        test.dut.adb.send_and_receive("[ -d /sys/module/apparmor ]")
        test.expect(test.dut.adb.last_retcode == 0)


        test.log.info("Check if apparmor is enabled")
        test.dut.adb.send_and_receive("cat /sys/module/apparmor/parameters/enabled")
        test.expect(test.dut.adb.last_retcode == 0)

        adb_rsp_lines = split_adb_response(test.dut.adb.last_response)
        test.expect(lines(adb_rsp_lines) == 1)
        if test.test_result == RetCode.FAILED:
            test.log.error(f'adb response: {test.dut.adb.last_response}')

        test.expect(adb_rsp_lines[0] == "Y")
        if test.test_result == RetCode.FAILED:
            test.log.error(f'adb response: {test.dut.adb.last_response}')

        test.log.info("Check if cache directory for apparmor exists")
        test.dut.adb.send_and_receive(f"[ -d {dut_cache_dir} ]")
        test.expect(test.dut.adb.last_retcode == 0)


        # if apparmor was properly started then there should be some cached data
        test.log.info("Check if apparmor was started (by cache dir)")
        test.dut.adb.send_and_receive(f"ls {dut_cache_dir}/*")
        test.expect(test.dut.adb.last_retcode == 0)
        if test.test_result == RetCode.FAILED:
            test.log.warning(f'adb response: {test.dut.adb.last_response}')

        adb_rsp_lines = split_adb_response(test.dut.adb.last_response)
        cache_files = list(map(lambda text: text.strip(), " ".join(adb_rsp_lines).split(' ')))

        test.expect(len(cache_files) > 0)
        test.log.info(f"cache_files: {cache_files}")

    def cleanup(test):
        pass

def lines( text: list):
    return len(text)

def split_adb_response(adb_response, keep_empty_lines=False):
        lines = list(adb_response.split("\n"))
        # remove '\r'
        lines = list(map(lambda i: i.rstrip(), lines))
        # filter empty lines
        if keep_empty_lines is False:
            lines = list(filter(lambda i: i != '', lines))

        return lines
