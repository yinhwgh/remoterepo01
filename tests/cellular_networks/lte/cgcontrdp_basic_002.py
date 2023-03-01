#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088220.002

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context


class Test(BaseTest):
    """
    TC0088220.002 - CgcontrdpBasic_Dahlia
    Check the basic functionality of the AT command AT+CGCONTRDP

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?','SIM PIN'))

    def run(test):
        maxcid= test.dut.dstl_get_supported_max_cid()
        apn1 = test.dut.sim.gprs_apn
        apn2 = test.dut.sim.gprs_apn_2

        test.log.info('1.enter the test command (shall be rejected)')
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=?', '.*CME ERROR: SIM PIN required.*'))

        test.log.info('2.enter the write command (shall be rejected)')
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=1', '.*CME ERROR: SIM PIN required.*'))

        test.log.info('3.enter the execute command (shall be rejected)')
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP', '.*CME ERROR: SIM PIN required.*'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1,"IP","{apn1}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=2,"IP","{apn2}"', 'OK'))
        test.log.info('4.enter the PIN')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(10)

        test.log.info('5.activate the PDP context')
        test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,2', 'OK'))

        test.log.info('6.enter the test command (a list of the activated PDP contexts shall be returned)')
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=?', '.*\+CGCONTRDP: \(1,2\).*'))

        test.log.info('7.enter the execute command (the dynamic parameters for all activated PDP contexts shall be returned)')
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP', '.*\+CGCONTRDP: 1,\d.*\+CGCONTRDP: 2,\d.*'))

        test.log.info('8.enter the write command for each PDP context(1 possible) (the dynamic parameters for each respective '\
                      'PDP context shall be displayed if that context is active, otherwise OK only)')
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=1', '.*\+CGCONTRDP: 1,\d.*'))

        test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=4,"IP","{apn1}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=4', '^.*4\s+OK\s$'))

        test.expect(test.dut.dstl_delete_pdp_context(5))
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=5', '^.*5\s+OK\s$'))

        test.log.info('9.enter several illegal parameter values for the write command (shall be rejected)')
        test.expect(test.dut.at1.send_and_verify(f'AT+CGCONTRDP={maxcid+1}', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=0', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGCONTRDP=-1', '.*ERROR.*'))

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
