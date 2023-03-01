#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105606.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import time
import datetime
import re
import random
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.network_service import register_to_network
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.internet_service.parser.internet_service_parser import Command
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_send_metering_data_normal_flow
from tests.rq6 import smart_meter_provide_data_connection_normal_flow as provide_data

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        smart_meter_init_module_normal_flow.set_run_all(False)
        smart_meter_init_module_normal_flow.set_listener_mode(True)
        provide_data.set_time_to_sleep(60)
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        provide_data.uc_provide_data_connection(test, start=1, end=8)
        test.log.step(
            '[ProvideConnection]:NF-09 server exchanges some data with the application from 50kBytes to 500kBytes')
        test.r1.at1.send('AT^SIST=1')
        test.r1.at1.wait_for('CONNECT', 5)
        data = dstl_generate_data(random.randint(2000, 10000))
        test.r1.at1.send(data)
        time.sleep(120)
        smart_meter_send_metering_data_normal_flow.uc_send_metering_data(test,expect_dcd_active=True)
        provide_data.uc_provide_data_connection(test, start=10, end=10)
        smart_meter_send_metering_data_normal_flow.uc_send_metering_data(test,expect_dcd_active=False)
        return True

        
    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()