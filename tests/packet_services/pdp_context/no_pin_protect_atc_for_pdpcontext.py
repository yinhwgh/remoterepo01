# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0092662.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.security import set_sim_waiting_for_pin1
from dstl.configuration import functionality_modes


class Test(BaseTest):
    '''
    TC0092662.001 - NoPinProtectedCommandsForPdpContext
    Intention: To check if context commands works without PIN
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()

    def run(test):

        test.log.info('***Test Start***')

        test.log.step('1.Check if test, read and write commands works without PIN')
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*\+CPIN: SIM PIN.*"))
        test.check_without_pin()

        test.log.step('2.Check if test, read and write commands in airplane mode')
        test.dut.dstl_set_airplane_mode()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*\+CPIN: SIM PIN.*"))
        test.check_without_pin()



    def cleanup(test):
        test.log.info('***Test End***')
        test.dut.dstl_set_full_functionality_mode()

    def check_without_pin(test):
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3,"IP","internet"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=?', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGTFT?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGTFT=1', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGQREQ?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGQREQ=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGQREQ=1', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGEQREQ?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQREQ=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQREQ=1', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=1', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS=1', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=1', 'OK'))


if "__main__" == __name__:
    unicorn.main()
