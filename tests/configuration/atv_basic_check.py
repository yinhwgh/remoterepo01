# responsible: yi.guo@thalesgroup.com
# location: Beijing
# TC0091673.001 - TpAtvBasic


import unicorn
import random
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.write_json_result_file import *


class TpAtvBasic(BaseTest):

    def setup(test):
        test.dut.detect()
        test.log.info("1. Restore to default configurations ")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))
        test.log.info("*******************************************************************\n\r")
        test.log.info("2. Enable SIM PIN lock before testing  ")

        test.expect(test.dut.at1.send_and_verify(r'AT+CLCK="SC",1,"{}"'.format(test.dut.sim.pin1), ".*(OK|ERROR).*"))
        test.dut.dstl_restart()
        # test.device.dstl_restart()
        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):
        simPINLOCKstatus = ["BEFORE", "AFTER"]

        for simPINLOCK in simPINLOCKstatus:
            test.log.info("1. test: Check default value of ATV {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.* V1.*\s+0.*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("2. test: Change ATV value to ATV0 {} input SIM PIN ".format(simPINLOCK))
            if test.dut.project == 'VIPER':
                test.expect(test.dut.at1.send_and_verify("ATV0", ".*0.*"))
            else:
                test.expect(test.dut.at1.send_and_verify(r'ATV0', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.* V0.*\s+0'))
            test.expect(test.dut.at1.send_and_verify(r'AT', r'.*0.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=0', r'.*0.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=4', r'.*4.*'))

            test.log.info("*******************************************************************\n\r")

            test.log.info("3. Restart Module and check value of ATV {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'AT+CFUN=1,1', r'.*OK.*|0', r'.*SYSSTART.*', timeout=20))
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.* V1.*\s+.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT', r'.*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("4. test: Change ATV value to ATV0 {} input SIM PIN and AT&W".format(simPINLOCK))

            if test.dut.project == 'VIPER':
                test.expect(test.dut.at1.send_and_verify("ATV0", ".*0.*"))
            else:
                test.expect(test.dut.at1.send_and_verify(r'ATV0', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.* V0.*\s+0'))
            test.expect(test.dut.at1.send_and_verify(r'AT&W', r'0'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("5. Restart Module and check value of ATV {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'AT+CFUN=1,1', r'.*OK.*|\s+0', r'.*SYSSTART.*',
                                                     timeout=15))
            test.sleep(6)
            test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.* V0.*\s+0'))
            test.expect(test.dut.at1.send_and_verify(r'AT', r'.*[^*OK*]0'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("6. Restore Module with AT&F and check value of ATV {} input SIM PIN ".format(simPINLOCK))
            if test.dut.project == 'VIPER':
                test.expect(test.dut.at1.send_and_verify("at&F"))
            else:
                test.expect(test.dut.at1.send_and_verify(r'AT&F', r'.*[^*OK*]0'))
            test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.* V1.*\s+0.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT&W', r'.*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("7. Set incorret value  of ATV {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'ATV2', r'.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(r'ATV3', r'.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(r'ATVB', r'.*ERROR.*'))

            # C.Dehm: Viper100_120c answer with CME: invalid index
            if test.dut.project == 'VIPER' and int(test.dut.step) >= 2:
                test.expect(test.dut.at1.send_and_verify("ATV-1", '.*4.*'))
            else:
                test.expect(test.dut.at1.send_and_verify(r'ATV-1', r'.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT&F', r'.*'))
            test.log.info("*******************************************************************\n\r")

            if simPINLOCK == "without":
                test.expect(test.dut.dstl_enter_pin())
                test.log.info("Wait a while after input PIN code")

            pass

    def cleanup(test):
        test.dut.at1.send_and_verify("at&F")
        test.sleep(5)
        test.dut.at1.send_and_verify("atv1", ".*OK.*")
        test.dut.at1.send_and_verify("ate1", ".*OK.*")
        test.dut.at1.send_and_verify("atq0", ".*OK.*")
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if __name__ == "__main__":
    unicorn.main()
