#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092208.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class EMERG_RST_Internetconn(BaseTest):
    """
    TC0092208.001 - EMERG_RST_InternetConn

    Special Equipment: MCTEST3/4
    Author: xiaoyu.chen@thalesgroup.com
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()

    def run(test):
        test.log.info('1. Power on and send at command')
        test.expect(test.dut.at1.send_and_verify('ATI','OK'))

        test.log.info('2. Establish dial up on module')
        test.expect(test.dut.at1.send_and_verify('ATD*99#', 'CONNECT'))

        test.log.info('3. Check the connection and transfer data to the internet')
        test.expect(test.dut.at1.wait_for('.*NO CARRIER.*',timeout=60))
        test.expect(test.dut.at1.send_and_verify('ATD*99#', 'CONNECT'))

        test.log.info('4. Connect EMERG_RST pin of the module with the ground pin on DSB75')
        test.expect(test.dut.devboard.send_and_verify('mc:emergoff=1', 'OK'))

        test.log.info('5. Check that internet connection is hung up and data transfer ended, no URC pop up ')
        test.expect(test.dut.at1.wait_for('.*NO CARRIER.*',timeout=60)==False)
        test.dut.at1.send('AT',end="\r\n")
        test.sleep(10)
        test.expect('.*OK.*' not in test.dut.at1.read())

        test.log.info('6. Disconnect EMERG_RST pin of the module with the ground pin on DSB75. ')
        test.expect(test.dut.devboard.send_and_verify('mc:emergoff=0', 'OK'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.sleep(3)

        test.log.info('7. Check that module is working, sending AT command and can set dial up again normally. ')
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
        test.expect(test.dut.dstl_register_to_network())

    def cleanup(test):
        pass

if "__main__" == __name__:
        unicorn.main()
