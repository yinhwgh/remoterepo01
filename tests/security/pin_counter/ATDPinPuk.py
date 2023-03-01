#responsible: thomas.troeger@thalesgroup.com
#location: Berlin
# TC0010112.001

import unicorn
from core.basetest import BaseTest

from dstl.internet_service import lwm2m_service
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary.check_urc import dstl_check_urc
import random


class Test(BaseTest):
    """ kurz
    Umsetzung des TC zur EIngabe der PUK per ATD*# commands

    Kommentar """

    def __init__(self):
        super().__init__()
        self.dut = None

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        pass

    def run(test):
        # get PIN1 from webimacs properties
        pin1 = test.dut.sim.pin1
        test.log.info('Pin1:' + pin1)

        # enable creg indication with at + creg=2
        test.dut.at1.send_and_verify("at+creg=2", "OK")

        # enable text error message format
        test.dut.at1.send_and_verify("at+cmee=2", "OK")

        # enter pin with at+cpin="PIN1" and wait for registration
        test.dut.dstl_enter_pin()
        test.sleep(15)


        # pin change to newer pin
        test.expect(test.dut.at1.send_and_verify("atd**04*"+pin1+"*3333*3333#;", "OK"))

        # pin change to old pin back
        test.expect(test.dut.at1.send_and_verify("atd**04*3333*" + pin1 + "*"+pin1+"#;", "OK"))
        # dut restart for disabling pin
        test.dut.dstl_restart()

        # Pineingabe 1 falsch
        test.dut.at1.send_and_verify("at+cpin=\"3333\"", '.*\+CME ERROR: incorrect password.*')

        #checke PIN counter normal (nicht cpinr!)
        test.expect(test.dut.at1.send_and_verify("at^spic?",  ".*\^SPIC: SIM PIN.*"))

        # Pineingabe 2 falsch
        test.dut.at1.send_and_verify("at+cpin=\"3333\"", '.*\+CME ERROR: incorrect password.*')

        # check Pin counter
        test.expect(test.dut.at1.send_and_verify("at^spic?", ".*\^SPIC: SIM PIN.*"))

        # Pineingabe 3 falsch
        test.expect(test.dut.at1.send_and_verify("at+cpin=\"3333\"", '.*\+CME ERROR: SIM PUK required.*'))

        # checke PIN counter und PUK counter
        test.expect(test.dut.at1.send_and_verify("at^spic?",  ".*\^SPIC: SIM PUK.*"))

        # setze alte PIN mit der PUK zurück
        puk1 = test.dut.sim.puk1
        test.log.info('Puk1:' + puk1)

        test.expect(test.dut.at1.send_and_verify("atd**05*"+puk1+"*"+pin1+"*"+pin1+"#;", "OK"))

        # checke PIN/PUK counter
        test.expect(test.dut.at1.send_and_verify("at^spic?", "OK"))

        # testcase am Ende
        # merke Dir das Ende



        test.sleep(5)



    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
