#responsible: pawel.habrych@globallogic.com, renata.bryla@globallogic.com
#location: Wroclaw
#TC0092179.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory


class Test(BaseTest):
    """
    TC0092179.001 - SystematicIndicationForIncomingSMS

    Test intention is to check if  at^scfg="Sms/Autoack" command allows user to skip automatic disabling of direct
    forwarding (to the application) of incoming SMS after a currently received SMS has not been acknowledged

    1.  (DUT) Set AT^SCFG="Sms/AutoAck","0" - AutoAck OFF
    2.  (DUT) Set AT+CMGF=1, AT+CSMS=1, AT+CNMI=2,2, AT+CPMS="ME","ME","ME", AT+CMEE=2
    3.  (Rmt) Set AT+CMGF=1, AT+CSMP=17,167,0,0
    4.  (Rmt) Send SMS to DUT, AT+CMGS=<Dut number>
    5.  (DUT) Wait for URC +CMT.
    6.  (DUT) Set AT+CNMA - manual acknowledge
    7.  (DUT) Check memory storage, set AT+CPMS?
    8.  (DUT) Check cnmi, set AT+CNMI?
    9.  (Rmt) Send another SMS to DUT, AT+CMGS=<Dut number>
    10. (DUT) Wait for URC +CMT.
    11. (DUT) Wait over 20 sec (15sec is specified)
    12. (DUT) Set AT+CNMA
    13. (DUT) Check cnmi, set AT+CNMI?
    14. (DUT) Check memory storage, set AT+CPMS?
    15. (DUT) Check memory storage, set AT+CPMS?, after SMS retransmission ?
    16. (DUT) Set AT+CNMI=2,2
    17. (DUT) Set AT^SCFG="Sms/AutoAck","1" - AutoAck ON
    18. (Rmt) Send another SMS to DUT, AT+CMGS=<Dut number>
    19. (DUT) Wait for URC: +CMT
    20. (DUT) Try to set AT+CNMA
    21. (DUT) Wait over 20sec (15sec is specified)
    22. (DUT) Check cnmi, set AT+CNMI?
    """

    OK_RESPONSE = ".*OK.*"

    def setup(test):
        test.get_information(test.dut)
        test.get_information(test.r1)
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))

    def run(test):
        TIME_OUT_IN_SECONDS = 120
        CNMA_WAIT_IN_SECONDS = 30
        AT_CNMA = "AT+CNMA"
        AT_CNMI = "AT+CNMI?"
        CMT_URC = ".*CMT.*"
        ERROR_RESPONSE = ".*CMS ERROR: no \\+CNMA acknowledgement expected.*"
        ZERO_SMS = "0"
        ONE_SMS = "1"
        ZERO_OR_ONE_SMS = "0|1"

        test.log.step('1.(DUT) Set AT^SCFG=Sms/AutoAck,0 - AutoAck OFF')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sms/AutoAck","0"', test.OK_RESPONSE))

        test.log.step('2.(DUT) Set AT+CMGF=1, AT+CSMS=1, AT+CNMI=2,2 , AT+CPMS="ME","ME","ME", AT+CMEE=2')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSMS=1', test.OK_RESPONSE))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,2', test.OK_RESPONSE))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', test.OK_RESPONSE))

        test.log.step('3.(Rmt) Set AT+CMGF=1, AT+CSMP=17,167,0,0')
        test.expect(dstl_select_sms_message_format(test.r1))
        test.expect(test.r1.at1.send_and_verify('AT+CSMP=17,167,0,0', test.OK_RESPONSE))

        test.log.step('4.(Rmt) Send SMS to DUT, AT+CMGS=<Dut number>')
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "Test 1 from Remote - Step4"))

        test.log.step('5.(DUT) Wait for URC +CMT. ')
        test.expect(test.dut.at1.wait_for(CMT_URC + "Test 1 from Remote - Step4.*", TIME_OUT_IN_SECONDS))

        test.log.step('6.(DUT) Set AT+CNMA - manual acknowledge')
        test.expect(test.dut.at1.send_and_verify(AT_CNMA, test.OK_RESPONSE))

        test.log.step('7.(DUT) Check memory storage, set AT+CPMS?')
        test.sleep(TIME_OUT_IN_SECONDS)
        SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))
        test.expect(re.search(str(SMS_NUMBER[0]), ZERO_SMS))
        if SMS_NUMBER[0] == 0:
            test.log.info('No SMS in the memory - correct behavior')
        else:
            test.log.error('There are some SMS in the memory. Number of SMS: ' + str(SMS_NUMBER))
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('8.(DUT) Check cnmi, set AT+CNMI?')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI, '.*2,2,.*'))

        test.log.step('9.(Rmt) Send another SMS to DUT, AT+CMGS=<Dut number>')
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "Test 2 from Remote - Step9"))

        test.log.step('10. (DUT) Wait for URC +CMT.')
        test.expect(test.dut.at1.wait_for(CMT_URC + "Test 2 from Remote - Step9.*", TIME_OUT_IN_SECONDS))

        test.log.step('11.(DUT) Wait over 20 sec (15sec is specified)')
        test.sleep(CNMA_WAIT_IN_SECONDS)

        test.log.step('12.(DUT) Set AT+CNMA')
        test.expect(test.dut.at1.send_and_verify(AT_CNMA, ERROR_RESPONSE))

        test.log.step('13.(DUT) Check cnmi, set AT+CNMI?')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI, '.*2,0,.*'))

        test.log.step('14.(DUT) Check memory storage, set AT+CPMS?')
        SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))
        test.expect(re.search(str(SMS_NUMBER[0]), ZERO_OR_ONE_SMS))
        if SMS_NUMBER[0] == 0:
            test.log.info('SMS_NUMBER = 0 - No SMS in the memory yet')
        elif SMS_NUMBER[0] == 1:
            test.log.info('SMS_NUMBER = 1 - SMS correctly retransmitted')
        else:
            test.log.error('There should be one retransmitted SMS in the memory. Number of SMS: ' + str(SMS_NUMBER[1]))
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('15.(DUT) Check memory storage, set AT+CPMS?, after SMS retransmission ?')
        test.sleep(TIME_OUT_IN_SECONDS)
        SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))
        test.expect(re.search(str(SMS_NUMBER[0]), ONE_SMS))
        if SMS_NUMBER[0] == 1:
            test.log.info('SMS retransmitted')
        elif SMS_NUMBER[0] == 0:
            test.log.error('No SMS in the memory')
        else:
            test.log.error('There is more than one SMS in memory. Number of SMS: ' + str(SMS_NUMBER[1]))
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('16.(DUT) Set AT+CNMI=2,2')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,2', test.OK_RESPONSE))
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('17.(DUT) Set AT^SCFG="Sms/AutoAck","1" - AutoAck ON')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sms/AutoAck","1"', test.OK_RESPONSE))

        test.log.step('18. (Rmt) Send another SMS to DUT, AT+CMGS=<Dut number>')
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "Test 3 from Remote - Step18"))

        test.log.step('19. (DUT) Wait for URC: +CMT')
        test.expect(test.dut.at1.wait_for(CMT_URC + "Test 3 from Remote - Step18.*", TIME_OUT_IN_SECONDS))

        test.log.step('20. (DUT) Try to set AT+CNMA')
        test.expect(test.dut.at1.send_and_verify(AT_CNMA, ERROR_RESPONSE))

        test.log.step('21. (DUT) Wait over 20sec (15sec is specified)')
        test.sleep(CNMA_WAIT_IN_SECONDS)

        test.log.step('22. (DUT) Check cnmi, set AT+CNMI?')
        test.expect(test.dut.at1.send_and_verify(AT_CNMI, '.*2,2,.*'))
        test.log.info('(DUT) Check memory storage, set AT+CPMS?')
        test.sleep(TIME_OUT_IN_SECONDS)
        SMS_NUMBER = test.expect(dstl_get_sms_count_from_memory(test.dut))
        test.expect(re.search(str(SMS_NUMBER[0]), ZERO_SMS))
        if SMS_NUMBER[0] == 0:
            test.log.info('No SMS in the memory - correct behavior')
        else:
            test.log.error('There are some SMS in the memory. Number of SMS: ' + str(SMS_NUMBER))
            test.expect(dstl_delete_all_sms_messages(test.dut))

    def cleanup(test):
        test.clean_after_test(test.dut)
        test.clean_after_test(test.r1)

    def get_information(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_register_to_network(module))

    def clean_after_test(test, module):
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_delete_all_sms_messages(module))
        module.at1.send_and_verify("AT+CSMP=17,167,0,0", test.OK_RESPONSE)
        module.at1.send_and_verify("AT+CNMI=0,0,0,0", test.OK_RESPONSE)


if "__main__" == __name__:
    unicorn.main()