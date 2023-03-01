#responsible: pawel.habrych@globallogic.com
#location: Wroclaw
#TC0094926.001, TC0094926.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory

class Test(BaseTest):
    """
    Check a module behavior with usage of longer parameter. According to E.164 recommendation maximum length is
    15 digits plus prefix (up to 5 digits e.g. in Finland or one "+" sign instead digital prefix).

    1. Set character set with at+cscs="GSM" command.
    2. Write to memory message with 20 digits i.e. at+cmgw="12345678901234567890"
    3. Write to memory message with 15 digits and "+" i.e. at+cmgw="+123456789012345"
    4. Write to memory message with 30 digits  i.e. at+cmgw="123456789012345678901234567890"
    5. Read messages written to memory and check if <da> is correct
    6. Send message with 20 digits by at+cmgs command i.e. at+cmgs="12345678901234567890"
    7. Send message with 15 digits and "+" by at+cmgs command i.e. at+cmgs="+123456789012345"
    8. Send message with 30 digits by at+cmgs command i.e. at+cmgs="123456789012345678901234567890"
    9. Send from memory message from point 2 with new 20 digits i.e. at+cmss=0,"12345678901234567890"
    10. Send from memory message from point 2 with new 15 digits and "+" i.e. at+cmss=0,"+123456789012345"
    11. Send from memory message from point 2 with new 30 digits i.e. at+cmss=0,"123456789012345678901234567890"
    12. Send from memory message from point 2 without changing i.e. at+cmss=0
    If module support concatenated messages execute below steps for this structure:
    13. Write to storage concatenated message with 20 digits : i.e. at^scmw="12345678901234567890",,,    1,2,8,255
    at^scmw="12345678901234567890",,,2,2,8,255
    14. Write to storage concatenated message with 30 digits : i.e. at^scmw="123456789012345678901234567890",,,1,2,8,255
    at^scmw="123456789012345678901234567890",,,2,2,8,255
    15. Read messages written to memory and check if <da> is correct
    16. Send concatenated message with 20 digits : i.e. at^scms="12345678901234567890",,1,2,8,255
    at^scms="12345678901234567890",,2,2,8,255
    17. Send concatenated message with 30 digits : i.e. at^scms="123456789012345678901234567890",,1,2,8,255
    at^scms="123456789012345678901234567890",,2,2,8,255
    18. Try to send from memory concatenated message from point 13  i.e. at+cmss=2, at+cmss=3
    """

    OK_RESPONSE = ".*OK.*"
    TIME_WAIT_IN_SECONDS = 30
    SMS_TIMEOUT = 300
    AT_CMGR = "AT+CMGR={}"
    AT_SCMR = "AT^SCMR={}"
    AT_CMSS = "AT+CMSS={}"
    ERROR_RESPONSE_INVALID = ".*CMS ERROR.*invalid parameter.*|.*CMS ERROR: invalid text mode parameter.*"
    ERROR_RESPONSE_OK_OR_CMS_ERROR = ".*OK.*|.*CMS ERROR.*unknown error.*|.*CMS ERROR: invalid text mode parameter.*"

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_select_sms_message_format(test.dut))
        if test.dut.project.upper() != "VIPER":
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="Sms/AutoAck","0"', test.OK_RESPONSE))

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.info('TC0094926.002 - MaxSmsDestinationAddressTextGsm')
        else:
            test.log.info('TC0094926.001 - MaxSmsDestinationAddressTextGsm')

        test.log.step('1. Set character set with at+cscs="GSM" command.')
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', test.OK_RESPONSE))

        test.log.step('2. Write to memory message with 20 digits i.e. at+cmgw="12345678901234567890"')
        test.expect(test.dut.at1.send_and_verify('AT+CMGW="12345678901234567890"', ".*>"))
        test.expect(test.dut.at1.send_and_verify('20 digits SMS\x1A', test.OK_RESPONSE))

        test.log.step('3. Write to memory message with 15 digits and "+" i.e. at+cmgw="+123456789012345"')
        test.expect(test.dut.at1.send_and_verify('AT+CMGW="+123456789012345"', ".*>"))
        test.expect(test.dut.at1.send_and_verify('15 digits SMS\x1A', test.OK_RESPONSE))

        test.log.step('4. Write to memory message with 30 digits  i.e. at+cmgw="123456789012345678901234567890"')
        test.expect(test.dut.at1.send_and_verify('AT+CMGW="123456789012345678901234567890"',
                                                 test.ERROR_RESPONSE_INVALID))

        test.log.step('5. Read messages written to memory and check if <da> is correct')
        test.expect(test.dut.at1.send_and_verify(test.AT_CMGR.format("0"), '.*STO UNSENT.*12345678901234567890.*'))
        test.expect(test.dut.at1.send_and_verify(test.AT_CMGR.format("1"), '.*STO UNSENT.*\+123456789012345.*'))
        test.expect(test.dut.at1.send_and_verify(test.AT_CMGR.format("2"), test.OK_RESPONSE))

        test.log.step('6. Send message with 20 digits by at+cmgs command i.e. at+cmgs="12345678901234567890"')
        test.expect(test.dut.at1.send_and_verify('AT+CMGS="12345678901234567890"','.*>.*'))
        test.expect(test.dut.at1.send_and_verify('20 digits SMS by CMGS\x1A', test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                 timeout=test.SMS_TIMEOUT))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('7. Send message with 15 digits and "+" by at+cmgs command i.e. at+cmgs="+123456789012345"')
        test.expect(test.dut.at1.send_and_verify('AT+CMGS="+123456789012345"','.*>.*'))
        test.expect(test.dut.at1.send_and_verify('15 digits SMS by CMGS\x1A', test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                 timeout=test.SMS_TIMEOUT))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('8. Send message with 30 digits by at+cmgs command i.e. '
                      'at+cmgs="123456789012345678901234567890"')
        test.expect(test.dut.at1.send_and_verify('AT+CMGS="123456789012345678901234567890"',
                                                 test.ERROR_RESPONSE_INVALID))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('9. Send from memory message from point 2 with new 20 digits i.e.'
                      ' at+cmss=0,"12345678901234567890"')
        test.expect(test.dut.at1.send_and_verify('AT+CMSS=0,"12345678901234567890"',
                                                 test.ERROR_RESPONSE_OK_OR_CMS_ERROR, timeout=test.SMS_TIMEOUT))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('10. Send from memory message from point 2 with new 15 digits and "+" i.e.'
                      ' at+cmss=0,"+123456789012345"')
        test.expect(test.dut.at1.send_and_verify('AT+CMSS=0,"+123456789012345"', test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                 timeout=test.SMS_TIMEOUT))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('11. Send from memory message from point 2 with new 30 digits i.e. '
                      ' at+cmss=0,"123456789012345678901234567890"')
        test.expect(test.dut.at1.send_and_verify('AT+CMSS=0,"123456789012345678901234567890"',
                                                 test.ERROR_RESPONSE_INVALID))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('12. Send from memory message from point 2 without changing i.e. at+cmss=0')
        test.expect(test.dut.at1.send_and_verify(test.AT_CMSS.format("0"), test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                 timeout=test.SMS_TIMEOUT))
        test.sleep(test.TIME_WAIT_IN_SECONDS)

        test.log.step('If module support concatenated messages execute below steps for this structure:')
        if test.dut.project.upper() == "SERVAL":
            test.log.info('Concatenated SMS not supported')
            test.log.info('Omitted steps')
            test.log.info('13. Write to storage concatenated  message with 20 digits : i.e. ')
            test.log.info('at^scmw="12345678901234567890",,,1,2,8,255, at^scmw="12345678901234567890",,,2,2,8,255')
            test.log.info('14. Write to storage concatenated message with 30 digits : i.e. ')
            test.log.info('at^scmw="123456789012345678901234567890",,,1,2,8,255')
            test.log.info('at^scmw="123456789012345678901234567890",,,2,2,8,255')
            test.log.info('15. Read messages written to memory and check if <da> is correct')
            test.log.info('16. Send concatenated message with 20 digits : i.e.')
            test.log.info('at^scms="12345678901234567890",,1,2,8,255, at^scms="12345678901234567890",,2,2,8,255')
            test.log.info('17. Send concatenated message with 30 digits : i.e')
            test.log.info('at^scms="123456789012345678901234567890",,1,2,8,255')
            test.log.info('at^scms="123456789012345678901234567890",,2,2,8,255')
            test.log.info('18. Try to send from memory concatenated message from point 13  i.e. at+cmss=2, at+cmss=3"')
        else:
            test.log.step('13. Write to storage concatenated message with 20 digits : i.e. ')
            test.log.step('at^scmw="12345678901234567890",,,1,2,8,255, at^scmw="12345678901234567890",,,2,2,8,255')
            test.expect(dstl_delete_all_sms_messages(test.dut))
            test.expect(test.dut.at1.send_and_verify('at^scmw="12345678901234567890",,,1,2,8,255', ".*>"))
            test.expect(test.dut.at1.send_and_verify('20 digits SMS\x1A', test.OK_RESPONSE))
            test.expect(test.dut.at1.send_and_verify('at^scmw="12345678901234567890",,,2,2,8,255', ".*>"))
            test.expect(test.dut.at1.send_and_verify('20 digits SMS\x1A', test.OK_RESPONSE))

            test.log.step('14. Write to storage concatenated message with 30 digits : i.e. ')
            test.log.step('at^scmw="123456789012345678901234567890",,,1,2,8,255')
            test.log.step('at^scmw="123456789012345678901234567890",,,2,2,8,255')
            test.expect(test.dut.at1.send_and_verify('at^scmw="123456789012345678901234567890",,,1,2,8,255',
                                                     test.ERROR_RESPONSE_INVALID))
            test.expect(test.dut.at1.send_and_verify('at^scmw="123456789012345678901234567890",,,2,2,8,255',
                                                     test.ERROR_RESPONSE_INVALID))

            test.log.step('15. Read messages written to memory and check if <da> is correct')
            test.expect(test.dut.at1.send_and_verify(test.AT_SCMR.format("0"),
                                                     '.*STO UNSENT.*12345678901234567890.*,1,2,8,255.*'))
            test.expect(test.dut.at1.send_and_verify(test.AT_SCMR.format("1"),
                                                     '.*STO UNSENT.*12345678901234567890.*,2,2,8,255.*'))

            test.log.step('16. Send concatenated message with 20 digits : i.e.')
            test.log.step('at^scms="12345678901234567890",,1,2,8,255, at^scms="12345678901234567890",,2,2,8,255')
            test.expect(test.dut.at1.send_and_verify('at^scms="12345678901234567890",,1,2,8,255', '.*>.*'))
            test.expect(test.dut.at1.send_and_verify('20 digits SMS by SCMS\x1A', test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                     timeout=test.SMS_TIMEOUT))
            test.sleep(test.TIME_WAIT_IN_SECONDS)
            test.expect(test.dut.at1.send_and_verify('at^scms="12345678901234567890",,2,2,8,255', '.*>.*'))
            test.expect(test.dut.at1.send_and_verify('20 digits SMS by SCMS\x1A', test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                     timeout=test.SMS_TIMEOUT))
            test.sleep(test.TIME_WAIT_IN_SECONDS)

            test.log.step('17. Send concatenated message with 30 digits : i.e')
            test.log.step('at^scms="123456789012345678901234567890",,1,2,8,255')
            test.log.step('at^scms="123456789012345678901234567890",,2,2,8,255')
            test.expect(test.dut.at1.send_and_verify('at^scms="123456789012345678901234567890",,1,2,8,255',
                                                     test.ERROR_RESPONSE_INVALID))
            test.sleep(test.TIME_WAIT_IN_SECONDS)
            test.expect(test.dut.at1.send_and_verify('at^scms="123456789012345678901234567890",,2,2,8,255',
                                                     test.ERROR_RESPONSE_INVALID))
            test.sleep(test.TIME_WAIT_IN_SECONDS)

            test.log.step('18. Try to send from memory concatenated message from point 13  i.e. at+cmss=2, at+cmss=3"')
            test.expect(test.dut.at1.send_and_verify(test.AT_CMSS.format("0"), test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                     timeout=test.SMS_TIMEOUT))
            test.sleep(test.TIME_WAIT_IN_SECONDS)
            test.expect(test.dut.at1.send_and_verify(test.AT_CMSS.format("1"), test.ERROR_RESPONSE_OK_OR_CMS_ERROR,
                                                     timeout=test.SMS_TIMEOUT))
            test.sleep(test.TIME_WAIT_IN_SECONDS)

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.dut.at1.send_and_verify("AT&F", test.OK_RESPONSE)
        test.dut.at1.send_and_verify("AT&W", test.OK_RESPONSE)


if "__main__" == __name__:
    unicorn.main()