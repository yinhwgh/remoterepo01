# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0104483.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.sms import sms_configurations, write_sms_to_memory, sms_memory_capacity
from dstl.sms import send_sms_message, list_sms_message, delete_sms, get_sms_count_from_memory
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    '''
    TC0104483.001 - SMSRemoveByFactoryReset
    This test case is design to check whether short messages are deleted
    after the AT command AT^SCFG="MEopMode/Factory","all"

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(5)

    def run(test):

        test.log.info('1. Set AT^SCFG="MEopMode/Factory","none" and restart the module.')
        test.expect(test.dut.at1.send_and_verify('at^scfg=\"MEopMode/Factory\",none', 'OK'))
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_register_to_network()

        test.log.info('2. Fill all accessible message storages with SMS.include sms unsent,sent,received')
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=1'))
        test.expect(test.dut.dstl_set_preferred_sms_memory('SM'))
        test.expect(test.dut.dstl_delete_all_sms_messages())
        test.expect(test.dut.dstl_set_preferred_sms_memory('ME'))
        test.expect(test.dut.dstl_delete_all_sms_messages())

        test.expect(test.dut.at1.send_and_verify(f'at+csca={test.dut.sim.sca_int}', 'OK'))

        test.expect(test.dut.dstl_set_preferred_sms_memory('SM'))
        test.dut.dstl_write_sms_to_memory(sms_text='SM TEST SMS SMS SMS ')

        test.expect(test.dut.dstl_set_preferred_sms_memory('ME'))
        # IPIS100323117
        test.expect(test.dut.at1.send_and_verify(f'at+cmgw={test.r1.sim.int_voice_nr}', '>',wait_for='>'))
        test.expect(test.dut.at1.send_and_verify('TEST SMS 1 TO REMOTE1 \x1A', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(f'at+cmgw={test.r1.sim.int_voice_nr}', '>',wait_for='>'))
        test.expect(test.dut.at1.send_and_verify('TEST SMS 2 TO REMOTE1 \x1A', '.*OK.*'))

        max = int(test.dut.dstl_get_sms_memory_capacity(1))
        for i in range(max - 2):
            test.dut.dstl_write_sms_to_memory(sms_text=f'ME TEST SMS SMS SMS {i}')

        test.expect(test.dut.dstl_send_sms_message_from_memory(1))
        test.expect(test.dut.dstl_send_sms_message_from_memory(2))
        test.sleep(5)

        test.expect(test.dut.dstl_list_sms_messages_from_preferred_memory('ALL'))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS?',f'CPMS: \"ME\",{max},{max}.*'))

        test.log.info('3. Execute AT^SCFG="MEopMode/Factory","all"')
        test.expect(test.dut.dstl_reset_to_factory_default())
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.log.info('4. Check all accessible message storages.')
        test.expect(test.dut.dstl_set_preferred_sms_memory('ME', 1))
        test.expect(test.dut.dstl_set_preferred_sms_memory('MT', 2))
        test.expect(test.dut.dstl_set_preferred_sms_memory('SM', 3))

        memory_count = test.dut.dstl_get_sms_count_from_memory()
        me_count = memory_count[0]
        mt_count = memory_count[1]
        sm_count = memory_count[2]
        if mt_count == 0 and me_count == 0 and sm_count != 0:
            test.log.info('Short messages  are deleted after reset(except in SM), test pass')
            test.expect(True)
        else:
            test.log.error('Short messages are not deleted after reset(except in SM), test failed')
            test.expect(False)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
