#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091672.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary.devboard import devboard


class EmergOff(BaseTest):
    """
    TC0091672.001 - TpEmergOff
    Special Equipment: McTest3
    Author: xiaoyu.chen@thalesgroup.com
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info('1. Power down module via pin Emergency Off.')
        if 'MC-Test3' not in test.dut.dstl_get_dev_board_version():
            test.log.error('McTest3 is needed for this case.')
            test.fail()

        test.expect(test.dut.at1.send_and_verify('ATI','OK'))
        test.expect(test.dut.devboard.send_and_verify('at^mcswitch=7,1', 'OK'))

        test.log.info('2. With McTest the signal VEXT is verified before and after EmergOff.')
        test.dut.at1.send('AT',end="\r\n")
        test.sleep(10)
        test.expect('.*OK.*' not in test.dut.at1.read())
        test.log.info(test.dut.platform)
        test.log.info('3. Then the module is switched on again via DTR-toggle or additional start impulse from McTest.')
        test.expect(test.dut.devboard.send_and_verify('at^mcswitch=7,0', 'OK'))
        if test.dut.platform == 'QCT' or test.dut.platform == 'UNISOC':
            test.dut.devboard.send_and_verify('at^mcign=4000','.*OK.*')
        test.dut.at1.wait_for('.*SYSSTART.*',timeout= 60)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))


    def cleanup(test):
        pass

if "__main__" == __name__:
        unicorn.main()
