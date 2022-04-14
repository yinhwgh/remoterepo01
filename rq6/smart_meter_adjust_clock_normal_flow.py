# responsible: shuang.linag@thalesgroup.com
# location: Beijing
# TC0105520.001 - SmartMeter_adjustClock_normalFlow
# Hints:
# ntp_address should be defined in local.cfg currently,such as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,such as apn="internet"

import unicorn
import time
import datetime
import re
from core.basetest import BaseTest

from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_provide_data_connection_normal_flow
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(False)
        smart_meter_init_module_normal_flow.set_listener_mode(False)

    def run(test):

        uc_adjust_clock_normal_flow(test)

    def cleanup(test):
        pass

def uc_adjust_clock_normal_flow(test):
    test.log.info('NF_05_uc_adjust_clock begin')
    test.log.step('NF-01: check for listener mode')

    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('uc_adjust_clock_normal_flow - NF-01: Check for listener mode with DCD checking and closing listener', True)
    else:
        test.dut.dstl_collect_result('uc_adjust_clock_normal_flow - NF-01: Check for listener mode without operation of DCD checking and closing listener', True)

    test.log.step('NF-02: close, configure and restart the IP service bearer1')
    test.dut.dstl_collect_result('uc_adjust_clock_normal_flow - NF-02',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_init_module_normal_flow.restart_ip_service_bearer, smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-03: start this NTP service to query the UTC info (e.g. addressing "pool.ntp.org")')
    test.log.step('NF-04: Adjusts its clock with received UTC info')
    test.dut.dstl_collect_result('uc_adjust_clock_normal_flow - NF-03---NF-04', test.expect(convert_utc_to_local(test)))

    test.log.step('NF-05: check for listener mode')
    if smart_meter_init_module_normal_flow.get_run_all() == True:
        smart_meter_init_module_normal_flow.set_listener_mode(True)
        if smart_meter_init_module_normal_flow.check_listener_mode(test) == True:
            test.dut.dstl_collect_result('uc_adjust_clock_normal_flow - NF-05: Check for listener mode during duration test--It should be true and got to UC ProvideDataConnection', True)
            return
    elif smart_meter_init_module_normal_flow.get_run_all() == False:
            if smart_meter_init_module_normal_flow.check_listener_mode(test):
                if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
                    return
                else:
                    smart_meter_init_module_normal_flow.close_listener(test)
                    test.dut.dstl_collect_result(
                        'uc_adjust_clock_normal_flow - NF-05: Check for listener mode with DCD checking and closing listener', True)
            test.dut.dstl_collect_result('uc_adjust_clock_normal_flow - NF-05: Check for listener mode without operation of DCD checking and closing listener', True)

    test.dut.dstl_print_results()
    test.log.info('NF_05_uc_adjust_clock end')

    return True


def convert_utc_to_local(test):
    result = True
    # get time zone from network
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CTZU=1", ".*OK|.*0"))
    i=1
    while (not test.dut.at1.send_and_verify("AT+CREG?", ".*\+CREG: 0,1")) and (i<=5):
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '^0.*', timeout=20))
        i+=1
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CCLK?', ".*OK|.*0"))
    sStr = test.dut.at1.last_response
    start_index = sStr.index('+CCLK: "', 0, len(sStr)) + len('+CCLK: "')
    tz_label = sStr[start_index + 17]
    timezone = sStr[start_index + 18:start_index + 20]
    tz_to_hour = int(timezone) / 4

    #get UTC time from NTP service.
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SICA=1,1", ".*OK|.*0"))
    results = test.expect(test.dut.at1.send_and_verify('AT^SISX="NTP",1,"' + test.ntp_server_address + '"', ".*OK|.*0"))
    if results is True:
        sStr = test.dut.at1.last_response
        start_index = sStr.index('^SISX: "Ntp","', 0, len(sStr)) + len('^SISX: "Ntp","')
        origin_date_str = sStr[start_index:start_index + 19]

        # calculate local time
        utc_date = datetime.datetime.strptime(origin_date_str, "%Y-%m-%dT%H:%M:%S")
        local_date = utc_date + datetime.timedelta(hours=tz_to_hour)
        local_date_str = datetime.datetime.strftime(local_date, '%y/%m/%d,%H:%M:%S')

        # set local time
        result = result & test.expect(test.dut.at1.send_and_verify('AT+CCLK="' + local_date_str + tz_label + timezone + '"', ".*OK|.*0"))
    result = result & results

    result = result & test.expect(test.dut.at1.send_and_verify("AT+CTZU=0", ".*OK|.*0"))
    return result


if "__main__" == __name__:
    unicorn.main()
