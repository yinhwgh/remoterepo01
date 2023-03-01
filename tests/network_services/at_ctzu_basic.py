#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091864.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock

class Test(BaseTest):
    '''
    TC0091864.001 - TpAtCtzuBasic
    Subscriber :1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):

        test.log.step('1.Test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=?', '\+CTZU: \(0-1\)'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU?', '\+CTZU: [0|1]'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU?', '\+CTZU: 0'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU?', '\+CTZU: 1'))

        test.log.step('2.Test with pin')
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=?', '\+CTZU: \(0-1\)'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU?', '\+CTZU: [0|1]'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU?', '\+CTZU: 0'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU?', '\+CTZU: 1'))

        test.log.step('3.Test invalid parameter')
        test.expect(test.dut.at1.send_and_verify('AT+CTZU', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=', 'ERROR'))

        test.log.step('4.Check functionality at the testnetwork')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', '.*OK.*'))
        test.expect(test.dut.dstl_set_real_time_clock(time="20/05/05,08:34:27"))
        test.expect(test.dut.at1.send_and_verify('AT+CTZR=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('CTZU:'))

        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', '.*OK.*'))
        test.expect(test.dut.dstl_set_real_time_clock(time="20/05/05,08:34:27"))
        test.expect(test.dut.at1.send_and_verify('AT+CTZR=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('CTZU:')==False)


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
