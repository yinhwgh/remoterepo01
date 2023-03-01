#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0104632.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.hardware import set_real_time_clock
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    '''
    TC0104632.001 - ClockAlarmResetByFactoryReset
    This test case is design to check whether clock settings are reset
    after the AT command AT^SCFG="MEopMode/Factory","all"

    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(3)

    def run(test):
        test.log.info('1. Set AT^SCFG="MEopMode/Factory","none" and restart the module.')
        test.expect(test.dut.at1.send_and_verify('at^scfg=\"MEopMode/Factory\",none', 'OK'))

        test.log.info('2.Set the clock alarm and restart the module.')
        test.expect(test.dut.at1.send_and_verify('at+cala="31/11/11,11:11:11",1,0,"hello"', 'OK'))
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.sleep(3)

        test.log.info('3.Check if clock alarm is unchanged.')
        test.dut.at1.send_and_verify('at+cala?','CALA: "31/11/11,11:11:11",1,0,"hello"')

        test.log.info('4. Execute AT^SCFG="MEopMode/Factory","all", restart module.')
        test.expect(test.dut.dstl_reset_to_factory_default())

        test.log.info('5.Check if clock alarm have been removed.')
        test.dut.at1.send_and_verify('at+cala?')
        res = test.dut.at1.last_response
        test.expect('hello' not in res)


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
