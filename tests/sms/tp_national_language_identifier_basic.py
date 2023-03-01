# responsible: sebastian.lupkowski@globallogic.com
# location: Wroclaw
# TC0095036.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.identification.get_imei import dstl_get_imei
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0095036.001    TpNationalLanguageIdentifierBasic

    Test if SMS with chars from national language (i.e. Turkish) works properly.
    Adding Special (national characters) requires using of national language tables described at 3GPP TS 23.038 V8.2.0.
    The mechanism of those tables usage requires an indication by adding a National Language Single Shift IE (24) and a
    National Language Locking Shift IE (25) in TP User Data Header, as defined in 3GPP TS 23.040. Decoding of such a
    message should be done by using single shift or locking shift table as applicable for the language indicated in the
    National Language Identifier within these IEs. The Turkish National Language Identifier octet is encoded as
    00000001 (in table 6.2.1.2.4.1. of 3GPP TS 23.038 V8.2.0)

    Step 1. Check Locking Shift mechanism: Write to memory a SMS containing one Turkish letter (0001011) 
    using the mechanism of National Language Locking Shift Table of Turkish language
    Step 2. Check Single Shift mechanism: Chars from GSM 7 bit Default Alphabet and Turkish National 
    Language Single Shift Table after every char. In this case UserDataHeader is 4 bytes (32 bits) 
    long: 03240101
    Step 3. Check both Single Shift and Locking Shift mechanism: Mixed - Turkish letters from Locking 
    Shift Table and Single Shift Table one from Locking, escape to Single, char from Single and 
    next from Locking. In this case UserDataHeader is 7 bytes (56 bits) long: 06250101240101. 
    It means that it fills all bits till septet boundary - no additional fill bits needed!
    Step 4. Send messages in steps 1-3, read and compare the received one with sent.
    """

    messages = []
    contents = []
    lengths = ['20', '40', '42']
    contents_received = ['6032501015800', '03240101006EA6E0CD98B0991F36C7C5E6CCD824399B74675306',
                         '2006250101240101C0CD14BC191336F3C3E6B8D89C199B246793EE6CCA']

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
        test.expect(dstl_set_preferred_sms_memory(test.dut, preferred_storage='ME'))
        test.contents.append('{}5100{}00000006032501015A00'.format(test.dut.sim.sca_pdu, test.dut.sim.pdu))
        test.contents.append('{}5100{}0000001D03240101076EA6E0CD98B0991F36C7C5E6CCD824399B74675306'
                             .format(test.dut.sim.sca_pdu, test.dut.sim.pdu))
        test.contents.append('{}5100{}0000002006250101240101C0CD14BC191336F3C3E6B8D89C199B246793EE6CCA'
                             .format(test.dut.sim.sca_pdu, test.dut.sim.pdu))

    def run(test):
        test.log.step("1. Check Locking Shift mechanism: Write to memory a SMS containing one Turkish letter (0001011) "
                      "using the mechanism of National Language Locking Shift Table of Turkish language")
        write_read_sms(test, 0)

        test.log.step("2. Check Single Shift mechanism: Chars from GSM 7 bit Default Alphabet and Turkish National "
                      "Language Single Shift Table after every char. In this case UserDataHeader is 4 bytes (32 bits) "
                      "long: 03240101")
        write_read_sms(test, 1)

        test.log.step("3. Check both Single Shift and Locking Shift mechanism: Mixed - Turkish letters from Locking "
                      "Shift Table and Single Shift Table one from Locking, escape to Single, char from Single and "
                      "next from Locking. In this case UserDataHeader is 7 bytes (56 bits) long: 06250101240101. "
                      "It means that it fills all bits till septet boundary - no additional fill bits needed!")
        write_read_sms(test, 2)

        test.log.step("4. Send messages in steps 1-3, read and compare the received one with sent.")
        for i in range(0, 3):
            send_receive_sms(test, i)

    def cleanup(test):
        for index in test.messages:
            test.expect(test.dut.at1.send_and_verify("AT+CMGD={}".format(index), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def write_read_sms(test, mode):
    test.expect(test.dut.at1.send_and_verify('AT+CMGW={}'.format(test.lengths[mode]), ".*>.*", wait_for=".*>.*"))
    if test.expect(test.dut.at1.send_and_verify(test.contents[mode], end="\u001A", expect=r".*\+CMGW.*", timeout=30)):
        index = get_message_index_from_response(test.dut.at1.last_response)
        if index is not None:
            test.messages.append(index)
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(index), ".*{}.*OK.*"
                                                     .format(test.contents[mode])))


def send_receive_sms(test, mode):
    if test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(test.messages[mode]), ".*OK.*", wait_for=".*CMTI.*",
                                                timeout=120)):
        index = get_message_index_from_response(test.dut.at1.last_response)
        if index is not None:
            test.messages.append(index)
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(index), ".*{}.*OK.*"
                                                     .format(test.contents_received[mode])))


def get_message_index_from_response(response):
    index = re.match('(?s)(.*CMGW:*.|.*CMTI:.*,.*)(\\d{1,3})(.*)', response)
    if index:
        return index.group(2)
    else:
        return None


if "__main__" == __name__:
    unicorn.main()
