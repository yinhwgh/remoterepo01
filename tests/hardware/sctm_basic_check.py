#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091811.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class EMERG_RST_IdleState(BaseTest):
    """
    TC0091811.001 - TpAtSctmBasic

    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):

        test.log.info('1. Check command without and with PIN')
        test.expect(test.dut.at1.send_and_verify('at+cpin?','SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=?', 'SCTM: (0,1)'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 0,0'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=0', 'OK'))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at^sctm=?', 'SCTM: (0,1)'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 0,0'))

        test.log.info('2. Check all parameters and also with invalid values')
        test.expect(test.dut.at1.send_and_verify('at^sctm=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 1,0'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 0,0'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 1,0'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 1,0,\d+'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=0,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 0,0'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=0,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 0,0,\d+'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^sctm=', 'ERROR'))

        test.log.info('3. Check display of temperature')
        test.expect(test.dut.at1.send_and_verify('at^sctm=?', 'SCTM: \(0,1\),\(-\d+ .. \d+\)'))
        test.expect(test.dut.at1.send_and_verify('at^sctm?', 'SCTM: 0,0,\d+'))


    def cleanup(test):
        pass

if "__main__" == __name__:
        unicorn.main()
