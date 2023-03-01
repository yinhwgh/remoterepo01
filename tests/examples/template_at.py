# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_at

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    """Example test: Send AT command
    """
    def setup(test):
        """
        # query product version with ati
        res = test.dut.at1.send_and_verify("ati", ".*")

        # log the message that module returned (last_response) as info
        test.log.info(test.dut.at1.last_response)

        # query product version with at^cicret
        res = test.dut.at1.send_and_verify("at^cicret=\"swn\"")

        # log the message that module returned (last_response) as info
        test.log.info(test.dut.at1.last_response)

        # query product version with at^cicret, append response to current last_response value
        # last_response should contain now output from both recently run commands
        res = test.dut.at1.send_and_verify("at^cicret=\"swn\"", append=True)
        test.log.info(test.dut.at1.last_response)
        """
        pass

    def run(test):
        """
        # loop from 1 to 2:
        for i in range(1, 2):
            test.log.info("Iteration: {}".format(i))

            # sending command and verifying if response matches expected one - response should contain "OK"
            status = test.dut.at1.send_and_verify("at", "OK")

            # logging True or False
            test.log.info(status)

            # sending command and verifying if response matches expected one - response should be exactly as the RegEx phrase
            status = test.dut.at1.send_and_verify("at", "^.*OK.*$")

            # logging True or False
            test.log.info(status)

            # expect is a test method to verify conditions: True or False
            test.expect(status)

        # read PIN1 of DUT's SIM card
        pin_value = test.dut.sim.pin1

        # log the PIN value - format puts real value into the brackets
        test.log.info("Read PIN value: {}".format(pin_value))

        # query PIN status
        test.dut.at1.send_and_verify("at+cpin?")
        if "READY" in test.dut.at1.last_response:
            test.log.info("PIN is already entered")
        elif "CPIN" in test.dut.at1.last_response:
            test.log.info("Entering PIN")
            test.dut.at1.send_and_verify("at+cpin=\"{}\"".format(pin_value))
            # holding test execution for 10 seconds
            test.sleep(5)
        else:
            # unknown SIM state - test is not aware how to proceed so it will break here
            test.log.error("Unknown SIM state")
            # expect(False) will log error, critical = True will stop the test
            test.expect(False, critical=True)

        res = test.dut.at1.send_and_verify("at+creg=2", wait_for="OK")
        res = test.dut.at1.send_and_verify("at+cereg=2", wait_for="OK")
        res = test.dut.at1.send_and_verify("at+cgreg=2", wait_for="OK")
        res = test.dut.at1.send_and_verify("at+cops=?", ".*OK.*", wait_for="OK", timeout=90)

        test.dut.at1.send("at")
        test.dut.at1.wait_for("OK")

        for i in range(1):
            res = test.dut.at1.send_and_verify("at+csq", "OK", wait_for="OK")
            res = test.dut.at1.send_and_verify("at+creg?", "OK", wait_for="OK")
            res = test.dut.at1.send_and_verify("at+cereg?", "OK", wait_for="OK")
            res = test.dut.at1.send_and_verify("at+cgreg?", "OK", wait_for="OK")
            test.dut.at1.send("at+cops=?")
            test.dut.at1.wait_for("OK", timeout=90)
            test.sleep(1)
        """
        pass

    def cleanup(test):
        """
        # test cleanup - for example reboot module
        resp = test.dut.at1.send_and_verify("at+cfun=1,1")
        test.dut.at1.wait_for(".*SYSSTART.*|.*SYSLOADING.*", timeout = 90)
        """
        pass

if "__main__" == __name__:
    unicorn.main()
