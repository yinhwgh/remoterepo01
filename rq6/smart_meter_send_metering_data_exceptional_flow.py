#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105605.001
import unicorn
import time
import datetime
import re
from core.basetest import BaseTest

from dstl.network_service import register_to_network
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.internet_service.parser.internet_service_parser import Command
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_send_metering_data_normal_flow


class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        smart_meter_init_module_normal_flow.set_listener_mode(False)
        NF03_goto_EF_A_restart(test)
        NF05_goto_EF_A_restart(test)

    def cleanup(test):
        pass


def NF03_goto_EF_A_restart(test):
    test.log.step('***** NF03_goto_EF_A_restart flow start *****')
    test.expect(smart_meter_send_metering_data_normal_flow.uc_send_metering_data(test,3))
    test.log.step('***** NF03_goto_EF_A_restart flow end *****')

def NF05_goto_EF_A_restart(test):
    test.log.step('***** NF05_goto_EF_A_restart flow start *****')
    test.expect(smart_meter_send_metering_data_normal_flow.uc_send_metering_data(test,5))
    test.log.step('***** NF05_goto_EF_A_restart flow end *****')


if "__main__" == __name__:
    unicorn.main()
