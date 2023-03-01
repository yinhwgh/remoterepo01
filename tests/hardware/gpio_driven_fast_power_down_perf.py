#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0094768.002

import unicorn
import time

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board,dstl_turn_on_vbatt_via_dev_board

class Test(BaseTest):
    """
    Debuged in Viper
    TC0094768.002 - GPIODrivenFastPowerDownPerf
    Check if the GPIO Fast Power Down functionality is working according to specified timing.

    Precondition
    - Dedicated GPIO is not reserved.
    - McTest
    - Multiadapter with GPIO

    1. Set AT^SCFG="GPIO/mode/FSR","gpio"
    2. Restart module
    3. Check AT^SCFG="GPIO/mode/FSR"
    4. Set GPIO4 pin as Input.
    5. Set AT^SCFG="GPIO/mode/FSR","std"
    6. Restart module
    7. Check AT^SCFG="GPIO/mode/FSR"
    8. Set AT^SCFG="MEShutdown/Fso","1"
    9. Check AT^SCFG="MEShutdown/Fso"
    10. Restart the module (AT+CFUN=1,1)
    11. Wait for ^SYSSTART, then connect GPIO4 to GND for a while just after 1 second the ^SYSSTART came and measure delay time to power down then turn on the module,
        repeat this step: 20 times.
    12. Wait for ^SYSSTART, then connect GPIO4 to GND for a while just after 5 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,
        repeat this step: 20 times.
    13. Wait for ^SYSSTART, then connect GPIO4 to GND for a while just after 10 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,
        repeat this step: 20 times.
    14. Wait for ^SYSSTART, then connect GPIO4 to GND for a while just after 30 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,
        repeat this step: 20 times.
    15. Wait for ^SYSSTART, then connect GPIO4 to GND for a while just after 60 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,
        repeat this step: 20 times.

    """
    numOfLoops = 20
    def measurePowerDownTime(test, delaySeconds):
        startTime = 0
        estimatedTime = 0
        sum_switchoffTime = 0

        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('*** Loop: {} '.format(loop))
            test.sleep(delaySeconds)
            test.log.info("Connect GPIO4 to GND")
            test.dut.devboard.send('MC:GPIO3=0')
            startTime = time.time()
            test.dut.devboard.wait_for('.* PWRIND: 1.*',timeout=2)
            estimatedTime = time.time()
            estimatedTime -= startTime
            sum_switchoffTime += estimatedTime
            test.log.info("Module Switch off Time is {:.1f} msec.".format(1000*estimatedTime))
            test.sleep(5)
            test.log.info("Turn on Module and wait for ^SYSSTART")
            test.dut.devboard.send_and_verify('mc:gpio3=1')
            dstl_turn_on_igt_via_dev_board(test.dut)
            test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
            loop = loop + 1

        test.log.info("****************************************************\n")
        test.log.info("The average of FAST SWITCHOFF-time is {:.0f} msec".format(1000*sum_switchoffTime/test.numOfLoops))
        test.log.info("When delayTime is {} sec ".format(delaySeconds))
        test.log.info("****************************************************\n")

    def setup(test):
        dstl_detect(test.dut)
        dstl_register_to_network(test.dut)
        test.log.info("Prepare McTest")
        test.dut.devboard.send_and_verify('MC:MODULE=PLS8', ".*OK")
        test.dut.devboard.send_and_verify('mc:urc=off,common', "OK")
        test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK')
        test.dut.devboard.send_and_verify('mc:gpio3=1', "OK")
        dstl_turn_on_igt_via_dev_board(test.dut)

    def run(test):
        test.log.step('1. Set AT^SCFG="GPIO/mode/FSR","gpio"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR","gpio"', 'OK'))
        test.log.step("2. Restart module")
        test.expect(dstl_restart(test.dut))
        if test.dut.project == "SERVAL":
            test.log.info(" * Skip steps 3-7 *")
        else:
            test.log.step("3.Check the GPIO/mode/FSR")
            test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR"', '.*gpio.*')
            test.log.step("4. Set GPIO4 pin as Input")
            test.dut.at1.send_and_verify('AT^SPIO=0', 'OK')
            test.dut.at1.send_and_verify('AT^SPIO=1', 'OK')
            #test.dut.at1.send_and_verify('AT^SCPIN=1,3,0', 'OK')
            test.log.step('5. Set AT^SCFG="GPIO/mode/FSR","std"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR","std"', '.*OK.*'))
            test.log.step("6. Restart module")
            test.expect(dstl_restart(test.dut))
            test.log.step("7. Check the GPIO/mode/FSR")
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR"', '.*std.*'))
        if test.dut.platform is 'INTEL':
            test.log.step('8. set "MEShutdown/Fso","1"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/Fso","1"', '.*OK.*'))
            test.log.step('9. check "MEShutdown/Fso"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/Fso"', '.*1.*'))
        else:
            test.log.info(" * Skip steps 8-9 * ")

        test.log.step("10. Restart module")
        dstl_restart(test.dut)

        test.log.step("11.connect GPIO4 to GND for a while just after 1 second the ^SYSSTART came and measure delay time to power down then turn on the module,repeat this step: 20 times")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measurePowerDownTime(1)

        test.sleep(1)
        test.log.step("12.connect GPIO4 to GND for a while just after 5 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,repeat this step: 20 times")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measurePowerDownTime(5)

        test.sleep(1)
        test.log.step("13.connect GPIO4 to GND for a while just after 10 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,repeat this step: 20 times")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measurePowerDownTime(10)

        test.sleep(1)
        test.log.step("14.connect GPIO4 to GND for a while just after 30 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,repeat this step: 20 times")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measurePowerDownTime(30)

        test.sleep(1)
        test.log.step("15.connect GPIO4 to GND for a while just after 60 seconds the ^SYSSTART came and measure delay time to power down then turn on the module,repeat this step: 20 times")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.measurePowerDownTime(60)

    def cleanup(test):
        test.dut.at1.send_and_verify('AT&F', 'OK')
        test.dut.devboard.send('mc:gpiocfg=3,inp')
        test.dut.devboard.send('mc:time=OFF')
        pass


if "__main__" == __name__:
    unicorn.main()
