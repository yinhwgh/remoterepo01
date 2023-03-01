#responsible: xiaolin.liu@thalesgroup.com
#location: Dalian
#TC0094323.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context
from dstl.security.lock_unlock_sim import dstl_unlock_sim,dstl_lock_sim

class Test(BaseTest):
    """
    TC0094323.001 - TpAtCgtftBasic
    This procedure provides the possibility of basic tests for the test, read and write command of +CGTFT

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):
        maxcid = test.dut.dstl_get_supported_max_cid()
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))


        test.log.step('1.check test, read and write commands without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cgtft=?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft?', '.*OK.*'))

        test.log.step('2.check test, read and write commands with PIN')
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('at+cgtft=?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft?', '.*OK.*'))


        test.log.step('3.check command with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+cgtft=@#', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(f'at+cgtft={maxcid+1}', '.*ERROR.*'))


        test.log.step('4.function check')
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify(f'at+cgdcont=1,"IP","{test.dut.sim.apn_v4}"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft= 1,1,0,"8.8.8.8.255.255.255.255" ', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgtft? ', '\+CGTFT: 1,1,0,"8.8.8.8.255.255.255.255",0,0.0,0.0,0,0.0,0'))


    def cleanup(test):
        pass






if __name__ == "__main__":
    unicorn.main()