"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
intention:  Minimum GNSS Elevation Angle (5-45 degrees) is configurable
LM-No (if known):
used eq.: DUT-At1,
execution time (appr.): 25 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):
        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        for n in range(1):
            test.log.step('Step 2: Configure GNSS start mode without assistance data - Start')
            test.dut.dstl_collect_result('Step 2: Configure GNSS start mode without assistance data', test.dut.at1.send_and_verify("at^SGPSC=\"Engine/StartMode\", \""+str(n)+"\"","OK"))

            test.log.step('Step 3: Configure  LTE context and nonip context  - Start')
            test.dut.dstl_collect_result('Step 3: Configure  LTE context and nonip context ', test.dut.at1.send_and_verify("at+cgdcont=1, \"IPv4v6\", \"ber7.ericsson\"","OK") and test.dut.at1.send_and_verify("at+CGDCONT=3,\"Non-IP\",\"ber-nonip.ericsson\"", "OK"))

            test.log.step('Step 4: Restart Module  - Start')
            test.dut.dstl_collect_result('Step 4: Restart Module', test.dut.dstl_restart())
            test.sleep(20)
            test.dut.at1.send_and_verify('at+cpin=1234', 'OK')

            for stop in range(3):
                if(stop == 0):
                    test.dut.at1.send_and_verify("at+cops=0", "OK")
                elif(stop==1):
                    test.dut.at1.send_and_verify("at+cops=2", "OK")
                    test.dut.at1.send_and_verify("at+cops=0", "OK")
                elif(stop==2):
                    test.dut.at1.send_and_verify("at+cops=,,,9", "OK")

                test.sleep(120)

                test.dut.at1.send_and_verify("at^smoni",".NB,")

                if "NB" in test.dut.at1.last_response:
                    break

            test.log.step('Step 5: Ue is attach to network (NBIOT)  - Start')
            test.dut.dstl_collect_result('Step 5: Ue is attach to network (NBIOT)',
                                         test.dut.at1.send_and_verify("at^smoni", ".NB,"))

            for x in range(1,3):
                if(x==1):
                    test.log.step('Step 6: Configure GNSS operation to higher priority than LTE - Start')
                    test.dut.dstl_collect_result('Step 6: Configure GNSS operation to higher priority than LTE', test.dut.at1.send_and_verify("at^SCFG=\"MEopMode/RscMgmt/Rrc\",\"1\"", "OK"))
                else:
                    test.log.step('Step 6: Configure LTE operation to higher priority than GNSS - Start')
                    test.dut.dstl_collect_result('Step 6: Configure LTE operation to higher priority than GNSS', test.dut.at1.send_and_verify( "at^SCFG=\"MEopMode/RscMgmt/Rrc\",\"2\"", "OK"))

                test.log.step('Step 7: Enable eDRX mode with Request_eDRX = 163.84 sec  - Start')
                test.dut.dstl_collect_result('Step 7: Enable eDRX mode with Request_eDRX = 163.84 sec ', test.dut.at1.send_and_verify("at+cedrxs=2,5,1001", "OK"))

                test.log.step('Step 8: Request_paging_time_window = 5,12 sec (0011)  - Start')
                test.dut.dstl_collect_result('Step 8: Request_paging_time_window = 5,12 sec (0011) ', test.dut.at1.send_and_verify("at^sedrxs=2,5,1001,0011","OK"))

                test.log.step('Step 9:  Check the eDrx parameters which is accept /reject by the network  - Start')
                test.dut.dstl_collect_result('Step 9:  Check the eDrx parameters which is accept /reject by the network ', test.dut.at1.send_and_verify("at+cedrxrdp", "+CEDRXRDP: 5,\"1001\",\"1001\",\"0011\""))

                test.dut.at1.send_and_verify("at+csodcp=3,60,777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777","OK")
                test.sleep(10)

                test.log.step('Step 10: Switch on  GNSS engine - Start')
                test.dut.dstl_collect_result('Step 10: Switch on  GNSS engine', test.dut.dstl_switch_on_engine(3))

                while("Engine\",\"0\"" in test.dut.at1.last_response):
                    test.dut.at1.read()
                    test.log.step('Step 10: Switch on  GNSS engine - Start')
                    test.sleep(5)
                    test.dut.dstl_switch_on_engine(3)

                test.dut.dstl_collect_result('Step 10: Switch on  GNSS engine', True)


                for i in range(1,4):
                    test.log.step('Step 11.'+str(i)+': Wait for first fix position - Start')
                    test.dut.dstl_collect_result('Step 11.'+str(i)+': Wait for first fix position', test.dut.dstl_check_ttff() < 90)

                    test.log.step('Step 12.' + str(i) + ': Determine TTFF - Start')
                    test.dut.dstl_collect_result('Step 12.' + str(i) + ': Determine TTFF', test.dut.dstl_check_ttff() < 32)

                    test.log.step('Step 13.' + str(i) + ': GNSS running for 3 minutes - Start')
                    test.sleep(180)
                    test.dut.dstl_collect_result('Step 13.' + str(i) + ':GNSS running for 3 minutes', True)

                    test.dut.at1.read()

                    test.log.step('Step 14.'+str(i)+': Send NON-IP data with the length of 60 octets - Start')
                    test.dut.dstl_collect_result('Step 14.'+str(i)+': Send NON-IP data with the length of 60 octets', test.dut.at1.send_and_verify("at+csodcp=3,60,777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777","OK"))

                    test.log.step('Step 15.'+str(i)+': .Check fix position with NMEA data - Start')
                    test.dut.dstl_collect_result('Step 15.'+str(i)+': .Check fix position with NMEA data', test.dut.dstl_check_ttff() != 0)

                test.log.step('Step 16: Switch off GNSS engine - Start')
                test.dut.dstl_collect_result('Step 16: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

    def cleanup(test):
        test.log.step('Step 16: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 16: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.dut.nmea.read()
        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
