#responsible: lijuan.li@thalesgroup.com
#location: Beijing
#TC0095054.002 FfsRobustnessAgainstPowerLossDuringStartup

import unicorn
import time
from decimal import Decimal
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network

maxTestTime = 28800 #time in second 28800 -8h

class FfsRobustnessAgainstPowerLossDuringStartup(BaseTest):
    """
    TC0095054.002 FfsRobustnessAgainstPowerLossDuringStartup

    Check if the module is robust against unexpected loss of power during module startup.

    1. Switch on module.
    2. Cut off power after delay. If ^SYSSTART will apear then delay = 0 ms.
    3. Switch on module.
    4. Wait for ^SYSSTART.
    5. Switch off module.
    6. Repeat all above described steps 10 times.
    7. Increase delay by 1 ms.
    8. Repeat steps 1 - 7 for at least 8 hours.

    """
    wforsysstarttimer = 60
    time1 = 0

    def check_timing(test, teststep="", maxduration=10):
        if teststep == "":
            teststep = "general time measuring"

        time2 = time.perf_counter()
        #print("T1", time1, "T2", time2, "diff", (time2-time1) )
        duration = time2 - test.time1
        resultmsg = teststep, "was: {:.1f} sec.".format(duration)
        if duration > maxduration:
            resultmsg = resultmsg, "is bigger than " +str(maxduration) + " sec. - FAILED"
            test.log.critical(resultmsg)
            return -1
        else:
            resultmsg = resultmsg, "is lower than " + str(maxduration) + " sec. as expected."
            test.log.info(resultmsg)
        return 0

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        # enable URCs on MCT to see which serial lines are changing
        test.dut.devboard.send_and_verify('mc:URC=SER')
        test.dut.devboard.send_and_verify('mc:URC=PWRIND')
        test.dut.devboard.send_and_verify('mc:URC=on')

        pass

    def run(test):
        test.log.step("0. Turn off module immediately with AT^SMSO")
        test.expect(dstl_shutdown_smso(test.dut))
        test.sleep(1)

        test.dut.devboard.send('mc:gpiocfg=3,outp')
        test.sleep(0.3)
        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(0.3)
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(test.wforsysstarttimer)
        test.dut.at1.send('ATi')
        test.dut.devboard.send_and_verify('mc:pwrind?')

        tStart = time.time()
        delay = 0
        while (((time.time() - tStart) < maxTestTime)):
            loop = 1
            while loop < 11:
                test.log.step('Loop: {}'.format(loop) + ' with  ' + 'delay: {}'.format(delay*1000) + 'ms')
                test.log.step("1. Power on DUT")
                test.dut.devboard.send_and_verify('MC:VBATT=OFF', ".*")
                test.dut.devboard.send_and_verify('MC:VBATT=ON', ".*")
                test.sleep(10)
                test.dut.devboard.send_and_verify('MC:IGT=555', ".*")
                test.sleep(1)

                test.log.step("2. Wait for SYSSTART and Shutdown after delay.")
                test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
                time.sleep(delay)
                test.dut.at1.send('AT^SMSO="fast"')
                test.time1 = time.perf_counter()
                test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
                ret = test.check_timing("SMSO FAST SHUTDOWN", maxduration=1)

                test.log.step("3. Power on DUT")
                test.dut.devboard.send_and_verify('MC:VBATT=ON', ".*")
                test.sleep(1)
                test.dut.devboard.send_and_verify('MC:IGT=555', ".*")

                test.log.step("4. Wait for SYSSTART")
                test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))

                #test.log.step("5. Switch OFF module")
                #test.sleep(2)
                #test.dut.devboard.send('mc:gpio3=0')
                #test.time1 = time.perf_counter()
                #test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
                #ret = test.check_timing("6. GPIO-Shutdown", maxduration=1)
                #test.dut.devboard.send_and_verify('mc:gpio3=1')
                #test.sleep(1)
                loop = loop + 1

            delay = Decimal(str(delay)) + Decimal(str(0.01))

    def cleanup(test):
        test.log.step("11. Power on DUT")
        test.dut.devboard.send_and_verify('MC:VBATT=ON', ".*")
        test.sleep(10)
        test.dut.devboard.send_and_verify('MC:IGT=555', ".*")

        test.log.step("12. Wait for SYSSTART")
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.sleep(1)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


    if "__main__" == __name__:
        unicorn.main()


