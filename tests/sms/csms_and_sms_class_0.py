#responsible: pawel.habrych@globallogic.com
#location: Wroclaw
#TC0102251.001, TC0102251.002

import unicorn
import re
import time

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory

class Test(BaseTest):
    """
    Check if module behavior is correct despite AT+CSMS setting when Class 0 message is received.
    Test will check scenarios with PDU mode and Text mode
    Test config: at+cnmi=<mode=all supported>,<mt=1>
    Based on: IPIS100204981

    1. Set Text mode on both modules.
    2. Set AT+CSMS=0 on both modules
    3. On DUT set AT+CNMI=0,1,0,0 and enable +CIEV: message,1 URCs if supported (eg. AT^SIND="message",1).
    4. On Remote set Class0 SMS: AT+CSMP=17,167,0,16 or  AT+CSMP=17,167,0,240
    5. Send message from Remote to DUT.
    6. Wait ~1 minute for message to come. For AT+CNMI=0,1,0,0 no +CMT or +CMTI URC should be displayed.
    For other <mode> values only +CMT should be displayed.
    7. Check memory - there should be no received messages
    8. Check AT+CNMI? - values shouldn't be changed. Delete all saved messages.
    9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1
    10. Repeat steps 1-9, but this time set AT+CSMS=1 in step 2
    11. Repeat steps 1-10 in PDU mode.
    """

    TIME_WAIT_IN_SECONDS = 60
    OK_RESPONSE = ".*OK.*"
    AT_CSMP = "AT+CSMP=17,167,0,{}"
    AT_CNMI = "AT+CNMI={},{},0,0"
    AT_CSMS = "AT+CSMS={}"
    CMT_URC = ".*CMT.*"

    def setup(test):
        test.get_information(test.dut)
        test.get_information(test.r1)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        if test.dut.project.upper() != "VIPER":
            test.log.info('Set AT^SCFG=Sms/AutoAck,0 - AutoAck OFF')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sms/AutoAck","0"', test.OK_RESPONSE))

    def run(test):
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step('1. Set Text mode on both modules.')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step('2. Set AT+CSMS=0 on both modules')
        test.expect(test.dut.at1.send_and_verify(test.AT_CSMS.format("0"), test.OK_RESPONSE))
        test.expect(test.r1.at1.send_and_verify(test.AT_CSMS.format("0"), test.OK_RESPONSE))

        test.log.info('========== Text Mode ==========')
        test.log.info('===== AT+CSMS=0 + AT+CNMI=0,1,0,0 =====')
        test.steps_3_to_8(0)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== Text Mode ==========')
        test.log.info('===== AT+CSMS=0 + AT+CNMI=1,1,0,0 =====')
        test.steps_3_to_8(1)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== Text Mode ==========')
        test.log.info('===== AT+CSMS=0 + AT+CNMI=2,1,0,0 =====')
        test.steps_3_to_8(2)

        test.log.step('10. Repeat steps 1-9, but this time set AT+CSMS=1 in step 2')
        test.log.step('1. Set Text mode on both modules.')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step('2. Set AT+CSMS=1 on both modules')
        test.expect(test.dut.at1.send_and_verify(test.AT_CSMS.format("1"), test.OK_RESPONSE))
        test.expect(test.r1.at1.send_and_verify(test.AT_CSMS.format("1"), test.OK_RESPONSE))

        test.log.info('========== Text Mode ==========')
        test.log.info('===== AT+CSMS=1 + AT+CNMI=0,1,0,0 =====')
        test.steps_3_to_8(0)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== Text Mode ==========')
        test.log.info('===== AT+CSMS=1 + AT+CNMI=1,1,0,0 =====')
        test.steps_3_to_8(1)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== Text Mode ==========')
        test.log.info('===== AT+CSMS=1 + AT+CNMI=2,1,0,0 =====')
        test.steps_3_to_8(2)

        test.log.step('11. Repeat steps 1-10 in PDU mode.')
        test.log.step('1. Set PDU mode on DUT.')
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=0', test.OK_RESPONSE))

        test.log.step('2. Set AT+CSMS=0 on both modules')
        test.expect(test.dut.at1.send_and_verify(test.AT_CSMS.format("0"), test.OK_RESPONSE))
        test.expect(test.r1.at1.send_and_verify(test.AT_CSMS.format("0"), test.OK_RESPONSE))

        test.log.info('========== PDU Mode ==========')
        test.log.info('===== AT+CSMS=0 + AT+CNMI=0,1,0,0 =====')
        test.steps_3_to_8(0)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== PDU Mode ==========')
        test.log.info('===== AT+CSMS=0 + AT+CNMI=1,1,0,0 =====')
        test.steps_3_to_8(1)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== PDU Mode ==========')
        test.log.info('===== AT+CSMS=0 + AT+CNMI=2,1,0,0 =====')
        test.steps_3_to_8(2)

        test.log.step('10. Repeat steps 1-9, but this time set AT+CSMS=1 in step 2')
        test.log.step('1. Set PDU mode on DUT.')
        test.expect(dstl_select_sms_message_format(test.dut, "PDU"))

        test.log.step('2. Set AT+CSMS=1 on both modules')
        test.expect(test.dut.at1.send_and_verify(test.AT_CSMS.format("1"), test.OK_RESPONSE))
        test.expect(test.r1.at1.send_and_verify(test.AT_CSMS.format("1"), test.OK_RESPONSE))

        test.log.info('========== PDU Mode ==========')
        test.log.info('===== AT+CSMS=1 + AT+CNMI=0,1,0,0 =====')
        test.steps_3_to_8(0)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== PDU Mode ==========')
        test.log.info('===== AT+CSMS=1 + AT+CNMI=1,1,0,0 =====')
        test.steps_3_to_8(1)

        test.log.step('9. Repeat steps 3-8 with AT+CNMI=<all supported modes>,1')
        test.log.info('========== PDU Mode ==========')
        test.log.info('===== AT+CSMS=1 + AT+CNMI=2,1,0,0 =====')
        test.steps_3_to_8(2)

    def cleanup(test):
        test.clean_after_test(test.dut)
        test.clean_after_test(test.r1)

    def steps_3_to_8(test, mode):
        test.log.step('3. On DUT set AT+CNMI=' + str(mode) + ',1,0,0 and enable +CIEV: message,1 '
                                                           'URCs if supported (eg. AT^SIND="message",1).')
        test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format(str(mode), '1'), test.OK_RESPONSE))

        test.log.step('4. On Remote set Class0 SMS: AT+CSMP=17,167,0,16 or AT+CSMP=17,167,0,240')
        test.expect(test.r1.at1.send_and_verify(test.AT_CSMP.format('16'), test.OK_RESPONSE))

        test.log.step('5. Send message from Remote to DUT.')
        test.check_dut_memory()
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "Test from Remote 1 - Step5"))

        test.log.step('6. Wait ~1 minute for message to come. For AT+CNMI=0,1,0,0 no +CMT or +CMTI '
                      'URC should be displayed. For other <mode> values only +CMT should be displayed.')
        if mode == 0:
            test.log.info("Waiting 60.00 seconds for no URC response: +CMT, +CMTI")
            test.expect(test.check_no_urc(test.CMT_URC, test.TIME_WAIT_IN_SECONDS))
        else:
            test.log.info("Waiting 60.00 seconds for expected response: +CMT")
            test.expect(test.dut.at1.wait_for(test.CMT_URC, test.TIME_WAIT_IN_SECONDS))

        test.log.step('7. Check memory - there should be no received messages')
        test.check_dut_memory()

        test.log.step("8. Check AT+CNMI? - values shouldn't be changed. Delete all saved messages")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI?", '.*CNMI:.*' + str(mode) + ',1,0,0,\d.*OK.*'))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def get_information(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.expect(dstl_register_to_network(module))

    def check_dut_memory(test):
        zero_sms = "0"
        sms_number = dstl_get_sms_count_from_memory(test.dut)
        if sms_number[0] == 0:
            test.log.info('No SMS in the memory')
        else:
            test.log.error('There are some SMS in the memory. Number of SMS: ' + str(sms_number))
            test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(re.search(str(sms_number[0]), zero_sms))

    def check_no_urc(test, urc, timeout):
        elapsed_seconds = 0
        start_time = time.time()
        result = True
        while elapsed_seconds < timeout:
            if re.search(urc, test.dut.at1.last_response):
                result = False
                break
            elapsed_seconds = time.time() - start_time
        if result:
            test.log.info('No URC displayed - Correct behavior')
        else:
            test.log.error('URC displayed - Error')
        return result

    def clean_after_test(test, module):
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_select_sms_message_format(module))
        if module == test.dut:
            test.dut.at1.send_and_verify(test.AT_CSMP.format('0'), test.OK_RESPONSE)
            test.dut.at1.send_and_verify(test.AT_CNMI.format('0', '0'), test.OK_RESPONSE)
        else:
            test.r1.at1.send_and_verify(test.AT_CSMP.format('0'), test.OK_RESPONSE)
            test.r1.at1.send_and_verify(test.AT_CNMI.format('0', '0'), test.OK_RESPONSE)


if "__main__" == __name__:
    unicorn.main()