#responsible: baris.kildi@thalesgroup.com
#location: Berlin
#TC0104876.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init


class Test(BaseTest):
    """ The AT^SNMON command can be used to monitor various network information
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):

        # 0. Restart module
        test.log.info("0. Restart module by calling dstl_restart")
        test.dut.dstl_restart()

        # Run steps without entering PIN
        # 1. Run test command
        test.log.info("1. Run test command: AT^SNMON=?")
        test.expect(test.dut.at1.send_and_verify("AT^SNMON=?", ".*INSCatM*"))

        # 2. Run invalid commands
        test.log.info("2. Run invalid command: AT^SNMON?")
        test.expect(test.dut.at1.send_and_verify("AT^SNMON?", ".*ERROR*"))

        test.expect(test.dut.at1.send_and_verify("AT^SNMON", ".*ERROR*"))

        test.expect(test.dut.at1.send_and_verify("AT^SNMON=0", ".*ERROR*"))

        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",0', ".*OK*"))

        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",1', ".*OK*"))

        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",2', wait_for=".*INSCatM*"))

        test.sleep(5)

        # 3. Run steps with entering PIN, module should be registered
        test.log.info("3. Enter PIN, register to network")
        test.expect(test.dut.at1.send_and_verify("at+cpin=\"{}\"".format(test.dut.sim.pin1), ".*OK.*"))

        test.attempt(test.dut.at1.send_and_verify, "AT+COPS=0", ".*OK.*", timeout=30, retry=10)
        test.sleep(10)
        test.dut.at1.send_and_verify("at+cimi")
        resp = test.dut.at1.last_response.split()
        test.log.info(resp)
        mcc_mnc = resp[1][:5]

        test.log.info("This is your MCC_MNC: {}".format(mcc_mnc))
        #test.expect(test.dut.at1.send_and_verify(("at+cops?", ".*mcc_mnc.*", ".*OK.*")))
        test.expect(test.dut.at1.send_and_verify("at+cops?", expect=mcc_mnc, wait_for=".*OK.*"))

        #test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*COPS:.*,.*,.*OK.*"))

        # 4. Run test command
        test.log.info("4. Run test command: AT^SNMON=?")
        test.expect(test.dut.at1.send_and_verify("AT^SNMON=?", ".*INSCatM*"))

        # 5. Run invalid commands
        test.log.info("5. Run invalid command: AT^SNMON?")
        test.expect(test.dut.at1.send_and_verify("AT^SNMON?", ".*ERROR*"))

        test.expect(test.dut.at1.send_and_verify("AT^SNMON", ".*ERROR*"))

        test.expect(test.dut.at1.send_and_verify("AT^SNMON=0", ".*ERROR*"))

        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",0', ".*OK*"))

        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",1', ".*OK*"))

        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",2', "\s\+CME ERROR: Operation temporary not allowed\s", wait_after_send=5))


        # 6. Deregister from network at+cops=2
        test.log.info("6. Deregister from network at+cops=2")

        test.attempt(test.dut.at1.send_and_verify, "AT+COPS=2", ".*OK.*", timeout=30, retry=10)
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:2.*,.*,.*OK.*"))

        # 7. Call write command with action=2 ---- AT^SNMON="INSCatM", <action>
        test.log.info('7. Call write command with AT^SNMON="INSCatM",2')
        test.expect(test.dut.at1.send_and_verify('AT^SNMON="INSCatM",2', wait_for=".*INSCatM*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
