# responsible: dariusz.drozdek@globallogic.com, renata.bryla@globallogic.com
# location: Wroclaw
# TC0102353.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """
    TC0102353.001    CemodeBasicFunctionality

    Intention of this TC is to check if modes of EPS (Evolved Packet System) operation works correctly on module.

    1. Check test command cemode (AT+CEMODE=?)
    2. Set 0 EPS mode of operation by write command (AT+CEMODE=0) and restart module
    3. Ping any address via AT^SISX command
    4. Detach module to the network (AT+CGATT=0)
    5. Check cemode value (AT+CEMODE?)
    6. Check test command cemode (AT+CEMODE=?)
    7. Attach module to the network (AT+CGATT=1)
    8. Check cemode value (AT+CEMODE?)
    9. Set 2 EPS mode of operation by write command (AT+CEMODE=2) and restart module
    10. Send SMS in text mode via AT+CMGS command to Remote
    11. Repeat steps: 3-8
    """

    def setup(test):
        for device in [test.dut, test.r1]:
            dstl_detect(device)
            dstl_get_bootloader(device)
            dstl_get_imei(device)
            test.expect(dstl_enter_pin(device))
            test.sleep(5)
            test.expect(dstl_set_preferred_sms_memory(device, "ME"))
            test.expect(dstl_delete_all_sms_messages(device))
            test.expect(device.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
            test.expect(dstl_set_scfg_urc_dst_ifc(device))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=1,\"IP\",\"{}\"".format(test.dut.sim.apn_v4), ".*OK.*"))
        pass

    def run(test):
        cemode_cmd_with_write = True
        cemode_test_resp = r".*[+]CEMODE: \(0,2\)[\n\r].*OK.*"

        if test.dut.project is 'VIPER':
            cemode_test_resp = r".*[+]CEMODE: \(0-3\)[\n\r].*OK.*"
            cemode_cmd_with_write = False

        elif test.dut.project is 'SERVAL':
            cemode_test_resp = r".*[+]CEMODE: \(0,2\)[\n\r].*OK.*"
            cemode_cmd_with_write = True

        elif test.dut.project is 'BOBCAT' and test.dut.step is '2':
            cemode_test_resp = r".*[+]CEMODE: \(0-3\)[\n\r].*OK.*"
            cemode_cmd_with_write = True

        project = test.dut.project.capitalize()
        test.log.step("For {} product TC should be proceed according to steps listed below. ".format(project))
        test.log.step("1. Check test command cemode (AT+CEMODE=?)")
        test.expect(test.dut.at1.send_and_verify("AT+CEMODE=?", cemode_test_resp))

        if not cemode_cmd_with_write:
            test.log.step("2. try to perform write command - not available in this product")
            test.expect(test.dut.at1.send_and_verify("AT+CEMODE=0", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CEMODE=1", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CEMODE=2", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CEMODE=3", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CEMODE=4", ".*ERROR.*"))

        else:
            test.log.step("2. Set 0 EPS mode of operation by write command (AT+CEMODE=0) and restart module")
            test.expect(test.dut.at1.send_and_verify("AT+CEMODE=0", ".*OK.*"))
            test.expect(dstl_restart(test.dut))
            test.connection_setup = dstl_get_connection_setup_object(test.dut)
            test.ping_execution = InternetServiceExecution(test.dut, test.connection_setup.dstl_get_used_cid())

            for mode in ["0", "2"]:
                test.expect(dstl_register_to_network(test.dut))
                test.sleep(5)
                test.log.step("3. Ping any address via AT^SISX command")
                test.expect(test.connection_setup.dstl_activate_internet_connection())
                test.expect(test.ping_execution.dstl_execute_ping("8.8.8.8", 30, 5000))
                test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= 30*0.2)

                test.log.step("4. Detach module to the network (AT+CGATT=0)")
                test.expect(test.connection_setup.dstl_detach_from_packet_domain())

                test.log.step("5. Check cemode value (AT+CEMODE?)")
                test.expect(test.dut.at1.send_and_verify("AT+CEMODE?", r"[+]CEMODE: {}[\n\r].*OK.*".format(mode)))

                test.log.step("6. Check test command cemode (AT+CEMODE=?)")
                test.expect(test.dut.at1.send_and_verify("AT+CEMODE=?", r".*[+]CEMODE: \(0,2\)[\n\r].*OK.*"))

                test.log.step("7. Attach module to the network (AT+CGATT=1)")
                test.sleep(10)
                test.expect(test.connection_setup.dstl_attach_to_packet_domain())

                test.log.step("8. Check cemode value (AT+CEMODE?)")
                test.expect(test.dut.at1.send_and_verify("AT+CEMODE?", r".*[+]CEMODE: {}[\n\r].*OK.*".format(mode)))
                if mode == "0":
                    test.log.step("9. Set 2 EPS mode of operation by write command (AT+CEMODE=2) and restart module")
                    test.expect(test.dut.at1.send_and_verify("AT+CEMODE=2", ".*OK.*"))
                    test.expect(dstl_restart(test.dut))
                    test.expect(dstl_register_to_network(test.dut))
                    test.sleep(5)

                    test.log.step("10. Send SMS in text mode via AT+CMGS command to Remote")
                    test.expect(dstl_register_to_network(test.r1))
                    test.expect(dstl_select_sms_message_format(test.r1))
                    test.expect(test.r1.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
                    msg = "SMS to remote"
                    test.expect(dstl_send_sms_message(test.dut, test.r1.sim.int_voice_nr, msg))
                    test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=180))
                    sms_index = re.search(r".*\",\s*(\d{1,3})", test.r1.at1.last_response)
                    if sms_index:
                        test.expect(test.r1.at1.send_and_verify("AT+CMGR={}".format(sms_index.group(1)),
                                                                ".*{}.*{}.*OK.*".format(test.dut.sim.nat_voice_nr[-9:],
                                                                                        msg)))
                    else:
                        test.expect(False, msg="Module does not receive SMS in required timeout")
                    test.log.step("11. Repeat steps: 3-8")
        pass

    def cleanup(test):
        dstl_delete_all_sms_messages(test.r1)
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")
        pass


if "__main__" == __name__:
    unicorn.main()
