#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092919.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.configuration import functionality_modes
from dstl.auxiliary.devboard import devboard

class Test(BaseTest):
    '''
    TC0092919.001 - TpAtScfgAirplaneMode
    This procedure tests the SCFG=MEopMode/cfun command and
    check the Startup behavior with SIM with PIN and w/o PIN
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='OK'))

    def run(test):

        test.log.info('1.1 basis tests without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","1"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN"', '.*"MEopMode/CFUN","1".*.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","0"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN"', '.*"MEopMode/CFUN","0".*.*OK.*'))

        test.log.info('1.2 basis tests with pin')
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","1"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN"', '.*"MEopMode/CFUN","1".*.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","0"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN"', '.*"MEopMode/CFUN","0".*.*OK.*'))

        test.log.info('2. activate Airplane mode at startup')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.dut.at1.send_and_verify('AT^SMSO', expect='.*OK.*', wait_for='SHUTDOWN'))
        test.sleep(2)
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
        test.expect(test.dut.at1.wait_for('\^SYSSTART'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CFUN?', expect='CFUN: 4'))

        test.log.info('3. set back all settings')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","0"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_restart())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CFUN?', expect='CFUN: 1'))


    def cleanup(test):
        pass



if '__main__' == __name__:
    unicorn.main()
