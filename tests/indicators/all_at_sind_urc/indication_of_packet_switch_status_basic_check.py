#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0071533.001

import unicorn
import re
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):

        test.log.info("1. Check status of paging coordination.")
        test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,0.*OK.*"))

        test.log.info("2. Activate paging urc.")
        test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",1', ".*SIND: psinfo,1,0.*OK.*"))

        test.log.info("3. Enter pin")
        test.expect(test.dut.dstl_enter_pin())

        test.sleep(15)

        test.log.info("4. Test with URC enabled.")

        if test.dut.dstl_is_umts_supported():
            test.check_UMTS()

        if test.dut.dstl_is_lte_supported():
            test.check_LTE()

        if test.dut.dstl_is_nbiot_supported():
            test.check_NBIOT()

        if test.dut.dstl_is_gsm_supported():
            test.check_GSM()

        test.log.info("Deregister from network")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*", timeout=60))
        # test.dut.at1.send_and_verify("AT")
        # test.dut.at1.wait_for(".*CIEV: psinfo,0.*", 30)
        test.wait_for_workaround(".*CIEV: psinfo,0.*", 30)

        test.log.info("5. Test with URC disabled.")

        test.log.info("Disable urc for paging coordination")
        test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",0', ".*OK.*"))

        test.log.info("Check status of paging coordination")
        test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,.*OK.*"))
        # test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*", timeout=30))

        if test.dut.dstl_is_umts_supported():
            test.check_UMTS(False)

        if test.dut.dstl_is_lte_supported():
            test.check_LTE(False)

        if test.dut.dstl_is_nbiot_supported():
            test.check_NBIOT(False)

        if test.dut.dstl_is_gsm_supported():
            test.check_GSM(False)

        test.log.info("6. Test with automatic register mode")
        test.dut.dstl_register_to_network()
        test.log.info("Check status of paging coordination")
        test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,.*OK.*"))

    def check_GSM(test, enable_urc=True):
        test.log.info("Test under GSM starts.")
        register_result = test.dut.dstl_register_to_gsm()
        test.expect(register_result)
        if register_result:
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", ".*OK.*", timeout=60))
            test.sleep(10)
            test.dut.at1.send_and_verify("AT")
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*", timeout=30))
            # test.dut.at1.send_and_verify("AT")
            if enable_urc:
                # test.expect(test.dut.at1.wait_for(".*CIEV: psinfo,4.*", 30, append=True))
                test.wait_for_workaround(".*CIEV: psinfo,[2|4].*", 30, append=True)
            else:
                test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,[2|4].*OK.*"))
            test.log.info("Test under GSM ends.")
        else:
            test.log.error('register to network fail, please check')

    def check_UMTS(test, enable_urc=True):
        test.log.info("Test under UMTS starts.")
        register_result = test.dut.dstl_register_to_umts()
        test.expect(register_result)
        if register_result:
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", ".*OK.*", timeout=60))
            test.sleep(10)
            test.dut.at1.send_and_verify("AT")
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*", timeout=30))
            # test.dut.at1.send_and_verify("AT")

            if enable_urc:
                # test.expect(test.dut.at1.wait_for(".*CIEV: psinfo,6.*", 30, append=True))
                test.wait_for_workaround(".*CIEV: psinfo,6.*", 30, append=True)
            else:
                test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,6.*OK.*"))
            test.log.info("Test under UMTS ends.")
        else:
            test.log.error('register to network fail, please check')

    def check_LTE(test, enable_urc=True):
        test.log.info("Test under LTE starts.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*", timeout=120))
        register_result = test.dut.dstl_register_to_lte()
        test.expect(register_result)
        if register_result:
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", ".*OK.*", timeout=60))
            test.sleep(10)
            test.dut.at1.send_and_verify("AT")
            test.log.info("Last response: ")
            test.log.info(test.dut.at1.last_response)
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*", timeout=30))

            # test.dut.at1.send_and_verify("AT")
            if enable_urc:
                test.log.info("Last response: ")
                test.log.info(test.dut.at1.last_response)
                # test.expect(test.dut.at1.wait_for(".*CIEV: psinfo,17.*", 30, append=True))
                test.wait_for_workaround(".*CIEV: psinfo,17.*", 30, append=True)
                test.log.info("Last response: ")
                test.log.info(test.dut.at1.last_response)
            else:
                test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,17.*OK.*"))
            test.log.info("Test under LTE ends.")
        else:
            test.log.error('register to network fail, please check')

    def check_NBIOT(test, enable_urc=True):
        test.log.info("Test under NB-IOT starts.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*", timeout=120))
        register_result = test.dut.dstl_register_to_nbiot()
        test.expect(register_result)
        if register_result:
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", ".*OK.*", timeout=60))
            test.sleep(10)
            test.dut.at1.send_and_verify("AT")
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*", timeout=30))
            # test.dut.at1.send_and_verify("AT")

            if enable_urc:
                # test.expect(test.dut.at1.wait_for(".*CIEV: psinfo,19.*", 30, append=True))
                test.wait_for_workaround(".*CIEV: psinfo,19.*", 30, append=True)
            else:
                test.expect(test.dut.at1.send_and_verify('AT^SIND="psinfo",2', ".*SIND: psinfo,0,19.*OK.*"))
            test.log.info("Test under NB-IOT ends.")
        else:
            test.log.error('register to network fail, please check')

    def cleanup(test):
        pass

    def wait_for_workaround(test, expect, timeout, append=True):
        if re.search(expect, test.dut.at1.last_response, flags=re.S):
            test.expect(True)
        else:
            test.expect(test.dut.at1.wait_for(expect, 30, append=True))


if "__main__" == __name__:
    unicorn.main()
