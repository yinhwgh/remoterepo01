# responsible: shuang.linag@thalesgroup.com
# location: Beijing
# TC0105529.001 - SmartMeter_adjustClock_exceptionalFlow
# Hints:
# ntp_address should be defined in local.cfg currently,such as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,such as apn="internet"

import unicorn
import time
import datetime
import re
import os
from core.basetest import BaseTest

from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_provide_data_connection_normal_flow
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)

    def run(test):
        adjust_clock_exceptional_flow(test)

    def cleanup(test):
        pass

def adjust_clock_exceptional_flow(test):
    test.log.info('*** adjust_clock_exceptional_flow begin ***')

    test.log.step('Preparation for triggering NF-02 failure')
    smart_meter_init_module_normal_flow.mc_remove_sim(test)
#    smart_meter_init_module_normal_flow.mc_deregister_network(test)
    time.sleep(3)

    test.log.step('NF-01: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong. Script stops.')
        test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-01: Check for listener mode', True)

    test.log.step('NF-02: Close, configure and restart the IP service bearer 1.')
    test.log.step('NF-03: Power down the module.')
    test.log.step('NF-04: Wait a security time about 5 seconds.')
    test.log.step('NF-05: Boot up the module via the ignition line and re-initialized module.')
    test.dut.dstl_collect_result('NF-02---NF-05', smart_meter_init_module_normal_flow.retry(test, smart_meter_init_module_normal_flow.restart_ip_service_bearer,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))
    
    test.log.step('NF-06: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong.')
        test.dut.dstl_collect_result('NF-06: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-06: Check for listener mode', True)

    test.log.step('NF-07: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-07: Close, configure and restart the IP service bearer 1.',
        test.expect(smart_meter_init_module_normal_flow.restart_ip_service_bearer(test)))

    test.log.step('Preparation for triggering NF-08 failure')
    smart_meter_init_module_normal_flow.mc_remove_sim(test)
#    smart_meter_init_module_normal_flow.mc_deregister_network(test)
    test.log.step('NF-08: start this NTP service to query the UTC info (e.g. addressing "pool.ntp.org")')
    test.log.step('NF-09: Power down the module.')
    test.log.step('NF-10: Wait a security time about 5 seconds.')
    test.log.step('NF-11: Boot up the module via the ignition line and re-initialized module.')
    test.dut.dstl_collect_result('NF-08---NF-11', smart_meter_init_module_normal_flow.retry(test, convert_utc_to_local, smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-12: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong. Script stops.')
        test.dut.dstl_collect_result('NF-12: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-12: Check for listener mode', True)

    test.log.step('NF-13: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-13: Close, configure and restart the IP service bearer 1.',
        test.expect(smart_meter_init_module_normal_flow.restart_ip_service_bearer(test)))

    test.log.step('NF-14: start this NTP service to query the UTC info (e.g. addressing "pool.ntp.org")')
    test.log.step('NF-15: Adjusts its clock with received UTC info')
    test.dut.dstl_collect_result('NF-14---NF15',test.expect(convert_utc_to_local(test)))

    test.log.step('NF-16: check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        smart_meter_init_module_normal_flow.close_listener(test)
        test.dut.dstl_collect_result('NF-16: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-16: Check for listener mode', True)

    test.dut.dstl_print_results()
    test.log.info('*** adjust_clock_exceptional_flow end ***')

    return True


def convert_utc_to_local(test):
    result = True
    # get time zone from network
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CTZU=1", ".*OK|.*0"))
    test.dut.dstl_register_to_network()
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CCLK?', ".*OK|.*0"))
    sStr = test.dut.at1.last_response
    start_index = sStr.index('+CCLK: "', 0, len(sStr)) + len('+CCLK: "')
    tz_label = sStr[start_index + 17]
    timezone = sStr[start_index + 18:start_index + 20]
    tz_to_hour = int(timezone) / 4

    # get UTC time from NTP service.
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
