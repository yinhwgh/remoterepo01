# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0000480.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    '''
    TC0000480.001 - TpCColpFunc
    Intention:
    Check status of COLP (Connected Line Identification Presentation) via *#76#
    Subscriber: 3
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r2.dstl_detect()
        test.r2.dstl_register_to_network()
        test.sleep(3)

    def run(test):
        nat_dut_phone_num = test.dut.sim.nat_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr
        nat_r2_phone_num = test.r2.sim.nat_voice_nr

        test.log.step('1.register subscriber 3 and activate call forwarding (register service) at subscriber 2.')
        test.expect(test.r1.at1.send_and_verify('at+ccfc=4,4', 'OK|ERROR'))
        test.sleep(3)
        test.expect(test.r1.at1.send_and_verify('at+ccfc=0,2', 'CCFC: 0,1'))
        test.expect(test.r1.at1.send_and_verify(f'at+ccfc=0,3,"{nat_r2_phone_num}",129,1', 'OK'))

        test.log.step('2.query call forwarding at subscriber 2')
        test.expect(test.r1.at1.send_and_verify('at+ccfc=0,2',
                                                f'\+CCFC: 1,1,"{nat_r2_phone_num}",129.*OK.*'))
        test.log.step('3.trying test, write and read command')
        test.expect(test.dut.at1.send_and_verify('at+colp=?', '.*\+COLP: \(0[,-]1\).*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp=0', '.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 0,[012]\s+.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp=1', '.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 1,[012]\s+.*OK.*', timeout=15))

        test.log.step('4.check status with atd*#76#')
        test.expect(test.dut.at1.send_and_verify('atd*#76#;', '.*\+COLP: 1,[012]\s+.*OK.*', timeout=15))

        test.log.step('5.connection from subscriber 1 to subscriber 2,subscriber 2 is forwarding call to subscriber 3')
        test.expect(test.dut.at1.send_and_verify(f'atd{nat_r1_phone_num};', ''))
        test.expect(test.r2.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.r2.at1.send_and_verify('ata'))
        test.expect(test.dut.at1.wait_for(f'.*\+COLP: .*{nat_r1_phone_num}.*'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+clcc', f'CLCC: 1,0,0,0,0,"{nat_r1_phone_num}"'))
        test.expect(test.r2.at1.send_and_verify('at+clcc', f'CLCC: 1,1,0,0,0,"{nat_dut_phone_num}"'))
        test.expect(test.r2.dstl_release_call())

        test.log.step('6.reset to default values ( subscriber 2: disable call forwarding )')
        test.expect(test.dut.at1.send_and_verify('at+colp=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 0,[012]\s+.*OK.*', timeout=15))
        test.expect(test.r1.at1.send_and_verify('at+ccfc=4,4', 'OK|ERROR'))
        test.sleep(3)
        test.expect(test.r1.at1.send_and_verify('at+ccfc=0,2', 'CCFC: 0,1'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
