# responsible fang.liu@thalesgroup.com
# Berlin
# TC0093677.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *
from dstl.auxiliary import init
from dstl.security.lock_unlock_sim import *
from datetime import datetime
import time
import re


class Test(BaseTest):
    """Example test: Send AT command
    """

    def setup(test):

        test.dut.dstl_detect()

    def run(test):

        test.dut.dstl_unlock_sim()
        # Test Section 1:
        # Check test, write and read command for CTZR At cmd.
        res = test.dut.at1.send_and_verify("at+ctzr=?")
        test.expect("0-2" in test.dut.at1.last_response or "0-3" in test.dut.at1.last_response)

        # Disable event reporting for changes of timezone and daylight saving time.
        test.dut.at1.send_and_verify("at+ctzr=0", ".*OK.*")

        # Test incorrect value (5) for event reporting for changes of timezone and daylight saving time.
        test.dut.at1.send_and_verify("at+ctzr=5", ".*ERROR.*")

        # Check the current mode of event reporting for changes of time zone and daylight saving time.
        test.dut.at1.send_and_verify("at+ctzr?", ".*0.*")

        #  Enable automatic time zone update via NITZ.
        test.dut.at1.send_and_verify("at+ctzu=1")

        # Get current time and time zone.
        test.dut.at1.send_and_verify("at+cclk?", ".*OK.*")

        # Test Section 2
        # Check CTZR=1 :
        # Enable event reporting for changes of timezone and daylight saving time.
        test.dut.at1.send_and_verify("at+ctzr=1", ".*OK.*")
        test.dut.at1.send_and_verify("at+ctzr?", ".*1.*")

        test.log.info("Change the time zone and daylight saving time.\n")
        test.dut.at1.send_and_verify("at+cclk=\"10/03/19,16:26:43\"", ".*OK.*")

        # Try to detach and attach to the network, and wait for URC "+CTZV:<timezone>".
        test.dut.at1.send_and_verify("at+cgatt=0", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgatt=1", ".*OK.*", wait_for=".*CTZV:.*", append=True)

        #test.expect(".*+CTZV:.*" in test.dut.at1.last_response)


        # Get current local time.
        """
        def getLocalTime():

            dt = time.time()
            utc_offset = int((datetime.fromtimestamp(dt) - datetime.utcfromtimestamp(dt)).total_seconds() / 900)

            if utc_offset >= 0:
                    LocalDateTime = time.strftime("\"%y/%m/%d,%H:%M:%S\" +{:0>2d}".format(utc_offset))
                    print(LocalDateTime)
            else:
                    LocalDateTime = time.strftime("\"%y/%m/%d,%H:%M:%S\" -{:0>2d}".format(utc_offset))
                    print(LocalDateTime)
            return LocalDateTime

        localTime = getLocalTime()
        if time.localtime().tm_isdst:
              test.expect("+CTZU: {},1".format(localTime) in test.dut.at1.last_response)
        else:
              test.expect("+CTZU: {},0".format(localTime) in test.dut.at1.last_response)
        """
        # Test Section 3
        # Check CTZR=2:
        # Enable event reporting for changes of timezone and daylight saving time.
        test.dut.at1.send_and_verify("at+ctzr=2", ".*OK.*")
        test.dut.at1.send_and_verify("at+ctzr?", ".*OK.*")

        # Change the time zone and daylight saving time.
        test.log.info("Change the time zone and daylight saving time.\n")
        test.dut.at1.send_and_verify("at+cclk=\"10/03/19,16:26:43\"", ".*OK.*")
        test.dut.at1.send_and_verify("at+ctzu=1", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgatt=0", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgatt=1", ".*OK.*", wait_for=".*\+CTZE:.*", append=True)

        #test.expect(".*+CTZE:.*" in test.dut.at1.last_response)

        test.dut.at1.send_and_verify("at+cclk?", ".*OK.*")

        # Check the time is the current network time.
        # localtime = getLocalTime()
        # test.dut.at1.send_and_verify("at+cclk?", ".*OK.*")
        # test.expect(localtime in test.dut.at1.last_response)

        # Test Section 4
        # Check CTZR=3:
        test.dut.at1.send_and_verify("at+ctzr=3", ".*OK.*")
        test.dut.at1.send_and_verify("at+ctzr?", ".*OK.*")

        test.log.info("Change the time zone and daylight saving time.\n")
        test.dut.at1.send_and_verify("at+cclk=\"10/03/19,16:26:43\"", ".*OK.*")

        test.dut.at1.send_and_verify("at+ctzu=1", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgatt=0", ".*OK.*")
        test.dut.at1.send_and_verify("at+cgatt=1", ".*OK.*", waitfor=".*CTZEU:.*", append=True)

        #test.expect(".*+CTZEU:.*" in test.dut.at1.last_response)


    def cleanup(test):
        """
        # test cleanup - for example reboot module
        resp = test.dut.at1.send_and_verify("at+cfun=1,1")
        test.dut.at1.wait_for(".*SYSSTART.*|.*SYSLOADING.*", timeout = 90)
        """
        test.dut.at1.send_and_verify("at+ctzr=0", ".*OK.*")
        test.dut.at1.send_and_verify("at+ctzu=0", ".*OK.*")



if "__main__" == __name__:
    unicorn.main()
