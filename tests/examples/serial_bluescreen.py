# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001

import unicorn
from core.basetest import BaseTest
import os
import time

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart

import serial

class Test(BaseTest):
    """Test which tries to invoke BSOD (blue screen) when working with USB module
    to check the USB driver.
    """
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        port = test.dut.at1.port
        dstl_restart_thread = test.thread(test.dut.dstl_restart)
        test._attempts = []
        test._cluster_fails = 0
        test._cluster_success = 0
        test._status = None
        while dstl_restart_thread.is_alive():
            try:
                s = serial.Serial(port)
                s.close()
            except (serial.SerialException, serial.serialutil.SerialException) as ex:
                test._status = False
                test._cluster_fails += 1
            else:
                test._status = True
                test._cluster_success += 1

            if test._status == True and test._cluster_fails > 0:
                test.log.info("- connections failed: {}".format(test._cluster_fails))
                test._cluster_fails = 0
            elif test._status == False and test._cluster_success > 0:
                test.log.info("- connections established: {}".format(test._cluster_success))
                test._cluster_success = 0

            time.sleep(0.01)

        if test._cluster_success > 0:
            test.log.info("- connections established: {}".format(test._cluster_success))
        if test._cluster_fails > 0:
            test.log.info("- connections failed: {}".format(test._cluster_fails))

        test.log.info("Port polling ended successfully")
        test.expect(True)


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
