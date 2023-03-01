#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0088238.001

import re
import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.set_autoattach import dstl_disable_ps_autoattach, dstl_enable_ps_autoattach, \
    dstl_check_ps_autoattach_enabled
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_umts


class Test(BaseTest):
    """TC0088238.001    AtCgregBasic3G

    This procedure provides basic tests for the test, write and read command of +CGREG.

    1. Check test read and write commands without PIN (commands should be PIN protected)
    2. Check test read and write commands with PIN (module attach to 3G)
    3. Check invalid parameters of write command
    4. Check functionality for GPRS attach and detach and for de-/re-registration of the module (module attach to 2G)
    4.1. Set appropriate CGREG value and check the settings
    4.2. Attach and detach module to GPRS via AT+CGATT, check CGREG URCs
    4.3. Deregister and register module into the network
    Repeat step 4. for all supported values for parameter <n> of CGREG command
    """

    def setup(test):
        test.urc_timeout = 40
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.log.info("Disable GPRS autoattch")
        dstl_disable_ps_autoattach(test.dut)
        dstl_restart(test.dut)
        test.sleep(3)
        test.expect(not dstl_check_ps_autoattach_enabled(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))

    def run(test):
        test.log.step("1. Check test read and write commands without PIN (commands should be PIN protected)")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", r".*\+CPIN: SIM PIN.*"))
        test.log.step("Check commands")
        test.expect(test.dut.at1.send_and_verify("AT+CGREG=?", r".*\+CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGREG=1", r".*\+CME ERROR: SIM PIN required.*"))

        test.log.step("2. Check test read and write commands with PIN (module attach to 3G)")
        test.expect(dstl_register_to_umts(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CGREG=?", r".*\+CGREG: \((0-2,4)|(0-2)\).*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CGREG: 0,[0|2|4].*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGREG=0", r".*OK.*"))

        test.log.step("3. Check invalid parameters of write command")
        invalid_parameters = ["-1", "3", "5", "1e", "2f", "1A", "2#", "11", "\"2#\"", "\"2\""]
        for value in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify("AT+CGREG={}".format(value), r".*\+CME ERROR.*"))

        test.log.step("4. Check functionality for GPRS attach and detach and for de-/re-registration of the module "
                      "(module attach to 3G)")
        time.sleep(5)
        for param_n in ["0", "1", "2"]:
            test.log.step("Scenario for CGREG={}".format(param_n))
            test.log.step("4.1. Set appropriate CGREG value and check the settings")
            test.expect(test.dut.at1.send_and_verify("AT+CGREG={}".format(param_n), r".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CGREG: {},[0|1|2|4].*OK.*".format(param_n)))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", r".*OK.*"))
            if re.search(r".*\+CGATT: 1.*", test.dut.at1.last_response):
                test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", r".*OK.*"))
            test.log.step("4.2. Attach and detach module to GPRS via AT+CGATT, check CGREG URCs")
            test.expect(
                test.dut.at1.send_and_verify("AT+CGATT=1", r".*OK.*", wait_for=test.wait_cgreg_status(param_n, "1"),
                                             timeout=test.urc_timeout))
            test.search_urc(param_n, "1")
            test.expect(
                test.dut.at1.send_and_verify("AT+CGATT=0", r".*OK.*", wait_for=test.wait_cgreg_status(param_n, "0"),
                                             timeout=test.urc_timeout))
            test.search_urc(param_n, "0")
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CGREG: {},0.*OK.*".format(param_n)))
            test.expect(
                test.dut.at1.send_and_verify("AT+CGATT=1", r".*OK.*", wait_for=test.wait_cgreg_status(param_n, "1"),
                                             timeout=test.urc_timeout))
            test.search_urc(param_n, "1")
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CGREG: {},1.*OK.*".format(param_n)))

            test.log.step("4.3. Deregister and register module into the network")
            test.expect(
                test.dut.at1.send_and_verify("AT+COPS=2", r".*OK.*", wait_for=test.wait_cgreg_status(param_n, "0")))
            test.search_urc(param_n, "0")
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CGREG: {},0.*OK.*".format(param_n)))
            test.expect(dstl_register_to_umts(test.dut))
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", r".*\+CGREG: {},0.*OK.*".format(param_n)))

            test.log.step("Repeat step 4. for all supported values for parameter <n> of CGREG command")


    def cleanup(test):
        dstl_enable_ps_autoattach(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def wait_cgreg_status(self, param_n, stat):
        if param_n == "0":
            return "OK"
        if param_n == "1" or stat == "0":
            return r".*\+CGREG: {}.*".format(stat)
        elif param_n == "2" and stat != "0":
            return r".*\+CGREG: {}.*".format(stat)

    def search_urc(test, param_n, stat):
        if param_n == "0":
            test.sleep(test.urc_timeout)
            test.expect(not re.search(r".*\+CGREG:.*", test.dut.at1.last_response))
        elif param_n == "1" or stat == "0":
            test.expect(re.search(r".*\+CGREG: {}.*".format(stat), test.dut.at1.last_response))
        elif param_n == "2" and stat != "0":
            test.expect(re.search(r".*\+CGREG: {},\".*\",\".*\",(2|4|5|6).*".format(stat), test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
