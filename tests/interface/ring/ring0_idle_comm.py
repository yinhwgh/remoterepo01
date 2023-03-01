# responsible: dan.liu@thalesgroup.com
# location: Dalian
# TC0095659.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.devboard import devboard
from dstl.configuration.functionality_modes import dstl_set_minimum_functionality_mode
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.auxiliary.check_urc import dstl_check_urc
from core import dstl


class Test(BaseTest):
    ''' TC0095659.001 - Ring0IdleComm

    Intention :Check functionality of RING0 line of idle communication interface.

    '''

    def setup(test):
        test.dut.dstl_detect()
        if test.dut.project.upper() == "COUGAR|BOXWOOD":
            test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","std"', 'OK')
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"', 'OK')
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime",2', 'OK')
        test.dut.dstl_restart()
        test.sleep(2)
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline"', '.*local.*')
        test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime"', '.*2.*')

    def run(test):
        test.dut.devboard.read()
        test.log.info('1.Enter pin ')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.log.info('2. Enable CEREG urc')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=1', ".*OK.*"))
        test.log.info('3. Issue ringline by CEREG URC')
        test.issue_ringline_local_by_cereg()
        test.log.info('4. Disble ringline URC in SCFG')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"', 'OK'))
        test.log.info('5.Restart module')
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        test.dut.devboard.read()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline"', '.*off.*'))
        test.log.info('6.Enter pin')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.log.info('7. Enbale CEREG URC')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=1', ".*OK.*"))
        test.log.info('8. Issue Ringline by CEREG URC')
        test.issue_ringline_off_by_cereg()

    def issue_ringline_local_by_cereg(test):
        test.check_cfun()
        test.expect(test.dut.dstl_set_minimum_functionality_mode())
        test.expect(test.dut.dstl_check_urc(expect_urc='\+CEREG: \d'))
        test.expect(test.dut.devboard.wait_for('URC:  RINGline: 0'))
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc(expect_urc='\+CEREG: \d'))
        test.expect(test.dut.devboard.wait_for('URC:  RINGline: 0'))

    def issue_ringline_off_by_cereg(test):
        test.check_cfun()
        test.expect(test.dut.dstl_set_minimum_functionality_mode())
        test.expect(test.dut.dstl_check_urc(expect_urc='\+CEREG: \d'))
        test.expect(test.dut.devboard.wait_for('URC:  RINGline: 0')==False)
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc(expect_urc='\+CEREG: \d'))
        test.expect(test.dut.devboard.wait_for('URC:  RINGline: 0')==False)

    def check_cfun(test):
        test.expect(test.dut.at1.send_and_verify('at+cfun=1', '.*OK.*'))

    def cleanup(test):

        pass


if "__main__" == __name__:
    unicorn.main()
