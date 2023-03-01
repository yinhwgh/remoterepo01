#responsible: dan.liu@thalesgroup.com
#location: Dalian
#TC0088045.001


import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard import devboard
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary.check_urc import dstl_check_urc

class copsbeforepin(BaseTest):
    '''
    TC0088045.001 - TpCopsBeforePin
    Intention :Check command at+cops behaviour before enter pin

    '''

    def setup(test):

        test.expect(test.dut.at1.send_and_verify("at", ".*OK.*"))
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):

        test.log.info("start module without sim")
        test.expect(test.dut.at1.send_and_verify("at+creg=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*SIM PIN.*"))
        test.expect(test.dut.dstl_remove_sim())
        test.expect(test.dut.at1.send_and_verify("at+cops=?", ".*SIM not inserted.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*SIM not inserted.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*SIM not inserted.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=3,1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=3,2", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=1,2,12345,0", ".*OK.*"))
        test.log.info("insert sim")
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.at1.send_and_verify("at+creg=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=?", ".*SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=1,2,12345,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*SIM PIN.*"))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("at+cops=0", ".*OK.*"))
        test.expect(test.dut.dstl_check_urc('CREG: 1'))

    def cleanup(test):
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '.*SIM PIN|READY'))


if "__main__" == __name__:
    unicorn.main()