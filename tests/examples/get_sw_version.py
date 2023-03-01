# responsible: marian.schmidt@globallogic.com
# location: Berlin
# TC0000001.001 get_sw_version

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    """Example test: querry SW build version and return status PASSED
    This testcase can be used for validation of SW version after SWUP and CI bringup

    Example URL: https://blnjenkins.gemalto.com/view/M2M_Projects/view/Bobcat_2.0/job/Bobcat2_Unicorn/
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

        pass

    def run(test):

        # query product version with at^cicret
        res = test.dut.at1.send_and_verify("at^cicret=\"swn\"")


        # log the message that module returned (last_response) as info
        test.log.info(test.dut.at1.last_response)

        # set test case status to PASS
        test.expect(True)

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
