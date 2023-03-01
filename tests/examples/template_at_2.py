# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_at2

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    """Example test: Send AT command
    """
    def setup(test):

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

    def run(test):

        test.log.info("Query PIN status")
        test.dut.at1.send_and_verify("at+cpin?")
        if "READY" in test.dut.at1.last_response:
            test.log.info("PIN is already entered")
        elif "CPIN" in test.dut.at1.last_response:
            test.log.info("Entering PIN")
            test.dut.at1.send_and_verify("at+cpin=\"{}\"".format(test.dut.sim.pin1))
            test.sleep(5)
        else:
            test.log.error("Unknown SIM state")
            test.expect(False, critical=True)

        for i in range(2):
            res = test.dut.at1.send_and_verify("at+csq", "OK", wait_for="OK")
            test.expect(res)
            res = test.dut.at1.send_and_verify("at+creg?", "OK", wait_for="OK")
            test.expect(res)
            res = test.dut.at1.send_and_verify("at+cereg?", "OK", wait_for="OK")
            test.expect(res)
            res = test.dut.at1.send_and_verify("at+cgreg?", "OK", wait_for="OK")
            test.expect(res)
            test.sleep(1)

    def cleanup(test):
        """
        # test cleanup - for example reboot module
        resp = test.dut.at1.send_and_verify("at+cfun=1,1")
        test.dut.at1.wait_for(".*SYSSTART.*|.*SYSLOADING.*", timeout = 90)
        """
        pass


if "__main__" == __name__:
    unicorn.main()
