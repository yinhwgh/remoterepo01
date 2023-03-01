"""
author: katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number:  TC0094096.002 - TpMultiplePDPContexts
intention:  2 PDP context for each serial port (or virtual serial port) can be active by Qos setting
LM-No (if known): LM0002581.001 - Multiple Persistent PDP Contexts
                  LM0003195.004 - Configuration of Secondary PDP Contexts
                  LM0004783.001 - Multiple PDP Context
                  developed/tested for/with Viper
used eq.: ASC0 and second intreface ASC1 or USB
execution time (appr.): ?? min

    N O T   R E A D Y !!!!
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.gnss.gnss import *


class Test(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_register_to_network()
        test.dut.at1.send_and_verify("at+cmee=2",".*OK.*")
        test.dut.at1.send_and_verify("at+creg=2",".*OK.*")
        test.dut.at1.send_and_verify("at+cops?",".*COPS: .*,.*,.*,[02367].*OK.*")



    def run(test):
        rat_list = [["GSM",0,"03"], ["UMTS",2,"246"] , ["LTE",7,"7"]]

        for i in range(len(rat_list)):

            test.log.step('Step 1.' + str(i+1) + ': Change RAT to \'' + rat_list[i][0] + '\' - Start')
            test.dut.dstl_collect_result('Step 1.' + str(i+1) + ': Change RAT to \'' + rat_list[i][0] + '\' ',
                                         test.dut.at1.send_and_verify("at+cops=,,," + str(rat_list[i][1]), "OK", timeout=30))

            test.sleep(5)

            test.dut.at1.verify_or_wait_for(".*CREG: 1,.*,.*," + str(rat_list[i][2] ))

            test.log.step('Step 2.' + str(i+1) + ': Activate GPRS attach - Start')
            test.dut.dstl_collect_result('Step 2.' + str(i+1) + ': Activate GPRS attach', test.dut.at1.send_and_verify("at+cgatt=1","OK"))

            test.log.step('Step 3.' + str(i+1) + ': Check RAT \'' + rat_list[i][0] + '\' - Start')
            test.dut.dstl_collect_result('Step 3.' + str(i+1) + ': Check RAT \'' + rat_list[i][0] + '\' ',
                                         test.dut.at1.send_and_verify("at+cops?", "COPS: .*,.*,.*,["+ rat_list[i][2] + "].*OK.*", timeout=30))


            test.log.step('Step 4.' + str(i+1) + ': Show smoni - Start')
            test.dut.dstl_collect_result('Step 4.' + str(i+1) + ': Show smoni', test.dut.at1.send_and_verify("at^smoni"))


            test.log.step('Step 5.' + str(i+1) + ': Define primary PDP context through ASC0 - Start')
            test.dut.dstl_collect_result('Step 5.' + str(i+1) + ': Define primary PDP context through ASC0', test.dut.at1.send_and_verify("at+cgdcont=1,\"IP\",\"ber1.ericsson\""))

            test.log.step('Step 6.' + str(i+1) + ': Define secondary PDP context on second interface (ASC/USBx) - Start')
            test.dut.dstl_collect_result('Step 6.' + str(i+1) + ': Define secondary PDP context on second interface (ASC/USBx)', test.dut.at2.send_and_verify("at+cgdscont=5,1"))

            test.log.step('Step 7.' + str(i+1) + '.1: Set default value for Qos Profile minimum acceptable - Start')
            test.dut.dstl_collect_result('Step 7.' + str(i+1) + '.1: Set default value for Qos Profile minimum acceptable', test.dut.at1.send_and_verify("at+cgeqos=1,1,1,1,1,1"))

            test.log.step('Step 7.' + str(i+1) + '.2: Set default value for Qos Profile minimum acceptable (2nd context) - Start')
            test.dut.dstl_collect_result('Step 7.' + str(i+1) + '.2: Set default value for Qos Profile minimum acceptable (2nd context)', test.dut.at1.send_and_verify("at+cgeqos=5,1,1,1,1,1"))


            test.log.step('Step 8.' + str(i+1) + '.1: Set any value for Qos profile requested - Start')
            test.dut.dstl_collect_result('Step 8.' + str(i+1) + '.1: Set any value for Qos profile requested', test.dut.at1.send_and_verify("at+cgeqos=1,1,64,64,128,128"))

            test.log.step('Step 8.' + str(i+1) + '.2: Set any value for Qos profile requested (2nd context) - Start')
            test.dut.dstl_collect_result('Step 8.' + str(i+1) + '.2: Set any value for Qos profile requested (2nd context)', test.dut.at1.send_and_verify("at+cgeqos=5,1,64,64,128,128"))

            test.log.step('Step 9: Set traffic flow template - Start')
            test.dut.dstl_collect_result('Step 9.' + str(i+1) + ': Set traffic flow template', test.dut.at1.send_and_verify("at+cgtft=5,1,0,\"8.8.8.8.255.255.255.255\""))

            test.log.step('Step 10.' + str(i+1) + ': Activate PDP context 1 - Start')
            test.dut.dstl_collect_result('Step 10.' + str(i+1) + ': Activate PDP context 1', test.dut.at1.send_and_verify("at+cgact=1,1"))

            test.log.step('Step 11.' + str(i+1) + ': Activate PDP context 5 on second interface (ASC/USBx)- Start')
            test.dut.dstl_collect_result('Step 11.' + str(i+1) + ': Activate PDP context 5 on second interface (ASC/USBx)', test.dut.at2.send_and_verify("at+cgact=1,5"))

            test.log.step('Step 12.' + str(i+1) + '.' + str(i+1) + ': Show PDP address - Start')
            test.dut.dstl_collect_result('Step 12.' + str(i+1) + ': Show PDP address', test.dut.at1.send_and_verify("at+cgpaddr"))

            test.log.step('Step 13.' + str(i+1) + ': Show secondary PDP context read dynamic parameters - Start')
            test.dut.dstl_collect_result('Step 13.' + str(i+1) + ': Show secondary PDP context read dynamic parameters', test.dut.at1.send_and_verify("at+cgscontrdp=5","CGSCONTRDP: 5,1"))

            test.log.step('Step 14.' + str(i+1) + ': Deactivate GPRS attach - Start')
            test.dut.dstl_collect_result('Step 14.' + str(i+1) + ': Deactivate GPRS attach', test.dut.at1.send_and_verify("at+cgatt=0","OK"))



    def cleanup(test):
        test.dut.at1.send_and_verify("at+cops=2", ".*OK.*")
        test.dut.at1.send_and_verify("at+cops=0", ".*OK.*")
        test.dut.dstl_register_to_network()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
