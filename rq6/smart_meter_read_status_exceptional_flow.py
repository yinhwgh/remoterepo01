#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105602.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import re

from core.basetest import BaseTest
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        smart_meter_init_module_normal_flow.uc_init_module(test,1,14)
        smart_meter_read_status_normal_flow.uc_read_status(test,exceptional_step=5)

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
