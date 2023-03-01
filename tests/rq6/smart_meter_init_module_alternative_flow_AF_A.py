# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0105596.001
# Hints:
# ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import time
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import smart_meter_adjust_clock_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import smart_meter_init_module_normal_flow


class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        NF08_goto_AF_A_restart(test)
        NF11_goto_AF_A_restart(test)
        NF13_goto_AF_A_restart(test)

    def cleanup(test):
        pass

def NF04_goto_AF_A_restart(test):
    test.log.step('***** NF04_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1,4))
    test.log.step('***** NF04_goto_AF_A flow end *****')

def NF07_goto_AF_A_restart(test):
    test.log.step('***** NF07_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1, 7))
    test.log.step('***** NF07_goto_AF_A flow end *****')

def NF08_goto_AF_A_restart(test):
    test.log.step('***** NF08_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1, 8))
    test.log.step('***** NF08_goto_AF_A flow end *****')

def NF09_goto_AF_A_restart(test):
    test.log.step('***** NF09_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1, 9))
    test.log.step('***** NF09_goto_AF_A flow end *****')

def NF10_goto_AF_A_restart(test):
    test.log.step('***** NF10_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1, 10))
    test.log.step('***** NF10_goto_AF_A flow end *****')

def NF11_goto_AF_A_restart(test):
    test.log.step('***** NF11_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1, 11))
    test.log.step('***** NF11_goto_AF_A flow end *****')

def NF13_goto_AF_A_restart(test):
    test.log.step('***** NF13_goto_AF_A flow start *****')
    test.expect(smart_meter_init_module_normal_flow.uc_init_module(test,1, 13))
    test.log.step('***** NF13_goto_AF_A flow end *****')



if "__main__" == __name__:
    unicorn.main()
