#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0094424.001 - TpAtScfgMEopModePwrSave

import unicorn
import random

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim


class TpAtScfgMEopModePwrSave(BaseTest):

    def setup(test):
        test.log.info("1. Restore to default configurations ")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.log.info("*******************************************************************\n\r")
        # AT+CLCK="SC",1,"1234"
        test.log.info("2. Enable SIM PIN lock before testing  ")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):
        # AT^SCFG= "MEopMode/PwrSave"[,<PwrSaveMode>][,<PwrSavePeriod>][,<PwrSaveWakeup>]
        PwrSaveMode = ['disabled', 'enabled']
        PwrSavePeriod = range(0, 601)
        PwrSaveWakeup = range(1, 36001)
        default_PwrSaveMode = 'disabled'
        default_PwrSavePeriod = 52
        default_PwrSaveWakeup = 50
        simPINLOCKstatus = ["Before","After"]

        for simPINLOCK in simPINLOCKstatus:
            test.log.info("1. test: Check supported parameters and values of Power Save Mode {} input SIM PIN ".format(simPINLOCK))
            # test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*SCFG: \"MEopMode/PwrSave\".*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*{}.*.OK.*'.format(
                'SCFG: "MEopMode/PwrSave",\("disabled","enabled"\),\("0-600"\),\("1-36000"\)')))
            test.log.info("*******************************************************************\n\r")

            # test.log.info(test.dut.at1.last_response)
            test.log.info("2. test: Check current parameters and values of Power Save Mode {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCFG?',
                                                     '.*.SCFG: "MEopMode/PwrSave","(disabled|enabled)","\\d{0,3}","\\d{0,5}".*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("3. test: Enable Power Save Mode with default values {} PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","enabled",{0},{1}'.format(str(default_PwrSavePeriod),
                                                                       str(default_PwrSaveWakeup)),
                '.*.SCFG: "MEopMode/PwrSave","enabled","{0}","{1}".*OK.*'.format(str(default_PwrSavePeriod),
                                                                                 str(default_PwrSaveWakeup))))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave"',
                '.*.SCFG: "MEopMode/PwrSave","enabled","{0}","{1}".*OK.*'.format(str(default_PwrSavePeriod),
                                                                                 str(default_PwrSaveWakeup))))

            test.log.info("*******************************************************************\n\r")

            test.log.info("4. test: Disable Power Save Mode with default values {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","disabled"',
                '.*.SCFG: "MEopMode/PwrSave","disabled","{0}","{1}".*OK.*'.format(str(default_PwrSavePeriod),
                                                                                  str(default_PwrSaveWakeup))))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave"',
                '.*.SCFG: "MEopMode/PwrSave","disabled","{0}","{1}".*OK.*'.format(str(default_PwrSavePeriod),
                                                                                  str(default_PwrSaveWakeup))))

            test.log.info("*******************************************************************\n\r")

            for x in range(1, 6):
                test.log.info(
                    "5.{0} test: Enable Power Save Mode with random PwrSavePeriod&PwrSaveWakeup {1} input SIM PIN ".format(x,simPINLOCK))
                random_PwrSavePeriod = random.choice(PwrSavePeriod)
                random_PwrSaveWakeup = random.choice(PwrSaveWakeup)
                test.expect(test.dut.at1.send_and_verify(
                    r'AT^SCFG="MEopMode/PwrSave","enabled",{0},{1}'.format(random_PwrSavePeriod,
                                                                           random_PwrSaveWakeup),
                    '.*.SCFG: "MEopMode/PwrSave","enabled","{0}","{1}".*OK.*'.format(random_PwrSavePeriod,
                                                                                     random_PwrSaveWakeup)))
                test.log.info("*******************************************************************\n\r")

            for x in range(1, 6):
                test.log.info(
                    "6.{0} test: Disable Power Save Mode with random PwrSavePeriod&PwrSaveWakeup {1} input SIM PIN ".format(x,simPINLOCK))
                random_PwrSavePeriod = random.choice(PwrSavePeriod)
                random_PwrSaveWakeup = random.choice(PwrSaveWakeup)
                test.expect(test.dut.at1.send_and_verify(
                    r'AT^SCFG="MEopMode/PwrSave","disabled",{0},{1}'.format(random_PwrSavePeriod,
                                                                            random_PwrSaveWakeup),
                    '.*.SCFG: "MEopMode/PwrSave","disabled","{0}","{1}".*OK.*'.format(random_PwrSavePeriod,
                                                                                      random_PwrSaveWakeup)))
                test.log.info("*******************************************************************\n\r")

            test.log.info(
                "7.test: Test invalid parameter settings {} input SIM PIN ".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","on"',
                '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","OFF"',
                '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","enabled",{0}'.format(str(PwrSavePeriod[0] - 1)), '.*ERROR.*'
            ))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","enabled",{0}'.format(str(PwrSavePeriod[-1] + 1)), '.*ERROR.*'
            ))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","enabled",52,{0}'.format(str(PwrSaveWakeup[0] - 1)), '.*ERROR.*'
            ))
            test.expect(test.dut.at1.send_and_verify(
                r'AT^SCFG="MEopMode/PwrSave","enabled",52,{0}'.format(str(PwrSaveWakeup[-1] + 1)), '.*ERROR.*'
            ))
            test.log.info("*******************************************************************\n\r")

            if simPINLOCK == "without":
                test.expect(test.dut.dstl_enter_pin())
                test.log.info("Wait a while after input PIN code")
    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
