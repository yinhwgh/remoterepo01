#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105600.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import time
import re
import random
import string
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from tests.rq6 import smart_meter_init_module_normal_flow as init
from tests.rq6 import smart_meter_provide_data_connection_normal_flow as provide_data

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        init.uc_init_module(test, 1)
        provide_data.set_time_to_sleep(10)
        NF02_goto_EF_A_restart(test)
        NF04_goto_EF_A_restart(test)
        NF05_goto_EF_A_restart(test)

    def uc_read_status(test,start_step):
        pass

    def cleanup(test):
        pass

def NF02_goto_EF_A_restart(test):
    test.log.step('***** NF02_goto_AF_A_restart flow start *****')
    test.expect(provide_data.uc_provide_data_connection(test,start=1,end=1))
    init.mc_remove_sim(test)
    test.expect(provide_data.uc_provide_data_connection(test, start=2, end=12))
    test.log.step('***** NF02_goto_AF_A_restart flow end *****')

def NF03_goto_EF_A_restart(test):
    test.log.step('***** NF03_goto_EF_A_restart flow start *****')
    test.expect(provide_data.uc_provide_data_connection(test, start=1, end=2))
    init.mc_remove_sim(test)
    test.expect(provide_data.uc_provide_data_connection(test, start=3, end=12))
    test.log.step('***** NF03_goto_EF_A_restart flow end *****')

def NF04_goto_EF_A_restart(test):
    test.log.step('***** NF04_goto_EF_A_restart flow start *****')
    test.expect(provide_data.uc_provide_data_connection(test, start=1, end=3))
    init.mc_remove_sim(test)
    test.expect(provide_data.uc_provide_data_connection(test, start=4, end=12))
    test.log.step('***** NF04_goto_EF_A_restart flow end *****')

def NF05_goto_EF_A_restart(test):
    test.log.step('***** NF05_goto_EF_A_restart flow start *****')
    test.expect(provide_data.uc_provide_data_connection(test, start=1, end=4))
    init.mc_deregister_network(test)
    test.expect(provide_data.uc_provide_data_connection(test, start=5, end=12))
    test.log.step('***** NF05_goto_EF_A_restart flow end *****')

if "__main__" == __name__:
    unicorn.main()
