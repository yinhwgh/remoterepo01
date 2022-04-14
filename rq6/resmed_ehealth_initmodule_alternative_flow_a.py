# responsible: haofeng.dding@thalesgroup.com
# location: Dalian
# TC0107804.001
# Hints:
# ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
# The SIM card should not with PIN
import unicorn
import time
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import smart_meter_adjust_clock_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import resmed_ehealth_initmodule_normal_flow


class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        NF02_goto_AF_A_restart(test)


    def cleanup(test):
        pass

def NF02_goto_AF_A_restart(test):
    test.log.step('***** NF04_goto_AF_A flow start *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,2))
    test.log.step('***** NF04_goto_AF_A flow end *****')



if "__main__" == __name__:
    unicorn.main()