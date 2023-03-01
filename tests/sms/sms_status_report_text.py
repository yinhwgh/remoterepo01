#responsible: pawel.habrych@globallogic.com
#location: Wroclaw
#TC0011145.001, TC0011145.003

import unicorn
import re
import time

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory

class Test(BaseTest):
    """
    TC0011145.001 - SmsStatusReportText
    TC0011145.003 - SmsStatusReportText

    Test if status report of sent sms returns correctly.

    1. Select ME memory on DUT and REM
    2. Set text mode on DUT and Remote (at+cmgf=1)
    3. Check available "ds" value for at+cnmi parameter
    4. Set SMS URCs presentation on DUT and Remote (at+cnmi=2,1)
    5. Set SMS without SMS Status Report Request on DUT (at+csmp=17,1,0,0)
    6. Store SMS on DUT memory
    7. Set SMS with SMS Status Report Request on DUT (at+csmp=49,1,0,0)
    8. Store SMS on DUT memory
    9. Set ds=2 on DUT, send SMS from DUT memory and check Status Reports notification (SMS with SR and NoSr)
    - if supported on DUT
    10. Set ds=1 on DUT, send SMS from DUT memory and check Status Reports notification (SMS with SR and NoSr)
    - if supported on DUT
    11. Set ds=0 on DUT, send SMS from DUT memory and check Status Reports notification (SMS with SR and NoSr)
    12. Set ds=1 on DUT, send SMS with SR from DUT memory but do not ACK SR (at+cnma) - if supported on DUT

    On Quinn only ds=0 and ds=1 is supported, but in case 0 no indication is shown, and no status report is saved.
    In 3GPP2 devices/networks some values may not be supported
    In CDMA2k only Verizon network supports status reports!
    """

    OK_RESPONSE = ".*OK.*"
    AT_CNMI = "AT+CNMI={},{},0,{}"
    AT_CSMP = "AT+CSMP={},{},0,0"

    def setup(test):
        test.get_information(test.dut)
        test.get_information(test.r1)
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        if test.dut.project.upper() == "SERVAL":
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sms/AutoAck","0"', test.OK_RESPONSE))

    def run(test):
        AT_CSMS = "AT+CSMS=1"
        AT_CNMA = "AT+CNMA"
        AT_CSMP_TEST = "AT+CSMP?"
        AT_CNMI_READ = "AT+CNMI?"
        AT_CNMI_TEST = "AT+CNMI=?"
        AT_CNMI_SET = "AT+CNMI={},{}"

        TIME_WAIT_IN_SECONDS = 120
        CNMA_WAIT_IN_SECONDS = 30
        CDS_URC_DUT = ".*CDS.*"
        CDSI_URC_DUT = ".*CDSI.*"
        CMTI_URC_REM = ".*CMTI.*"
        CNMI_URC_DUT = ".*2,{},0,{}.*OK.*"
        CSMP_URC = r".*\+CSMP: {},1,0,0.*OK.*"

        test.log.info('Check number of SMS in SR memory')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        SR_SMS_NUMBER_START = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]

        test.log.step("1. Select ME memory on DUT and REM")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))

        test.log.step("2. Set text mode on DUT and Remote (at+cmgf=1)")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step('3. Check available "ds" value for at+cnmi parameter')
        test.expect(test.dut.at1.send_and_verify(AT_CSMS.format('1'), test.OK_RESPONSE))
        if test.dut.platform.upper() == "QCT":
            test.expect(test.dut.at1.send_and_verify(AT_CNMI_TEST, '.*\(0,1,2\),\(0,1,2,3\).*\(0,1\).*'))
        else:
            test.expect(test.dut.at1.send_and_verify(AT_CNMI_TEST, '.*\(0,1,2\),\(0,1,2,3\).*\(0,1,2\).*'))

        test.log.step('4. Set SMS URCs presentation on DUT and Remote (at+cnmi=2,1)')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI_SET.format('2', '1'), test.OK_RESPONSE))
        test.expect(test.r1.at1.send_and_verify(AT_CNMI_SET.format('2', '1'), test.OK_RESPONSE))

        test.log.step("5. Set SMS without SMS Status Report Request on DUT (at+csmp=17,1,0,0)")
        test.expect(test.dut.at1.send_and_verify(test.AT_CSMP.format('17', '1', '0', '0'), test.OK_RESPONSE))
        test.expect(test.dut.at1.send_and_verify(AT_CSMP_TEST, CSMP_URC.format('17')))

        test.log.step("6. Store SMS on DUT memory")
        test.expect(dstl_write_sms_to_memory(test.dut, "No Status Report"))
        SMS_NO_SR = test.get_sms_index("CMGW")

        test.log.step("7. Set SMS with SMS Status Report Request on DUT (at+csmp=49,1,0,0)")
        test.expect(test.dut.at1.send_and_verify(test.AT_CSMP.format('49', '1', '0', '0'), test.OK_RESPONSE))
        test.expect(test.dut.at1.send_and_verify(AT_CSMP_TEST, CSMP_URC.format('49')))

        test.log.step("8. Store SMS on DUT memory")
        test.expect(dstl_write_sms_to_memory(test.dut, "Status Report"))
        SMS_SR = test.get_sms_index("CMGW")

        test.log.step("9. Set ds=2 on DUT, send SMS from DUT memory and check Status Reports notification "
                      "(SMS with SR and NoSr) - if supported on DUT")
        if test.dut.platform.upper() == "QCT":
            test.log.info('ds=2 not supported')
        else:
            test.log.info('SMS without SR')
            test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '2'), test.OK_RESPONSE))
            test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_NO_SR, test.r1.sim.int_voice_nr))
            test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
            test.expect(test.check_no_urc(CDS_URC_DUT, TIME_WAIT_IN_SECONDS))
            test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
            SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
            if SR_SMS_NUMBER != SR_SMS_NUMBER_START:
                test.log.error('SR stored in memory')
            test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('1', '2')))
            test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))

            test.log.info('SMS with SR')
            test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '2'), test.OK_RESPONSE))
            test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_SR, test.r1.sim.int_voice_nr))
            test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
            test.expect(test.dut.at1.wait_for(CDSI_URC_DUT, TIME_WAIT_IN_SECONDS))
            test.sleep(CNMA_WAIT_IN_SECONDS)
            test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
            SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
            if int(SR_SMS_NUMBER - 1) == int(SR_SMS_NUMBER_START):
                test.log.info('SR stored correctly in Memory')
            else:
                test.log.error('SR not stored in Memory')
            test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('1', '2')))
            test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))


        test.log.step("10. Set ds=1 on DUT, send SMS from DUT memory and check Status Reports notification "
                      "(SMS with SR and NoSr) - if supported on DUT")

        test.log.info('SMS without SR')
        test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '1'), test.OK_RESPONSE))
        test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_NO_SR, test.r1.sim.int_voice_nr))
        test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
        test.expect(test.check_no_urc(CDS_URC_DUT, TIME_WAIT_IN_SECONDS))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
        if SR_SMS_NUMBER != SR_SMS_NUMBER_START:
            test.log.error('SR stored in memory')
        else:
            test.log.info('No new Status Reports in module memory')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('1', '1')))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))

        test.log.info('SMS with SR')
        test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '1'), test.OK_RESPONSE))
        test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_SR, test.r1.sim.int_voice_nr))
        test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
        test.expect(test.dut.at1.wait_for(CDS_URC_DUT, TIME_WAIT_IN_SECONDS))
        test.expect(test.dut.at1.send_and_verify(AT_CNMA, test.OK_RESPONSE))
        test.sleep(CNMA_WAIT_IN_SECONDS)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
        if SR_SMS_NUMBER != SR_SMS_NUMBER_START:
            test.log.error('SR stored in memory')
        else:
            test.log.info('Status Reports not stored in module memory')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('1', '1')))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))

        test.log.step("11. Set ds=0 on DUT, send SMS from DUT memory and check Status Reports notification "
                      "(SMS with SR and NoSr)")

        test.log.info('SMS without SR')
        test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '0'), test.OK_RESPONSE))
        test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_NO_SR, test.r1.sim.int_voice_nr))
        test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
        test.expect(test.check_no_urc(CDS_URC_DUT, TIME_WAIT_IN_SECONDS))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
        if SR_SMS_NUMBER != SR_SMS_NUMBER_START:
            test.log.error('SR stored in memory')
        else:
            test.log.info('No new Status Reports in module memory')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('1', '0')))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))

        test.log.info('SMS with SR')
        test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '0'), test.OK_RESPONSE))
        test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_SR, test.r1.sim.int_voice_nr))
        test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
        test.expect(test.check_no_urc(CDS_URC_DUT, TIME_WAIT_IN_SECONDS))
        test.sleep(CNMA_WAIT_IN_SECONDS)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
        if test.dut.platform.upper() == "QCT":
            if SR_SMS_NUMBER != SR_SMS_NUMBER_START:
                test.log.error('SR stored in memory')
            else:
                test.log.info('No new Status Reports in module memory')
        else:
            if int(SR_SMS_NUMBER - 1) == int(SR_SMS_NUMBER_START):
                test.log.info('SR stored correctly in Memory')
            else:
                test.log.error('SR not stored in Memory')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('1', '0')))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))

        test.log.step("12. Set ds=1 on DUT, send SMS with SR from DUT memory but do not ACK SR (at+cnma) "
                      "- if supported on DUT")
        test.expect(test.dut.at1.send_and_verify(test.AT_CNMI.format('2', '1', '1'), test.OK_RESPONSE))
        test.expect(dstl_send_sms_message_from_memory(test.dut, SMS_SR, test.r1.sim.int_voice_nr))
        test.expect(test.r1.at1.wait_for(CMTI_URC_REM, TIME_WAIT_IN_SECONDS))
        test.expect(test.dut.at1.wait_for(CDS_URC_DUT, TIME_WAIT_IN_SECONDS))
        test.sleep(CNMA_WAIT_IN_SECONDS)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        SR_SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))[0]
        if SR_SMS_NUMBER != SR_SMS_NUMBER_START:
            test.log.error('SR stored in memory')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI_READ, CNMI_URC_DUT.format('0', '0')))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))
        test.sleep(CNMA_WAIT_IN_SECONDS)

    def cleanup(test):
        test.clean_after_test(test.dut)
        test.clean_after_test(test.r1)

    def get_sms_index(test, command):
        response_content = test.expect(re.search(".*{}: (.*)".format(command), test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for command {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get {} value".format(command))

    def check_no_urc(test, urc, timeout):
        elapsed_seconds = 0
        start_time = time.time()
        result = True
        while elapsed_seconds < timeout:
            if re.search(urc, test.dut.at1.last_response):
                result = False
                break
            elapsed_seconds = time.time() - start_time
        return result

    def get_information(test, module):
        dstl_detect(module)
        test.expect(dstl_get_imei(module))
        test.expect(dstl_get_bootloader(module))
        test.expect(dstl_register_to_network(module))

    def clean_after_test(test, module):
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_select_sms_message_format(module))
        if module == test.dut:
            test.dut.at1.send_and_verify(test.AT_CSMP.format('17', '167'), test.OK_RESPONSE)
            test.dut.at1.send_and_verify(test.AT_CNMI.format('0', '0', '0'), test.OK_RESPONSE)
        else:
            test.r1.at1.send_and_verify(test.AT_CSMP.format('17', '167'), test.OK_RESPONSE)
            test.r1.at1.send_and_verify(test.AT_CNMI.format('0', '0', '0'), test.OK_RESPONSE)

if "__main__" == __name__:
    unicorn.main()