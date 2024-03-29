# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104265.001 - TpSATRefreshSSTK

"""
This test case is intended to test the SIM proactive command "REFRESH" by means of execution of AT command AT^SSTK
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from tests.uicc.sat.ar_mode_refresh import refresh_applet_sstk


class TpSATRefresh(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("1. Disble SIM PIN lock before testing  ")
        test.dut.dstl_unlock_sim()

    def run(test):
        refresh_applet_sstk(test, 'AT^SSTK')

    def cleanup(test):
        test.dut.dstl_lock_sim()



if (__name__ == "__main__"):
    unicorn.main()
