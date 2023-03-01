#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0094560.002

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0094560.002    Sind_newSMS_stdCommands
    To check with SIND command the indicator newsms output while receiving SMS.

    Precondition:
    2 modules connected to network (DUT and REMOTE)
    2 interfaces connected between DUT and PC (eg. ASC0 + USB)
    Standard 3GPP commands used for tests (eg. at+cmgs, at+cmgr etc.)

    Description:
    2 interfaces of one DUT are being tested in parallel (eg. ASC0 + USB).
    Scenarios:
    1. Delete all messages from memory on both DUTs
    2. On DUT set at^sind="newsms",0 on 1st interface
    3. Receive 1st SMS from Remote (check if any URC was received)
    4. On DUT set at^sind="newsms",1 on 1st interface
    5. Receive 2nd and 3rd SMSs from Remote (check on which interface URCs were received)
    6. On DUT set at^sind="newsms",1 on 2nd interface
    7. Receive 4th and 5th SMSs from Remote (check on which interface URCs were received)
    8. On DUT set at^sind="newsms",0 on 1st interface
    9. On DUT set once again at^sind="newsms",1 on 2nd interface
    10. Receive 6th and 7th SMSs from Remote (check on which interface URCs were received)
    11. On DUT set at^sind="newsms",1 on 1st interface
    12. Receive 8th SMS from Remote (check on which interface URC was received)
    13. On DUT set at^sind="newsms",0 on both interfaces
    14. Receive 9th and 10th SMSs from Remote (check if any URC was received)
    15. Delete all messages from memory
    16. On DUT set at^sind="newsms",1 on 1st interface
    17. Receive 11th SMS from Remote (check on which interface URC was received)
    18. On DUT set at^sind="newsms",1 on 2nd interface
    19. Receive 12th SMS from Remote (check on which interface URC was received)
    20. On DUT set at^sind="newsms",0 on 1st interface
    21. Receive 13th SMS from Remote (check if any URC was received)
    """

    mode_enable = 1
    mode_disable = 0
    time_value_in_sec = 5

    def setup(test):
        test.prepare_module(test.dut, "===== Start preparation for DUT module =====")
        test.prepare_module(test.r1, "===== Start preparation for REMOTE module =====")

    def run(test):
        test.log.h2("Starting TC0094560.002 Sind_newSMS_stdCommands")
        test.log.step("Step 1. Delete all messages from memory on both DUTs")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.r1))

        test.log.step("Step 2. On DUT set at^sind=\"newsms\",0 on 1st interface")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_disable)

        test.log.step("Step 3. Receive 1st SMS from Remote (check if any URC was received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_disable}]
        test.execute_step(data_dict, "SMS 1st step 3")

        test.log.step("Step 4. On DUT set at^sind=\"newsms\",1 on 1st interface")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_enable)

        test.log.step("Step 5. Receive 2nd and 3rd SMSs from Remote (check on which interface URCs were received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_enable}]
        test.execute_step(data_dict, "SMS 2nd step 5")
        test.execute_step(data_dict, "SMS 3rd step 5")

        test.log.step("Step 6. On DUT set at^sind=\"newsms\",1 on 2nd interface")
        test.set_and_check_sind_newsms_command(test.dut.at2, test.mode_enable)

        test.log.step("Step 7. Receive 4th and 5th SMSs from Remote (check on which interface URCs were received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_enable},
                     {"interface": test.dut.at2, "mode": test.mode_enable}]
        test.execute_step(data_dict, "SMS 4th step 7")
        test.execute_step(data_dict, "SMS 5th step 7")

        test.log.step("Step 8. On DUT set at^sind=\"newsms\",0 on 1st interface")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_disable)

        test.log.step("Step 9. On DUT set once again at^sind=\"newsms\",1 on 2nd interface")
        test.set_and_check_sind_newsms_command(test.dut.at2, test.mode_enable)

        test.log.step("Step 10. Receive 6th and 7th SMSs from Remote (check on which interface URCs were received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_disable},
                     {"interface": test.dut.at2, "mode": test.mode_enable}]
        test.execute_step(data_dict, "SMS 6th step 10")
        test.execute_step(data_dict, "SMS 7th step 10")

        test.log.step("Step 11. On DUT set at^sind=\"newsms\",1 on 1st interface")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_enable)

        test.log.step("Step 12. Receive 8th SMS from Remote (check on which interface URC was received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_enable},
                     {"interface": test.dut.at2, "mode": test.mode_enable}]
        test.execute_step(data_dict, "SMS 8th step 12")

        test.log.step("Step 13. On DUT set at^sind=\"newsms\",0 on both interfaces")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_disable)
        test.set_and_check_sind_newsms_command(test.dut.at2, test.mode_disable)

        test.log.step("Step 14. Receive 9th and 10th SMSs from Remote (check if any URC was received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_disable},
                     {"interface": test.dut.at2, "mode": test.mode_disable}]
        test.execute_step(data_dict, "SMS 9th step 14")
        test.execute_step(data_dict, "SMS 10th step 14")

        test.log.step("Step 15. Delete all messages from memory")
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step("Step 16. On DUT set at^sind=\"newsms\",1 on 1st interface")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_enable)

        test.log.step("Step 17. Receive 11th SMS from Remote (check on which interface URC was received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_enable},
                     {"interface": test.dut.at2, "mode": test.mode_disable}]
        test.execute_step(data_dict, "SMS 11th step 17")

        test.log.step("Step 18. On DUT set at^sind=\"newsms\",1 on 2nd interface")
        test.set_and_check_sind_newsms_command(test.dut.at2, test.mode_enable)

        test.log.step("Step 19. Receive 12th SMS from Remote (check on which interface URC was received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_enable},
                     {"interface": test.dut.at2, "mode": test.mode_enable}]
        test.execute_step(data_dict, "SMS 12th step 19")

        test.log.step("Step 20. On DUT set at^sind=\"newsms\",0 on 1st interface")
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_disable)

        test.log.step("Step 21. Receive 13th SMS from Remote (check if any URC was received)")
        data_dict = [{"interface": test.dut.at1, "mode": test.mode_disable},
                     {"interface": test.dut.at2, "mode": test.mode_enable}]
        test.execute_step(data_dict, "SMS 13th step 21")

    def cleanup(test):
        test.set_and_check_sind_newsms_command(test.dut.at1, test.mode_disable)
        test.set_and_check_sind_newsms_command(test.dut.at2, test.mode_disable)
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module(test, module, text):
        test.log.info(text)
        test.expect(module.at1.send_and_verify("ATE1", "OK"))
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))

    def set_and_check_sind_newsms_command(test, interface, mode):
        test.expect(interface.send_and_verify("at^sind=\"newsms\",{}".format(mode),
                                              ".*SIND: newsms,{}.*OK.*".format(mode)))
        test.expect(interface.send_and_verify("at^sind=\"newsms\",2", ".*SIND: newsms,{}.*OK.*".format(mode)))

    def check_cmti_urc(test):
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=360))
        sms_received = re.search(r"CMTI:\s*\"ME\",\s*(\d{1,3})", test.dut.at1.last_response)
        if sms_received:
            test.expect(True, msg="===== Message received correctly =====")
            return sms_received[1]
        else:
            return test.expect(False, msg="===== Message was not received =====")

    def check_ciev_urc(test, interface, mode, index):
        if interface == test.dut.at1:
            interface_name = "1st"
        else:
            interface_name = "2nd"
        if mode == test.mode_enable:
            test.log.info("===== Check CIEV URC on {} interface - Expected SEARCH CIEV =====".format(interface_name))
            test.expect(interface.wait_for(".*CIEV: newsms,\"3gpp\",\"ME\",{}.*".format(index),
                                           timeout=test.time_value_in_sec, append=True))
        else:
            test.log.info("===== Check CIEV URC on {} interface - Expected NOT SEARCH CIEV =====".format(interface_name))
            test.expect(test.check_no_urc(interface, ".*CIEV: newsms,\"3gpp\",\"ME\",{}.*".format(index)))

    def check_no_urc(test, interface, urc):
        test.wait(test.time_value_in_sec)
        interface.read(append=True)
        if re.search(urc, interface.last_response):
            test.log.error(f"URC {urc} occurred, Test Failed")
            return False
        else:
            test.log.info(f"URC {urc} NOT occurred, Test Passed")
            return True

    def execute_step(test, data_dict, text):
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, text))
        sms_index = test.check_cmti_urc()
        for item in data_dict:
            test.check_ciev_urc(item["interface"], item["mode"], sms_index)
        test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index), ".*[\n\r]{}.*OK.*".format(text)))


if "__main__" == __name__:
    unicorn.main()