# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104188.001 - TpSATSendSS_AR_SSTK


"""
This testcase is intended to test in Automatic mode the Proactive Command:
SEND SS
This command is issued by AT^SSTK.

Registration to network.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from tests.uicc.sat.ar_mode_send_ss import sendss_applet_sstk

class TpSATSendSS(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()

    def run(test):
        sendss_applet_sstk(test, 'AT^SSTK')


    def cleanup(test):
        test.dut.dstl_lock_sim()


if (__name__ == "__main__"):
    unicorn.main()
