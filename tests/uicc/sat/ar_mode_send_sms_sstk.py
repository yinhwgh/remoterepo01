# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104267.001 - TpSATSendSMSSSTK

"""
This test case is intended to test the SIM proactive command "SEND SHORT MESSAGE" by means of AT command AT^SSTK
Registration to network.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from dstl.sms import sms_center_address
from dstl.sms import sms_configurations
from dstl.sms import select_sms_format
from tests.uicc.sat.ar_mode_send_sms import sendsms_applet_sstk

class TpSATSendSMS(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("***** Disble SIM PIN lock before testing ****")
        test.dut.dstl_unlock_sim()



    def run(test):
        sendsms_applet_sstk(test, 'AT^SSTK')


    def cleanup(test):
        test.dut.dstl_lock_sim()



if (__name__ == "__main__"):
    unicorn.main()
