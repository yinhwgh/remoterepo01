# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0095162.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.security import set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    TC0095162.001 - TpAtVzwMruBasic
    This procedure provides the possibility basic tests for commands
    Clear MRU: AT$QCMRUC
    Query MRU contents:	AT$QCMRUE?
    Write GWL: AT$QCMRUE=<Record Index>, <RAT>, <BAND>, <PLMN ID>

    """
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        pass

    def run(test):
        exp_err_result = 'ERROR'
        if test.dut.project is 'VIPER':
            exp_err_result = '.*OK.*'

        test.log.info('1. Restart the modul with command (At+Cfun=1,1) and wait for URC ^SYSSTART')
        test.expect(test.dut.dstl_restart())
        test.sleep(7)
        test.log.info('2. Check test command (At$QCMRUE=?) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUE=?', exp_err_result))
        test.log.info('3. Check read command (At$QCMRUE?) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUE?', exp_err_result))
        test.log.info('4. Check exec command (At$QCMRUE) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUE', exp_err_result))
        test.log.info('5. Check write command (At$QCMRUE=) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUE=2,2,0,"00000"', exp_err_result))
        test.log.info('6. Check test command (At$QCMRUC=?) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUC=?', exp_err_result))
        test.log.info('7. Check read command (At$QCMRUC?) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUC?', exp_err_result))
        test.log.info('8. Check exec command (At$QCMRUC) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUC', exp_err_result))

        test.log.info('9. Enter the PIN')
        test.dut.dstl_enter_pin()
        test.log.info('10. Check test command (At$QCMRUE=?)')
        test.expect(test.dut.at1.send_and_verify('AT$QCMRUE=?', 'OK'))
        test.log.info('11. Check read command (At$QCMRUE?)')
        test.expect(test.dut.at1.send_and_verify('AT$QCMRUE?', '\\$QCMRUE:.*OK.*'))
        test.log.info('12. Check exec command (At$QCMRUE)')
        test.expect(test.dut.at1.send_and_verify('AT$QCMRUE', 'OK'))
        test.log.info('13. Check write command (At$QCMRUE=)')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUE=1,2,0,"00000"', 'OK'))
        test.sleep(3)
        test.log.info('14. Check read command (At$QCMRUE?)')
        test.expect(test.dut.at1.send_and_verify('AT$QCMRUE?', '\\$QCMRUE:.*1,2,"0","00000".*OK.*'))
        test.log.info('15. Check test command (At$QCMRUC=?) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUC=?', exp_err_result))
        test.log.info('16. Check read command (At$QCMRUC?) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUC?', exp_err_result))
        test.log.info('17. Check exec command (At$QCMRUC) ')
        test.expect(test.dut.at1.send_and_verify('At$QCMRUC', 'OK'))
        test.sleep(3)
        pass

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
