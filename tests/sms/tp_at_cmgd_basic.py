# responsible: marek.polak@globallogic.com
# location: Wroclaw
# TC0091823.001
#SRV03-5034

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_list_occupied_sms_indexes
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    """
    This procedure provides the possibility of basic tests for the test and write command of +CMGD.

    1. Check command without PIN authentication
    2. Check command with PIN authentication
    3. Check all parameters and also invalid values

    Cmgd functionality is checked in tests: SmsMEWriteDeleteText, SmsMEWriteDeletePDU
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        result = test.dut.at1.send_and_verify('AT+CPIN?', '.*SIM PIN.*')
        if not result:
            dstl_restart(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step('Step 1. Check command without PIN ')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', r'.*\+CPIN: SIM PIN.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=?', r".*\+CMS ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=1', r".*\+CMS ERROR: SIM PIN required.*"))

        test.log.step('Step 2. Check command with PIN authentication ')
        dstl_enter_pin(test.dut)
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+CPMS?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=?', '.*\+CMGD: \(.*\)\s*OK\s*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=2', '.*OK.*'))

        test.log.step('Step 3. Check all parameters and also invalid values ')
        test.expect(test.dut.at1.send_and_verify('AT+CMGD?', r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD', r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=-1', r'.*\+CMS ERROR:.*'))
        max_mem_index = dstl_get_sms_memory_capacity(test.dut, 1)
        test.expect(test.dut.at1.send_and_verify('AT+CMGD={}'.format(int(max_mem_index)+1), r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=321', r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=any', r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD=ANY', r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD="ANY"', r'.*\+CMS ERROR:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGD="1"', r'.*\+CMS ERROR:.*'))
        dstl_select_sms_message_format(test.dut, sms_format='Text')
        dstl_set_preferred_sms_memory(test.dut, preferred_storage='ME')
        test.expect(test.dut.at1.send_and_verify('AT+CMGL="ALL"', '.*OK.*'))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(not dstl_list_occupied_sms_indexes(test.dut), msg='The sms messages were not deleted correctly.')
        test.expect(test.dut.at1.send_and_verify('AT+CPMS?', '.*\+CPMS: "ME",0,.*OK.*'))
        dstl_write_sms_to_memory(test.dut, sms_text='This is a test SMS')
        dstl_write_sms_to_memory(test.dut, sms_text='This is a second test SMS')
        test.expect(test.dut.at1.send_and_verify('AT+CPMS?', '.*\+CPMS: "ME",2,.*OK.*'))
        sms_list = dstl_list_occupied_sms_indexes(test.dut)
        for index in sms_list:
            test.expect(test.dut.at1.send_and_verify('AT+CMGD={}'.format(index), '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMGL="ALL"', '.*OK.*'))
        test.expect(not dstl_list_occupied_sms_indexes(test.dut), msg='The sms messages were not deleted correctly.')

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
