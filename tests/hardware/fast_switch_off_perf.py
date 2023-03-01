#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0094767.001

import unicorn
import time

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board


class Test(BaseTest):
    """
    debugged for VIPER

    TC0094767.001 - FastSwitchOffPerf

    Check if the fast switch off functionality by using AT^SMSO is works according to specified timing..

    1. Set AT^SCFG="GPIO/mode/FSR","std"
    2. Restart module
    3. Check AT^SCFG="GPIO/mode/FSR"
    4. Switch on sleep mode
    5. Set AT^SCFG="MEShutdown/Fso","1"
    6. Check AT^SCFG="MEShutdown/Fso"
    7. Restart the module (AT+CFUN=1,1)
    8. Wait for ^SYSTART, then Send at^smso just after (about 1 second) the ^SYSTART came and measure delay time to power down then turn on the module
    9. Repeat 8th point 20 times
    10. Repeat 8th point 20 times about 5 seconds from the moment of ^SYSTART
    11. Repeat 8th point 20 times about 10 seconds from the moment of ^SYSTART
    12. Repeat 8th point 20 times about 30 seconds from the moment of ^SYSTART
    13. Repeat 8th point 20 times about 60 seconds from the moment of ^SYSTART

    """
    numOfLoops = 20
    delaySeconds = 0

    def measureSwitchOffTime(test, delaySeconds):
        startTime = 0
        estimatedTime = 0
        sum_switchoffTime = 0

        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('*** Loop: {} - Begin'.format(loop))
            test.sleep(delaySeconds)
            test.log.info("Switch off module via AT^SMSO")
            test.dut.at1.send('AT^SMSO="fast"')
            startTime = time.time()
            test.expect(test.dut.devboard.wait_for('.* PWRIND: 1.*'))
            estimatedTime = time.time()
            estimatedTime -= startTime
            sum_switchoffTime += estimatedTime
            test.log.info("Module Switch off Time is {:.1f} msec.".format(1000*estimatedTime))
            test.sleep(5)
            test.log.info("Turn on module and wait for ^SYSSTART")
            test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
            test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
            loop = loop + 1

        test.log.info("****************************************************\n")
        test.log.info("The delayTime is {} sec ".format(delaySeconds))
        test.log.info("The average of FAST SWITCHOFF-time is {:.0f} msec".format(1000*sum_switchoffTime/test.numOfLoops))
        test.log.info("****************************************************\n")

    def setup(test):
        dstl_detect(test.dut)
        dstl_register_to_network(test.dut)
        test.log.info("Prepare McTest")
        test.dut.devboard.send_and_verify('MC:MODULE=PLS8','.*OK.*')
        test.dut.devboard.send_and_verify('mc:urc=off,common','.*OK')
        test.dut.devboard.send_and_verify('MC:URC=SER')
        test.dut.devboard.send_and_verify('MC:URC=PWRIND')

    def run(test):
        test.log.step('1. Set AT^SCFG="GPIO/mode/FSR","std"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR","std"', ".*OK.*"))
        test.log.step("2. Restart module")
        test.expect(dstl_restart(test.dut))
        # test.expect(dstl_shutdown_smso(test.dut))
        test.log.step('3. Check AT^SCFG="GPIO/mode/FSR"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR"', '.*std.*'))
        test.log.step("4. Switch on sleep mode")
        #test.expect(test.dut.at1.send_and_verify('AT^SPOW=2,2,200', '.*OK.*'))
        if test.dut.platform is 'INTEL':
            test.log.step('5. set "MEShutdown/Fso","1"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/Fso","1"', '.*OK.*'))

            test.log.step('6. check "MEShutdown/Fso"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/Fso"', '.*1.*'))
        else:
            test.log.info(" Skip steps 5-6 ")

        test.log.step("7. Restart module")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))

        test.log.step("8. Wait for ^SYSTART, then Send at^smso just after (about 1 second) the ^SYSTART came and measure delay time to power down then turn on the module")
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))

        test.log.step("9. Repeat 8th point 20 times")
        test.measureSwitchOffTime(1)

        test.sleep(1)
        test.log.step("9. Repeat 8th point 20 times about 5 seconds from the moment of ^SYSTART")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measureSwitchOffTime(5)

        test.sleep(1)
        test.log.step("10. Repeat 8th point 20 times about 10 seconds from the moment of ^SYSTART")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measureSwitchOffTime(10)

        test.sleep(1)
        test.log.step("12. Repeat 8th point 20 times about 30 seconds from the moment of ^SYSTART")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measureSwitchOffTime(30)

        test.sleep(1)
        test.log.step("13. Repeat 8th point 20 times about 60 seconds from the moment of ^SYSTART")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measureSwitchOffTime(60)

        test.log.step("Reset AT Command Settings to Factory Default Values")
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
