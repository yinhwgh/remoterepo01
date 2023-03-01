# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104264.001 - TpSATSelectItemSSTK

"""
This testcase is intended to test in Automatic Mode, the Proactive Command:
SELECT ITEM
Command is issued by AT^SSTK

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from tests.uicc.sat.ar_mode_select_item import selectitem_applet_sstk

class TpSATSelectItem(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()


    def run(test):
        selectitem_applet_sstk(test, 'AT^SSTK')

    def cleanup(test):
        # erase Proactive command in record 1#
        test.log.info("***** Erase record #1 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(1, '')
        test.dut.dstl_lock_sim()



if (__name__ == "__main__"):
    unicorn.main()