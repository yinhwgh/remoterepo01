#responsible  yanen.wang@thalesgroup.com
#location: Beijing
#TC0093810.002

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board

class Test(BaseTest):
    """
       TC0093810.002 - time_measurement_with_ShutdownRestart
       Debugged: Viper

    """
    t_switch_off_Start = 0
    t_switch_off_End = 0
    t_switch_on_Start = 0
    t_switch_on_End = 0
    sum_shutdown = 0
    max_shutdown = 0
    min_shutdown = 99999
    sum_startup = 0
    max_startup = 0
    min_startup = 99999
    switch_off_time = 0
    switch_on_time = 0
    numOfLoops = 1000

    def setup(test):
        dstl_detect(test.dut)
        test.dut.devboard.send_and_verify('MC:URC=SER', 'OK')
        test.dut.devboard.send_and_verify('MC:URC=PWRIND', 'OK')
    def run(test):
        test.log.info("***  Close PIN ***")
        dstl_unlock_sim(test.dut)
        test.log.step("***  Restart the module  ***")
        dstl_restart(test.dut)
        test.sleep(2)
        test.log.info("*** TpShutdownRestart - Start ***")
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('** Loop: {} -START **'.format(loop))
            test.log.info("* set the error report format *")
            test.dut.at1.send_and_verify('AT+CMEE=2', 'OK')
            test.log.step("* Registration to network **")
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("* Module Shutdown via at^smso ***")
            test.dut.at1.send('at^smso')
            test.t_switch_off_Start = time.time()
            test.dut.devboard.wait_for(".*PWRIND: 1.*")
            test.t_switch_off_End = time.time()
            test.switch_off_time = test.t_switch_off_End - test.t_switch_off_Start
            test.sum_shutdown += test.switch_off_time
            if  test.switch_off_time < test.min_shutdown:
                test.min_shutdown = test.switch_off_time
            if  test.switch_off_time > test.max_shutdown:
                test.max_shutdown = test.switch_off_time
            test.log.info("** Shutdown process end **")
            test.sleep(5)
            test.log.step(" *** start module  ***")
            dstl_turn_on_igt_via_dev_board(test.dut)
            test.t_switch_on_Start = time.time()
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.t_switch_on_End = time.time()
            test.switch_on_time = test.t_switch_on_End - test.t_switch_on_Start
            test.sum_startup += test.switch_on_time
            if test.switch_on_time < test.min_startup:
               test.min_startup = test.switch_on_time
            if test.switch_on_time > test.max_startup:
               test.max_startup = test.switch_on_time
            test.sleep(5)
            test.log.info("*******************************\n")
            test.log.info("* loop {} ".format(loop))
            test.log.info("The SHUTDOWN-time is {:.2f} seconds.".format(test.switch_off_time))
            test.log.info("The RESTART-time is {:.2f} seconds.".format(test.switch_on_time))
            test.log.info("*******************************\n")
            loop = loop + 1

        test.log.info("*******************************\n")
        test.log.info("The average of SHUTDOWN-time is {:.2f} seconds.".format(test.sum_shutdown/test.numOfLoops))
        test.log.info("The minimum of SHUTDOWN-time is {:.2f} seconds.".format(test.min_shutdown))
        test.log.info("The maximum of SHUTDOWN-time is {:.2f} seconds.".format(test.max_shutdown))
        test.log.info("*******************************\n")
        test.log.info("*******************************\n")
        test.log.info("The average of RESTART-time is {:.2f} seconds.".format(test.sum_startup/test.numOfLoops))
        test.log.info("The minimum of RESTART-time is {:.2f} seconds.".format(test.min_startup))
        test.log.info("The maximum of RESTART-time is {:.2f} seconds.".format(test.max_startup))
        test.log.info("*******************************\n")

    def cleanup(test):
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        pass


if (__name__ == "__main__"):
    unicorn.main()