#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092205.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class EMERG_RST_IdleState(BaseTest):
    """
    TC0092205.001 - EMERG_RST_IdleState

    Special Equipment: MCTEST3/4
    Author: xiaoyu.chen@thalesgroup.com
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):

        test.log.info('1. Power on and send at command')
        test.expect(test.dut.at1.send_and_verify('ATI','OK'))
        test.dut.dstl_register_to_network()
        test.sleep(150)
        test.attempt(test.dut.at1.send_and_verify,'at^smoni',wait_for='NOCONN',retry=5,sleep=10)

        test.log.info('2. Connect EMERG_RST pin with the ground pin on DSB75, module should be switched off')
        test.expect(test.dut.devboard.send_and_verify('mc:emergoff=1', 'OK'))

        test.log.info('3. Try to send AT command to the module, there should be no response')
        test.dut.at1.send('AT',end="\r\n")
        test.sleep(10)
        test.expect('.*OK.*' not in test.dut.at1.read())

        test.log.info('4. hen disconnect EMERG_RST pin with ground pin, module is switched on.')
        test.expect(test.dut.devboard.send_and_verify('mc:emergoff=0', 'OK'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.sleep(3)

        test.log.info('5. Check that module is working, sending AT command and attaching to the network. ')
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
        test.expect(test.dut.dstl_register_to_network())


    def cleanup(test):
        pass

if "__main__" == __name__:
        unicorn.main()
