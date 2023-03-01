#responsible: dan.liu@thalesgroup.com
#location: Dalian
#TC0095625.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes

class Readcommandccid(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.info('1.Check pin status')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?','SIM PIN'))
        test.log.info('2.send ccid command')
        test.read_ccid()
        test.log.info('3.Enter pin')
        test.expect(test.dut.dstl_enter_pin())
        test.log.info('4.Send ccid command')
        test.read_ccid()
        test.log.info('5.Enter airplane mode')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.log.info('6.Send ccid command')
        test.read_ccid()
        test.expect(test.dut.at1.send_and_verify('at+ccid', '\+CCID:\s\d{12,20}\s'))
        test.log.info('7.Back to full mode')
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.log.info('8. Restart module')
        test.expect(test.dut.dstl_restart())
        test.log.info('9.Check pin status')
        test.expect(test.dut.at1.send_and_verify('at+cpin?','SIM PIN'))
        test.log.info('10.Enter airpalne mode')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.log.info('11.Send ccid command')
        test.read_ccid()
        test.expect(test.dut.at1.send_and_verify('at+ccid', '\+CCID:\s\d{12,20}\s'))
        test.log.info('12.Back to full mode')
        test.expect(test.dut.dstl_set_full_functionality_mode())

    def read_ccid(test):
        iccid_from_sim_cfg = test.dut.sim.kartennummer_gedruckt
        if (iccid_from_sim_cfg != 'None'):
            response = '.*CCID:.*' + iccid_from_sim_cfg + '.*OK.*'
        else:
            response = '.*CCID:.*(8986|891|8901|8948|8949).*OK.*'

        test.expect(test.dut.at1.send_and_verify("AT+CCID=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CCID", response))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CCID=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CCID", response))

    def cleanup(test):
       pass


if "__main__" == __name__:
    unicorn.main()



