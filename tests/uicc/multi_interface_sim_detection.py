#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0095818.001 - MultiInterfaceSimDetection

"""
check setting commands for query sim status is independent of interface

NOTE: as VIPER does not support ^SIND: simtray, there are not codes to check it.

"""


import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import *



class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        time.sleep(2)

    def run(test):
        test.log.info('**** MutliInterface SIM Detection - Start ****')
        for i in range(2):
            if i==1:
                test.dut.at1 = test.dut.mux_1
                test.dut.at1.open()
                test.dut.at2 = test.dut.mux_2
                test.dut.at2.open()
            test.log.step('*'+('1. ASC0 'if (i == 0) else '5. Mux1 ') +': AT^SCKS=1')
            test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCKS?", "\^SCKS: 1,1.*OK.*"))

            test.log.step('*'+('2. ASC1 'if (i == 0) else '6. Mux2 ') +': query the status')
            test.expect(test.dut.at2.send_and_verify("AT^SCKS?", "\^SCKS: 0,1.*OK.*"))

            test.log.step('*'+('3.'if (i == 0) else '7.') +' Remove SIM : query the status')
            test.dut.dstl_remove_sim()
            test.log.info('**** '+('ASC0 'if (i == 0) else 'Mux1 ') +': urc pop up ****')
            test.expect("^SCKS: 0" in test.dut.at1.last_response)
            test.log.info('**** '+('ASC1 'if (i == 0) else 'Mux2 ') +': query the status  ****')
            test.expect(test.dut.at2.send_and_verify("AT^SCKS?", "\^SCKS: 0,0.*OK.*"))
            test.log.info('**** USB : query the status  ****')
            test.expect(test.dut.at3.send_and_verify("AT^SCKS?", "\^SCKS: 0,0.*OK.*"))

            test.log.step('*'+('4.'if (i == 0) else '8.') +' Insert SIM : query the status')
            test.dut.dstl_insert_sim()
            test.log.info('**** '+('ASC0 'if (i == 0) else 'Mux1 ') +': urc pop up ****')
            test.expect("^SCKS: 1" in test.dut.at1.last_response)
            test.log.info('**** '+('ASC1 'if (i == 0) else 'Mux2 ') +': query the status  ****')
            test.expect(test.dut.at2.send_and_verify("AT^SCKS?", "\^SCKS: 0,1.*OK.*"))
            test.log.info('**** USB : query the status  ****')
            test.expect(test.dut.at3.send_and_verify("AT^SCKS?", "\^SCKS: 0,1.*OK.*"))
            test.dut.at1.close()
            test.dut.at2.close()

        test.log.info('**** Test end ***')


    def cleanup(test):
        pass



if (__name__ == "__main__"):
    unicorn.main()
