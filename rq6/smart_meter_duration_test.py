#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105599.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import time
import re
import random
import string
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from tests.rq6 import smart_meter_init_module_normal_flow as init
from tests.rq6 import smart_meter_provide_data_connection_normal_flow as provide_data
from tests.rq6 import smart_meter_send_metering_data_normal_flow as send_metering_data
from tests.rq6 import smart_meter_download_configuration_file_normal_flow as download_configuration_file
from tests.rq6 import smart_meter_download_configuration_file_exceptional_flow as download_configuration_file_exceptional_flow
from tests.rq6 import smart_meter_download_configuration_file_alternative_flow as download_configuration_file_alternative_flow
from tests.rq6 import smart_meter_update_application_normal_flow as update_application
from tests.rq6 import smart_meter_update_application_alternative_flow as update_application_alternative_flow
from tests.rq6 import smart_meter_update_application_exceptional_flow as update_application_exceptional_flow
from tests.rq6 import smart_meter_adjust_clock_normal_flow as adjust_clock
from tests.rq6 import smart_meter_adjust_clock_exceptional_flow as adjust_clock_exceptional_flow
from tests.rq6 import smart_meter_adjust_clock_alternative_flow as adjust_clock_alternative_flow
from tests.rq6 import smart_meter_send_alert_message_normal_flow_update as send_alert_message
from tests.rq6 import smart_meter_send_alert_message_alternative_flow as send_alert_message_alternative_flow
from tests.rq6 import smart_meter_send_alert_message_exceptional_flow as send_alert_message_exceptional_flow
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.init import dstl_detect

