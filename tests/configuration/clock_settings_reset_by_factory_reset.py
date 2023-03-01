#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0104486.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.hardware import set_real_time_clock
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    '''
    TC0104486.001 - ClockSettingsResetByFactoryReset
    This test case is design to check whether clock settings are reset
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

        test.log.info('2. Disable automatic time zone update by AT+CTZU=0 command.')
        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', 'OK|ERROR'))
        test.log.info('3. Set the clock and date to different values than they really are.')
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_enter_pin()
        test.sleep(5)
        past_time = '20/03/01,12:12:12'
        default_time = '80/01/06,00'
        test.dut.dstl_set_real_time_clock('at1',past_time)
        test.dut.at1.send_and_verify('at+cclk?')
        test.expect('20/03/01,12:12' in test.dut.at1.last_response)

        test.log.info('4. Execute AT^SCFG="MEopMode/Factory","all", restart module.')
        test.expect(test.dut.dstl_reset_to_factory_default())

        test.log.info('5. Check if clock and date have been reset to default values.')
        test.dut.at1.send_and_verify('at+cclk?')
        test.expect(default_time in test.dut.at1.last_response)


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
