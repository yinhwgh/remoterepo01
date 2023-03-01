# responsible: kamil.kedron@globallogic.com
# location: Wroclaw
# TC0107322.001 PowerCgmmStress

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary import init
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.auxiliary.devboard import devboard
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.network_service.attach_to_network import attach_to_network
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin

import sys


class Test(BaseTest):
    """Example test: Send AT command
    """

    def setup(test):
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(test.r1.at1.send_and_verify("AT&F", "OK", timeout=10))
        test.expect(test.r1.at1.send_and_verify("AT&W", "OK", timeout=10))
        test.requests_number = 30
        test.correct_dns1 = "8.8.8.8"

        test.log.step("1) Log on to the network")
        test.expect(attach_to_network(test.r1))

        test.log.step("2. Define PDP context.")
        test.connection_setup = dstl_get_connection_setup_object(test.r1)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

    def run(test):
        """
        author kamil.kedron@globallogic.com
        Location: Wroclaw
        """
        test.r1.at2.open()

        for i in range(1000):
            test.log.info('************** Loop {} Starts *************'.format(i + 1))

            test.log.step("Set Error extension")
            test.expect(test.r1.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
            test.log.step("Set Registration URC ")
            test.expect(test.r1.at1.send_and_verify("AT+CEREG=2", ".*OK.*"))
            test.log.step("Set Echo")
            test.expect(test.r1.at1.send_and_verify("ATE1", ".*OK.*"))
            test.log.step("CHECK CGMM")

            if (test.r1.at1.send_and_verify("AT+CGMM", ".*ELS31-J.*OK.*") == False):
                test.log.step("Issue reproduced in loop {}".format(i + 1))
                break
            else:
                test.log.step("1. Define correct based on IPv4: dns1 and dns2 values (eg. Google DNS).")
                test.expect(
                    test.r1.at1.send_and_verify("AT^SICS={},\"dns1\",\"{}\"".format(test.cid, test.correct_dns1)))

                test.log.step(
                    "2. Activate defined context (if applicable - restart the module and enter the PIN earlier).")
                test.expect(test.connection_setup.dstl_activate_internet_connection())

                test.log.step("3. Ping chosen site with 30 repetitions.")
                ip_server_address = "8.8.8.8"
                ping_execution = InternetServiceExecution(test.r1.at1, test.cid)
                t = 0

                while t < 40:
                    test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=test.requests_number))
                    test.log.info('************** {} loops left to the end of pings************'.format(60 - t))
                    test.sleep(10)
                    t += 1

                test.log.step("4. Check GSN")
                test.expect(test.r1.at1.send_and_verify("AT+GSN", ".*OK.*"))

                test.log.step("5. Turn off module using SMSO.")
                test.expect(test.r1.devboard.send_and_verify('mc:ver', 'OK'))
                test.expect(test.r1.at1.send_and_verify('at^smso', 'OK'))
                test.sleep(5)
                test.expect(test.r1.dstl_check_if_module_is_on_via_dev_board() == False)
                test.expect(test.r1.devboard.send_and_verify('MC:VEXT', 'OK'))
                test.expect(test.r1.devboard.send_and_verify('MC:EMERGOFF', '.*0.*OK'))
                test.sleep(10)

                test.log.step("6. Turn on module using McTest.")
                test.expect(test.r1.dstl_turn_on_igt_via_dev_board())

                test.log.step("7. Wait 60 seconds until DUT started, send AT.")
                test.expect(test.r1.at1.wait_for("SYSSTART", timeout=60))
                test.expect(test.r1.at1.send_and_verify("AT", ".*OK.*"))

                test.log.step('8.Insert PIN.')
                test.r1.dstl_enter_pin()
                test.sleep(10)
                test.log.info('************** Loop {} End *************'.format(i + 1))

    def cleanup(test):
        test.r1.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)


if "__main__" == __name__:
    unicorn.main()