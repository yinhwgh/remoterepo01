# responsible: yi.guo@thalesgroup.com
# location: Beijing
# TC0095111.001 - SarPowerLimitationBasic

import unicorn
import random

from core.basetest import BaseTest


from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim


class SarPowerLimitationBasic(BaseTest):
    def setup(test):
        test.dut.detect()
        test.log.info("1. Restore to default configurations")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*(OK|ERROR).*", timeout=30))
        test.log.info("*******************************************************************\n\r")
        test.log.info("2. Enable SIM PIN lock before testing  ")
        test.expect(test.dut.dstl_lock_sim())
        test.dut.dstl_restart()
        # test.device.restart()
        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):
        # AT^SCFG= "MEopMode/PwrSave"[,<PwrSaveMode>][,<PwrSavePeriod>][,<PwrSaveWakeup>]
        PL_band2gs_Low = ['1', '4']
        PL_band2gs_High = ['2', '8']
        #PL_band4g_1s = [1, 2, 4, 8, 10, 80, 800, 1000, 2000, 20000, 40000, 80000, 1000000, 2000000, 4000000, 8000000]

        if test.dut.project is 'SERVAL':
            PL_band4g_1s = [1, 2, 4, 8, 10, 80, 800, 1000, 20000, 40000, 80000, 1000000, 2000000, 4000000, 8000000]
            PL_band4g_2s = [200000000, 4000000000, 10000000000000]
            PL_limit4gs = range(18, 21)
        elif test.dut.project is 'VIPER':
            PL_band4g_1s = [1, 2, 4, 8, 10, 80, 800, 1000, 20000, 40000, 80000, 2000000, 8000000]
            PL_band4g_2s = [20, 80, 100, 200000000]
            PL_limit4gs = range(18, 21)
        else:
            PL_band4g_1s = [9999]           # illegal values to show that the product is not well defined!
            PL_band4g_2s = [990099009]
            PL_limit4gs = range(17, 18)
            test.expect(False, critical=True, msg="band ranges are not defined, please define your project first!")

        PL_modes = [1, 2, 3, 4]
        PL_profiles = range(1, 9)
        simPINLOCKstatus = ["BEFORE", "AFTER"]
        PL_limit2gs_Low = range(18, 34)
        PL_limit2gs_High = range(18, 31)
        PL_limit_psks_Low = range(18, 28)
        PL_limit_psks_High = range(18, 27)

        for simPINLOCK in simPINLOCKstatus:
            test.log.info("1. test: Check supported parameters and values of MTPL {} Input SIM PIN".format(simPINLOCK))
            # test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*SCFG: \"MEopMode/PwrSave\".*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*{}[\S\s]*{}[\S\s]*{}[\S\s]*OK.*'.format(
                'SCFG: "Radio/Mtpl",\("0-1"\),\("1-8"\)','\^SCFG: "Radio/Mtpl/2G"','\^SCFG: "Radio/Mtpl/4G"')))
            test.log.info("*******************************************************************\n\r")

            test.log.info(
                "2. test: Check defautl Power Limitation Mode after restart module {} PIN".format(simPINLOCK))
            # test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*SCFG: \"MEopMode/PwrSave\".*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "Radio/Mtpl"', '.*{}.*.OK.*'.format(
                '\^SCFG: "Radio/Mtpl","0"')))
            test.log.info("*******************************************************************\n\r")

            # test.log.info(test.dut.at1.last_response)
            test.log.info(
                "3. test: Check default parameters and values of MTPL in Radio Band 2G {} PIN".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="Radio/Mtpl/2G"',
                                                     '\^SCFG: "Radio/Mtpl/2G","0".*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info(
                "4. test: Check default parameters and values of MTPL in  Radio Band 4G {} PIN".format(simPINLOCK))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="Radio/Mtpl/4G"',
                                                     '\^SCFG: "Radio/Mtpl/4G","0".*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("5. test: Configure MTPL in  Radio Band 2G {} PIN ".format(simPINLOCK))
            #########AT^SCFG= "Radio/Mtpl/2G"[,<PL_mode>[,<PL_profile>,<PL_band2g> ,,<PL_limit2g>,<PL_limit_psk>] ]

            for PL_band2g in PL_band2gs_Low:
                for PL_limit2g in PL_limit2gs_Low:
                    for PL_limit_psk in PL_limit_psks_Low:
                        for PL_profile in PL_profiles:
                            test.expect(test.dut.at1.send_and_verify(
                                r'AT^SCFG="Radio/Mtpl/2G",3,{},{},,{},{}'.format(PL_profile, PL_band2g, PL_limit2g,
                                                                                 PL_limit_psk),
                                '"Radio/Mtpl/2G".*OK.*'))
                        test.sleep(1)
                        test.dut.dstl_restart()
                        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="Radio/Mtpl/2G",2',
                                                                 '.*."1","0000000{}",,"{}","{}".*"2","0000000{}",,"{}","{}".*"3","0000000{}",,"{}","{}".*"4","0000000{}",,"{}","{}".*"5","0000000{}",,"{}","{}".*"6","0000000{}",,"{}","{}".*"7","0000000{}",,"{}","{}".*"8","0000000{}",,"{}","{}".*OK.*'.format(
                                                                                               PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,PL_band2g,PL_limit2g,PL_limit_psk,)))


            for PL_band2g in PL_band2gs_High:
                for PL_limit2g in PL_limit2gs_High:
                    for PL_limit_psk in PL_limit_psks_High:
                        for PL_profile in PL_profiles:
                            test.expect(test.dut.at1.send_and_verify(
                                r'AT^SCFG="Radio/Mtpl/2G",3,{},{},,{},{}'.format(PL_profile, PL_band2g, PL_limit2g,
                                                                                 PL_limit_psk),
                                '"Radio/Mtpl/2G".*OK.*'))
                        test.sleep(1)
                        test.dut.dstl_restart()
                        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="Radio/Mtpl/2G",2',
                                                                 '.*."1","0000000{}",,"{}","{}".*."2","0000000{}",,"{}","{}".*."3","0000000{}",,"{}","{}".*."4","0000000{}",,"{}","{}".*."5","0000000{}",,"{}","{}".*."6","0000000{}",,"{}","{}".*."7","0000000{}",,"{}","{}".*."8","0000000{}",,"{}","{}".*OK.*'.format(
                                                                     PL_band2g, PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, PL_band2g,
                                                                     PL_limit2g, PL_limit_psk, )))


            test.log.info("*******************************************************************\n\r")

            test.log.info("6. test: Configure MTPL in  Radio Band 4G {} PIN ".format(simPINLOCK))
            ######################AT^SCFG= "Radio/Mtpl/4G"[,<PL_mode>[,<PL_profile>,<PL_band4g-1>,<PL_band4g-2>,<PL_limit4g>] ]

            for PL_band4g_1 in PL_band4g_1s:
                for PL_limit4g in PL_limit4gs:
                    for PL_profile in PL_profiles:
                        test.expect(test.dut.at1.send_and_verify(
                            r'AT^SCFG="Radio/Mtpl/4G",3,{},{},{},{}'.format(PL_profile, PL_band4g_1, "0",
                                                                             PL_limit4g),
                            '"Radio/Mtpl/4G".*OK.*'))
                    test.sleep(1)
                    test.dut.dstl_restart()
                    test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="Radio/Mtpl/4G",2',
                                                             '[\S\s]*,"1","0*{}","{}","{}"[\s\S]*,"2","0*{}","{}","{}"[\s\S]*,"3","0*{}","{}","{}"[\s\S]*,"4","0*{}","{}","{}"[\s\S]*,"5","0*{}","{}","{}"[\s\S]*,"6","0*{}","{}","{}"[\s\S]*,"7","0*{}","{}","{}"[\s\S]*,"8","0*{}","{}","{}"[\s\S]*OK'.format(
                                                                                           PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g, PL_band4g_1,
                                                                                           "00000000",
                                                                                           PL_limit4g)))

            test.log.info("*******************************************************************\n\r")

            # __________________________________________________________
            for PL_band4g_2 in PL_band4g_2s:
                for PL_limit4g in PL_limit4gs:
                    for PL_profile in PL_profiles:
                        test.expect(test.dut.at1.send_and_verify(
                            r'AT^SCFG="Radio/Mtpl/4G",3,{},{},{},{}'.format(PL_profile, "0", PL_band4g_2,
                                                                             PL_limit4g),
                            '"Radio/Mtpl/4G".*OK.*'))
                    test.sleep(1)
                    test.dut.dstl_restart()
                    test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="Radio/Mtpl/4G",2',
                                                             '[\S\s]*"1","{}","{}","{}"[\S\s]*"2","{}","{}","{}"[\S\s]*"3","{}","{}","{}"[\S\s]*"4","{}","{}","{}"[\S\s]*"5","{}","{}","{}"[\S\s]*"6","{}","{}","{}"[\S\s]*"7","{}","{}","{}"[\S\s]*"8","{}","{}","{}"[\S\s]*OK'.format(
                                                                                           "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g, "00000000",
                                                                                           PL_band4g_2,
                                                                                           PL_limit4g)))

            test.log.info("*******************************************************************\n\r")

            # _____________________________________________________________________
            test.log.info("7. test: Eanble/Disable MTPL {} PIN ".format(simPINLOCK))
            # AT^SCFG= "Radio/Mtpl"[,<PL_mode>[,<PL_profile>] ]

            for PL_profile in PL_profiles:
                test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "Radio/Mtpl",{},{}'.format("1", PL_profile),
                                                         f'\^SCFG: "Radio/Mtpl","1","{PL_profile}"[\s\S]*OK'))
                test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "Radio/Mtpl",{},{}'.format("0", PL_profile),
                                                         '\^SCFG: "Radio/Mtpl","0"[\S\s]*OK'))
        test.log.info("*******************************************************************\n\r")

        if simPINLOCK == "without":
            test.expect(test.dut.enter_pin())
            test.log.info("Wait a while after input PIN code")

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
