# responsible: haofeng.dding@thalesgroup.com
# location: Dalian
# TC0107850.001
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
        NF04_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF05_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF06_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF07_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF08_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF09_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF10_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF11_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF12_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF13_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF14_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF15_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF16_goto_AF_B_restart(test)
        Set_re_init_flag(test)
        NF17_goto_AF_B_restart(test)


    def cleanup(test):
        pass

def NF04_goto_AF_B_restart(test):
    test.log.step('***** NF04_goto_AF_B flow start *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,4))
    test.log.step('***** NF04_goto_AF_B flow end *****')

def NF05_goto_AF_B_restart(test):
    test.log.step('***** NF05_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,5))
    test.log.step('***** NF05_goto_AF_B flow end *****')

def NF06_goto_AF_B_restart(test):
    test.log.step('***** NF06_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,6))
    test.log.step('***** NF06_goto_AF_B flow end *****')

def NF07_goto_AF_B_restart(test):
    test.log.step('***** NF07_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,7))
    test.log.step('***** NF07_goto_AF_B flow end *****')

def NF08_goto_AF_B_restart(test):
    test.log.step('***** NF08_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,8))
    test.log.step('***** NF08_goto_AF_B flow end *****')

def NF09_goto_AF_B_restart(test):
    test.log.step('***** NF09_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,9))
    test.log.step('***** NF09_goto_AF_B flow end *****')


def NF10_goto_AF_B_restart(test):
    test.log.step('***** NF10_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,10))
    test.log.step('***** NF10_goto_AF_B flow end *****')

def NF11_goto_AF_B_restart(test):
    test.log.step('***** NF11_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,11))
    test.log.step('***** NF11_goto_AF_B flow end *****')

def NF12_goto_AF_B_restart(test):
    test.log.step('***** NF12_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,12))
    test.log.step('***** NF12_goto_AF_B flow end *****')

def NF13_goto_AF_B_restart(test):
    test.log.step('***** NF13_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,13))
    test.log.step('***** NF13_goto_AF_B flow end *****')

def NF14_goto_AF_B_restart(test):
    test.log.step('***** NF14_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,14))
    test.log.step('***** NF14_goto_AF_B flow end *****')

def NF15_goto_AF_B_restart(test):
    test.log.step('***** NF15_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,15))
    test.log.step('***** NF15_goto_AF_B flow end *****')

def NF16_goto_AF_B_restart(test):
    test.log.step('***** NF16_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,16))
    test.log.step('***** NF15_goto_AF_B flow end *****')

def NF17_goto_AF_B_restart(test):
    test.log.step('***** NF17_goto_AF_B flow star *****')
    test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test,1,17))
    test.log.step('***** NF17_goto_AF_B flow end *****')
def Set_re_init_flag(test):
    test.log.step('***** Set the re_init_flag to False *****')
    resmed_ehealth_initmodule_normal_flow.set_reinit_flag(False)

if "__main__" == __name__:
    unicorn.main()