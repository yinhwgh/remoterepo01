#responsible agata.mastalska@globallogic.com
#Wroclaw

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network, attach_to_network
from dstl.sms import delete_sms, send_sms_message, write_sms_to_memory
import re

class Test(BaseTest):
    """
    Send and recive sms

    1. Test initialization
    2. Send SMS to remote
    3. Receive SMS from remote

    author: agata.mastalska@globallogic.com
    """

    def setup(test):
        test.log.step("1. Test initialization")
        test.dut.dstl_detect()
        test.r1.dstl_detect()

        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())
        #test.dut.dstl_register_to_network()

        test.expect(test.r1.dstl_enter_pin())
        test.expect(test.r1.dstl_register_to_network())

        test.log.info("Delate all messages from storage.")
        test.expect(test.dut.dstl_delete_all_sms_messages)
        test.expect(test.r1.dstl_delete_all_sms_messages)

        test.log.info("Set URC for received SMS.")
        test.expect(test.r1.at1.send_and_verify('AT+CNMI=1,1', '.*OK.*'))

        test.log.info("Set text mode format.")
        #test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))

    def run(test):
        test.log.step("2. Send SMS to remote")
        index = test.dut.dstl_write_sms_to_memory(sms_text="abcdefgh1234567890", sms_format='text', return_index=True)
        test.expect(test.dut.at1.send_and_verify('AT+CMSS={}, "{}"'.format(index[0], test.r1.sim.int_voice_nr), '.*OK.*'))

        test.log.step("3. Receive SMS from remote")
        test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
        msg_index = get_message_index(test.r1.at1.last_response)
        if msg_index is not False:
            test.expect(test.r1.at1.send_and_verify("AT+CMGR={}".format(msg_index), '.*OK.*'))
        else:
            test.expect(False, critical=True)

    def cleanup(test):
        test.dut.at1.close()

if "__main__" == __name__:
    unicorn.main()

def get_message_index(response):
    pattern = '\d+'
    match = re.search(pattern, response)
    if match:
        return match.group()
    else:
        return False