# responsible: christoph.dehm@thalesgroup.com
# author: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0000000.001
# JIRA: KRAKEN-740

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
# from dstl.auxiliary.restart_module import dstl_restart
# from dstl.network_service.attach_to_network import dstl_enter_pin


class Test(BaseTest):
    
    def setup(test):
        test.require_plugin('adb')
        test.dut.dstl_detect()

    def run(test):

        res = test.dut.adb.send_and_receive("uname -a")
        test.expect(test.dut.adb.last_retcode == 0)
        if "Linux" in res:
           test.log.info("'Linux' found in response of 'uname -a' shell cmd.")
           test.expect(True)
        else:
           test.log.info("'Linux' NOT found in response of 'uname -a' shell cmd.")
           test.expect(False)
        test.log.info("response was: \n" +  res)


        test.dut.adb.send_and_receive("getprop")
        if "MT2735" in test.dut.product:
            test.expect(test.dut.adb.last_retcode != 0)
        else:
            test.expect(test.dut.adb.last_retcode == 0)

        res = test.dut.adb.send_and_receive("cat /vendor/build.prop")
        test.expect(test.dut.adb.last_retcode == 0)
        pass


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

