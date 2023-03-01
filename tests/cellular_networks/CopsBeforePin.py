#responsible: thomas.troeger@thalesgroup.com
#location: Berlin
#TC0088045.001

import unicorn
from core.basetest import BaseTest

from dstl.internet_service import lwm2m_service
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
import random


class Test(BaseTest):
    """ kurz Kommentar """

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

        # check at + cops =?  ----> ERROR SIM_NOT_INSERTED
        test.expect(test.dut.at1.send_and_verify("at+cops=?", '.*ERROR: SIM PIN required.*'))

        # check at + cops?    ----> ERROR SIM_NOT_INSERTED
        test.dut.at1.send_and_verify("at+cops?", '.*ERROR: SIM PIN required.*')

        # check at + cops - ---> ERROR
        test.dut.at1.send_and_verify("at+cops", '.*CME ERROR: unknown.*')

        # check at + cops = 2 - -----> ERROR(deregistering is not allowed in restricted mode)
        test.dut.at1.send_and_verify("at+cops=2", '.*ERROR: SIM PIN required.*')

        # check at + cops = 3, 1 - ---> ERROR
        test.dut.at1.send_and_verify("at+cops=3.1", '.*CME ERROR: invalid index.*')

        # check at + cops = 3, 2 - ---> ERROR
        test.dut.at1.send_and_verify("at+cops=3.2", '.*CME ERROR: invalid index.*')

        # check at + cops = 0 - ---> OK
        test.dut.at1.send_and_verify("at+cops=0", "OK")

        # check at + cops = 2 - ---> ERROR INVALID_INDEX
        test.dut.at1.send_and_verify("at+cops=2", '.*CME ERROR: SIM PIN required.*')

        # check at + cops = 1, 2, 26201 - ---> OK
        test.expect(test.dut.at1.send_and_verify("at+cops=1,2,26301", "OK"))

        # insert sim with PIN1 enabled( PIN required)  no Telekom sim   use 301 ****

        # check at + cops =?  ----> ERROR SIM_PIN_REQUIRED
        test.dut.at1.send_and_verify("at+cops=?", '.*CME ERROR: SIM PIN required.*')

        # check at + cops?    ----> ERROR SIM_PIN_REQUIRED
        test.dut.at1.send_and_verify("at+cops?", '.*CME ERROR: SIM PIN required.*')

        # check at + cops - ---> ERROR
        test.dut.at1.send_and_verify("at+cops", '.*CME ERROR: unknown.*')

        # check at + cops = 0 - ---> OK
        test.dut.at1.send_and_verify("at+cops=0", "OK")

        # check at + cops = 2 - ---> ERROR INVALID_INDEX
        test.dut.at1.send_and_verify("at+cops=2", '.*CME ERROR: SIM PIN required.*')

        # check at + cops = 1, 2, 26201 - ---> OK
        test.dut.at1.send_and_verify("at+cops=1,2,26301", "OK")

        # enter PIN1 with at + cpin="PIN1"  wait  for +CREG: 4 indication
        test.dut.dstl_enter_pin()
        # test.sleep(10)
        test.expect(test.dut.dstl_check_urc('.*[+]CREG: 4.*', 60))
        #  enter at + cops = 0 wait for registration + creg: 1
        test.dut.at1.send_and_verify('at+cops=0', 'OK')
        test.expect(test.dut.dstl_check_urc('.*[+]CREG: 1.*', 60))

        # test.sleep(5)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
