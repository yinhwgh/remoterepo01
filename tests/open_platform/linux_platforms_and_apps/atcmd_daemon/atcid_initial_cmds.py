# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107496.001
# jira: KRAKEN-535, KRAKEN-741
# feature:
#
#

import unicorn
import time
from core.basetest import BaseTest
import dstl.embedded_system.linux.configuration
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import dstl_register_to_network

testcase_id = "TC0107496.001"
ver = "1.0"


class Test(BaseTest):

    def setup(test):
        test.dut.at1.close()
        test.pin1 = test.dut.sim.pin1
        test.dut.dstl_detect()
        test.dut.at1.close()

        test.log.info('>> restart module to get back to "SIM PIN" status in case PIN was entered before')
        test.expect(test.dut.dstl_restart())
        # test.dut.adb.send_and_receive("(reboot) && sleep 1")
        # time.sleep(25)      # some hard timer for restarting TBD: need global timer!
        test.dut.adb.open()

        res = test.dut.adb.send_and_receive("ps -efa |grep atcid")
        if "00:00:00 /usr/bin/atcid" in res:
            test.log.info(">> atcid already runs - nothing to do")
        else:
            test.log.info(">> atcid does not run - let's start it now!")
            res = test.dut.adb.send_and_receive("(nohup /usr/bin/atcid &) && sleep 1")
            if 'failed to open' in res:     # nohup: failed to open `nohup.out': Read-only file system
                test.log.error("! nohup could not be started - abort")
                test.expect(False, critical=True)
                pass

        test.dut.at1.open()
        test.expect(test.dut.at1.send_and_verify("ATI"))
        pass

    def run(test):
        test.log.info('>> enable all URCs ')
        test.dut.adb.send_and_receive("(sncfg prop_set persist.vendor.service.atci_urc.enable 1) && sleep 1")

        # 1. do everything without pin:
        test.expect(test.dut.at1.send_and_verify("AT+CLAC"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=?"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE?"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=?"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=?"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG?"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=?"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=?", "(ERROR|OK)", timeout=120))


        # 2. do everything with pin / network:
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG?"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=?", "(ERROR|OK)", timeout=120))
        pass


    def cleanup(test):
        test.log.info('>> disable all URCs again')
        test.dut.adb.send_and_receive("(sncfg prop_set persist.vendor.service.atci_urc.enable 0) && sleep 1")
        test.log.info('>> kill ATCID daemon')
        test.dut.at1.close()
        test.kill_atcid()
        pass


    def kill_atcid(test):
        res = test.dut.adb.send_and_receive("ps -efa |grep atcid")
        if "00:00:00 /usr/bin/atcid" in res:
            res_list = res.split()
            ret = test.dut.adb.send_and_receive("kill -9 " + res_list[1])
            res = test.dut.adb.send_and_receive("ps -efa |grep atcid")
        else:
            test.log.info("nothing to kill - process not found!")
        pass


if "__main__" == __name__:
    unicorn.main()
