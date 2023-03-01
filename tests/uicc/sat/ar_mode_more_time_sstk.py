# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104259.001 - TpSATMoreTimeSSTK

"""
This test case is intended to test the SIM proactive command "MORE TIME" by means of AT command AT^SSTK= <proactive command>

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from tests.uicc.sat.ar_mode_more_time import moretime_applet_sstk


class TpSATMoreTime(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()

    def run(test):
        moretime_applet_sstk(test, 'AT^SSTK')

    def cleanup(test):
        test.dut.dstl_lock_sim()



if (__name__ == "__main__"):
    unicorn.main()
