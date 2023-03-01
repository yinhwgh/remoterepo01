#responsible: thomas.troeger@thalesgroup.com
#location: Berlin
# 	TC0065663.001

import unicorn
from core.basetest import BaseTest

from dstl.internet_service import lwm2m_service
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary.check_urc import dstl_check_urc
import random


class Test(BaseTest):
    """ kurz Kommentar
    Non Blocking Cops Pops up


    """

    def __init__(self):
        super().__init__()
        self.dut = None

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        pass

    def run(test):
        # enable creg indication with at + creg=2
        test.dut.at1.send_and_verify("at+creg=2", "OK")

        # enable text error message format
        test.dut.at1.send_and_verify("at+cmee=2", "OK")

        # set indicator eons and nitz
        test.expect(test.dut.at1.send_and_verify(" AT^SIND=eons,1", '.*SIND: eons,1,0,"","",0.*'))
        test.sleep(5)
        # enter pin with at+cpin="PIN1" and wait for registration
        test.dut.dstl_enter_pin()
        #test.sleep(5)
        # wait for arriving indicators +ciev:  eons
        test.expect(test.dut.at1.wait_for(".*\+CIEV: eons,3,\".*", timeout=20))

        test.sleep(3)

        # deregister from network
        test.dut.at1.send_and_verify("AT+cops=2", ".*\+CIEV: eons,0,\"\",\"\",0.*")
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify(" AT+cops=0", ".*\+CIEV: eons,3,\".*", timeout=20))

        # register back to network and check if URTCs will arrive
        #test.dut.at1.wait_for("\+CIEV: eons,3,\"EDAV\",\"EDD-2259\",0", timeout=20)

        # for later expansion try to check the right time zone
        #test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        test.sleep(5)
        # repair  that means reset the indicators arrving etc.
        #test.dut.at1.send_and_verify("at+cops=0", "OK", timeout=5)
        test.expect(test.dut.at1.send_and_verify(" AT^SIND=eons,0", ".*\^SIND: eons,0,.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
