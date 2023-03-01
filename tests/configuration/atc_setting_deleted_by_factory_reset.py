#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0104490.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import set_user_profile
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    '''
    TC0104490.001 - ATCommandSettingDeletedByFactoryReset
    This test case is design to check whether AT command settings are restored to their
    default values after the AT command AT^SCFG="MEopMode/Factory","all".

    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.sleep(3)

    def run(test):
        test.log.info('1. Change at command settings storable with AT&W for non-default values.')
        test.expect(test.dut.dstl_set_at_storable_to_none_default())
        test.log.info('2. Display current configuration AT&V')
        test.expect(test.dut.dstl_check_at_storable_is_none_default())
        test.log.info('3. Store AT Command settings to User Defined Profile AT&W')
        test.expect(test.dut.at1.send_and_verify('at&w'))

        test.log.info('4. Execute AT^SCFG="MEopMode/Factory","all"')
        test.expect(test.dut.dstl_reset_to_factory_default())
        test.dut.dstl_enter_pin()
        test.sleep(3)

        test.log.info('5. Check if the parameters have been reset to default values')
        test.expect(test.dut.dstl_check_at_storable_is_default())

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('atv1','OK'))
        test.expect(test.dut.at1.send_and_verify('at&f','OK'))
        test.expect(test.dut.dstl_check_at_storable_is_default())
        test.expect(test.dut.at1.send_and_verify('at&W', 'OK'))


if "__main__" == __name__:
    unicorn.main()
