#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091676.001 - TpAtzBasic


import unicorn
import random
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class TpATZBasic(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("1. Restore to default configurations ")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))
        test.log.info("*******************************************************************\n\r")
        # AT+CLCK="SC",1,"1234"
        test.log.info("2. Enable SIM PIN lock before testing  ")
        test.expect(test.dut.at1.send_and_verify(r'AT+CLCK="SC",1,"{}"'.format(test.dut.sim.pin1), ".*(OK|ERROR).*"))
        test.dut.dstl_restart()
        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):

        simPINLOCKstatus = ["without", "with"]

        simPINLOCK = 'without'
        test.log.info("1. test: Send ATZ {} PIN ".format(simPINLOCK))
        if simPINLOCK == "without":
            if (test.dut.project == "SERVAL") or (test.dut.project == "MARLIN") or (test.dut.project == "BOBCAT") or (test.dut.project == "VIPER"):
                test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*ERROR.*SIM PIN required.*'))
                test.log.info("*1.1*****************************************************************\n\r")
            else:
                test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*OK.*'))
                print("product under test:",test.dut.product)
                test.log.info("*1.2*****************************************************************\n\r")
        else:
            test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*OK.*'))
            test.log.info("*1.3*****************************************************************\n\r")

        test.log.info("2. test: Send ATZ0  {} PIN ".format(simPINLOCK))
        if simPINLOCK == "without":
            if (test.dut.project == "SERVAL") or (test.dut.project == "MARLIN") or (test.dut.project == "BOBCAT") or (test.dut.project == "VIPER"):
                test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*ERROR.*SIM PIN required.*'))
                test.log.info("*2.1******************************************************************\n\r")
            else:
                test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*OK.*'))
                test.log.info("*2.2******************************************************************\n\r")
        else:
            test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*OK.*'))
            test.log.info("*2.3******************************************************************\n\r")

        test.expect(test.dut.dstl_enter_pin())
        simPINLOCK = 'with'

        test.log.info("3. Restore AT Command Settings to default values with ATZ0 {} PIN ".format(simPINLOCK))
        # BOB-4735: workaround to catch SIM busy shortly after PIN1 entering
        test.attempt(test.dut.at1.send_and_verify, 'AT+CMGF=1', r'.*OK.*', retry=5, sleep=0.3, append=True)
        # workaround for Unicorn IPIS100311352
        if 'SIM failure' in test.dut.at1.last_response:
            test.log.critical("SIM busy expected here instead of SIM failure, see IPIS100311283")
            test.expect(False)

        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=0', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SSET=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CREG=2', r'.*OK.*'))
        if (test.dut.product == "serval") or (test.dut.product == "marlin"):
            test.expect(test.dut.at1.send_and_verify(r'AT^SLED=1', r'.*OK.*'))
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))
        else:
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT&V', r'.*OK.*'))

        if (test.dut.product == "serval") or (test.dut.product == "marlin"):
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 0[\s\S]*CMEE: 2[\s\S]*SSET: 0[\s\S]*CREG: 0[\s\S]*SLED: 0[\s\S]*OK.*'))
        else:
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 0[\s\S]*CMEE: 2[\s\S]*SSET: 0[\s\S]*CREG: 0[\s\S]*OK.*'))

        test.log.info("*******************************************************************\n\r")

        test.log.info("4. Restore AT Command Settings to user defined profile with ATZ0 {} PIN ".format(simPINLOCK))
        # test.expect(test.dut.at1.send_and_verify(r'ATZ1', r'',r''))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMGF=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=0', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SSET=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CREG=2', r'.*OK.*'))

        if (test.dut.product == "serval") or (test.dut.product == "marlin"):
            test.expect(test.dut.at1.send_and_verify(r'AT^SLED=1', r'.*OK.*'))
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))
        else:
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT&W', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT&F', r'.*OK.*'))
        if (test.dut.product == "serval") or (test.dut.product == "marlin"):
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 0[\s\S]*CMEE: 2[\s\S]*SSET: 0[\s\S]*CREG: 0[\s\S]*SLED: 0[\s\S]*OK.*'))
        else:
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 0[\s\S]*CMEE: 2[\s\S]*SSET: 0[\s\S]*CREG: 0[\s\S]*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'ATZ', r'.*OK.*'))
        if (test.dut.product == "serval") or (test.dut.product == "marlin"):
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))
        else:
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*OK.*'))

        test.log.info("*******************************************************************\n\r")

        test.log.info(
            "5. Restore AT Command Settings to user defined profile with ATZ0 {} PIN after module restart".format(
                simPINLOCK))
        test.dut.dstl_restart()
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())
        # BOB-4735: workaround to catch SIM busy shortly after PIN1 entering
        test.attempt(test.dut.at1.send_and_verify, 'ATZ', r'.*OK.*', retry=5, sleep=0.3, append=True)
        # workaround for Unicorn IPIS100311352
        if 'SIM failure' in test.dut.at1.last_response:
            test.log.critical("SIM busy expected here instead of SIM failure, see IPIS100311283")
            test.expect(False)

        if (test.dut.product == "serval") or (test.dut.product == "marlin"):
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))
        else:
            test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         r'.*CMGF: 1[\s\S]*CMEE: 0[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*OK.*'))

        test.log.info("*******************************************************************\n\r")

        test.log.info("6. Set incorret value  of ATZ {} PIN ".format(simPINLOCK))
        test.expect(test.dut.at1.send_and_verify(r'ATZ1', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'ATZ?', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'ATZ=?', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'ATZ2', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'ATZB', r'.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify(r'ATZ-1', r'.*ERROR.*'))
        test.log.info("*******************************************************************\n\r")

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