class Test(BaseTest):
    def setup(test):
        test.r1.dstl_detect()
        test.r1.at1.send_and_verify(f'at+cgdcont=1,"ipv4v6",{test.r1.sim.apn_v4}')
        pass

    def run(test):
        
        test.log.step('RunAll-1.init')
        init.set_run_all(True)
        provide_data.set_time_to_sleep(10)
        init.uc_init_module(test, 1)
        init.set_listener_mode(True)
        test.dut.dstl_print_results()
        max_time = 43200
        start_time = time.time()
        test.log.step('StartTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)))
        while ((time.time() - start_time) < max_time):
            test.log.step('RunAll-2.execute provide data use case some times')
            test.dut.dstl_collect_result('RunAll-2.execute provide data use case some times', provide_data_some_times(test))
            test.dut.dstl_print_results()

            test.log.step('RunAll-3.execute send metering data use case with FTPS,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-3.execute send metering data use case with FTPS,when NO data transmission ongoing',
                                         send_metering_data_DCD_inactive(test, ftpes=False))
            test.dut.dstl_print_results()

            test.log.step('RunAll-4.execute send metering data use case with FTPES,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-4.execute send metering data use case with FTPES,when NO data transmission ongoing',
                                         send_metering_data_DCD_inactive(test, ftpes=True))
            test.dut.dstl_print_results()

            test.log.step('RunAll-5.execute send metering data use case with FTPS,when data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-5.execute send metering data use case with FTPS,when data transmission ongoing',
                                         send_metering_data_DCD_active(test, ftpes=False))
            test.dut.dstl_print_results()
            test.log.step('RunAll-6.execute send metering data use case with FTPES,when data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-6.execute send metering data use case with FTPES,when data transmission ongoing',
                                         send_metering_data_DCD_active(test, ftpes=True))
            test.dut.dstl_print_results()
            test.log.step('RunAll-7.execute download configuration file use case with FTPS,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-7.execute download configuration file use case with FTPS,when NO data transmission ongoing',
                                         download_configuration_file_DCD_inactive(test, sftpes=False))
            test.dut.dstl_print_results()
            test.log.step('RunAll-8.execute download configuration file use case with FTPES,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-8.execute download configuration file use case with FTPES,when NO data transmission ongoing',
                                         download_configuration_file_DCD_inactive(test, sftpes=True))
            test.dut.dstl_print_results()
            test.log.step('RunAll-9.execute download configuration file use case with FTPS,when data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-9.execute download configuration file use case with FTPS,when NO data transmission ongoing',
                                         download_configuration_file_DCD_active(test, sftpes=False))
            test.dut.dstl_print_results()
            test.log.step('RunAll-10.execute download configuration file use case with FTPES,when data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-10.execute download configuration file use case with FTPES,when NO data transmission ongoing',
                                         download_configuration_file_DCD_active(test, sftpes=True))
            test.dut.dstl_print_results()
            test.log.step('RunAll-11.execute update_application use case with FTPS,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-11.execute update_application use case with FTPS,when NO data transmission ongoing',
                                         update_application_DCD_inactive(test, sftpes=False))
            test.dut.dstl_print_results()
            test.log.step('RunAll-12.execute update_application file use case with FTPES,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-12.execute update_application file use case with FTPES,when NO data transmission ongoing',
                                         update_application_DCD_inactive(test, sftpes=True))
            test.dut.dstl_print_results()
            test.log.step('RunAll-13.execute update_application use case with FTPS,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-13.execute update_application use case with FTPS,when NO data transmission ongoing',
                                         update_application_DCD_active(test, sftpes=False))
            test.dut.dstl_print_results()
            test.log.step('RunAll-14.execute update_application file use case with FTPES,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-14.execute update_application file use case with FTPES,when NO data transmission ongoing',
                                         update_application_DCD_active(test, sftpes=True))
            test.dut.dstl_print_results()
            test.log.step('RunAll-15.execute send alert message use case,when NO data transmission ongoing')
            test.dut.dstl_collect_result('RunAll-15.execute send alert message use case,when NO data transmission ongoing',
                                         send_alert_message.send_alert_message_normal_flow_update(test))
            test.dut.dstl_print_results()
            
        test.log.step('EndTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        return

    def cleanup(test):
        pass
    
def provide_data_some_times(test):
    j = random.randint(1, 3)
    for i in range(0, j):
        provide_data.uc_provide_data_connection(test)
    return True
        
def send_metering_data_DCD_inactive(test,ftpes):
    end_step=random.randint(2, 7)
    test.log.step('Call uc_provide_data_connection end step is '+str(end_step))
    provide_data.uc_provide_data_connection(test,start=1, end=end_step)
    send_metering_data.uc_send_metering_data(test, ftpes=ftpes,expect_dcd_active=False)
    return True

def send_metering_data_DCD_active(test,ftpes):
    provide_data.uc_provide_data_connection(test,start=1, end=8)
    test.log.step('[ProvideConnection]:NF-09 server exchanges some data with the application from 50kBytes to 500kBytes')
    test.r1.at1.send('AT^SIST=1')
    test.r1.at1.wait_for('CONNECT', 5)
    data = dstl_generate_data(random.randint(2000,10000))
    test.r1.at1.send(data)
    time.sleep(120)
    send_metering_data.uc_send_metering_data(test, ftpes=ftpes, expect_dcd_active=True)
    end_step = random.randint(10, 12)
    test.log.step('Call uc_provide_data_connection end step is ' + str(end_step))
    provide_data.uc_provide_data_connection(test, start=10, end=end_step)
    send_metering_data.uc_send_metering_data(test, ftpes=ftpes,expect_dcd_active=False)
    return True

def download_configuration_file_DCD_inactive(test,sftpes):
    end_step=random.randint(2, 7)
    test.log.step('Call uc_provide_data_connection end step is '+str(end_step))
    results = test.expect(provide_data.uc_provide_data_connection(test,start=1, end=end_step))
    results = results & test.expect(download_configuration_file.download_configuration_file_normal_flow(test, sftpes=sftpes, expect_dcd_active=False))
    return results

def download_configuration_file_DCD_active(test,sftpes):
    results = provide_data.uc_provide_data_connection(test,start=1, end=8)
    test.log.step('[ProvideConnection]:NF-09 server exchanges some data with the application from 50kBytes to 500kBytes')
    test.r1.at1.send('AT^SIST=1')
    results = results & test.expect(test.r1.at1.wait_for('CONNECT', 5))
    data = dstl_generate_data(random.randint(2000, 10000))
    test.r1.at1.send(data)
    time.sleep(120)
    results = results & test.expect(download_configuration_file.download_configuration_file_normal_flow(test, sftpes=sftpes, expect_dcd_active=True))
    end_step = random.randint(10, 12)
    test.log.step('Call uc_provide_data_connection end step is ' + str(end_step))
    results = results & test.expect(provide_data.uc_provide_data_connection(test, start=10, end=end_step))
    results = results & test.expect(download_configuration_file.download_configuration_file_normal_flow(test, sftpes=sftpes, expect_dcd_active=False))
    return results

def update_application_DCD_inactive(test,sftpes):
    end_step=random.randint(2, 7)
    test.log.step('Call uc_provide_data_connection end step is '+str(end_step))
    results = test.expect(provide_data.uc_provide_data_connection(test,start=1, end=end_step))
    results = results & test.expect(update_application.update_application_normal_flow(test, sftpes=sftpes, expect_dcd_active=False))
    return results

def update_application_DCD_active(test,sftpes):
    results = test.expect(provide_data.uc_provide_data_connection(test,start=1, end=8))
    test.log.step('[ProvideConnection]:NF-09 server exchanges some data with the application from 50kBytes to 500kBytes')
    test.r1.at1.send('AT^SIST=1')
    results = results & test.expect(test.r1.at1.wait_for('CONNECT', 5))
    data = dstl_generate_data(random.randint(2000, 10000))
    test.r1.at1.send(data)
    time.sleep(120)
    results = results & test.expect(update_application.update_application_normal_flow(test, sftpes=sftpes, expect_dcd_active=True))
    end_step = random.randint(10, 12)
    test.log.step('Call uc_provide_data_connection end step is ' + str(end_step))
    results = results & test.expect(provide_data.uc_provide_data_connection(test, start=10, end=end_step))
    results = results & test.expect(update_application.update_application_normal_flow(test, sftpes=sftpes, expect_dcd_active=False))
    return results

if "__main__" == __name__:
    unicorn.main()
