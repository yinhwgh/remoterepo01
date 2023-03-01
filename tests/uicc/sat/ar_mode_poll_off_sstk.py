#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0104272.001 - TpSATPollingOff_AR_SSTK

"""
This testcase is intended to test in Automatic mode the Proactive Command:
POLLING OFF
This command is issued by AT^SSTK
"""

import unicorn
import random
import re
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.network_service.register_to_network import *
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.status_control import extended_indicator_control
from dstl.usat.ssta_command import *
from dstl.usat.sim_instance import *
from tests.uicc.sat.ar_mode_poll_off import polloff_applet_sstk



class TpSATPollOff(BaseTest):


    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.log.info("***Disble SIM PIN lock before testing *** ")
        test.dut.dstl_unlock_sim()


    def run(test):
        polloff_applet_sstk(test,'AT^SSTK')

    def cleanup(test):
        test.dut.dstl_lock_sim()


if (__name__ == "__main__"):
    unicorn.main()
