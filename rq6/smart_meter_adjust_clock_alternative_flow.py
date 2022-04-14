# responsible: shuang.linag@thalesgroup.com
# location: Beijing
# TC0105526.001 - SmartMeter_adjustClock_alternativeFlow
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
from tests.rq6 import smart_meter_init_module_normal_flow
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        adjust_clock_alternative_flow(test)

    def cleanup(test):
        pass

def adjust_clock_alternative_flow(test):
    test.log.info('*** adjust_clock_alternative_flow begin ***')

    test.log.step('Preparation for triggering NF-02: Define and open TCP listener service.')

    test.expect(test.dut.at1.send_and_verify("ATV1", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object(ip_public=True)
#    connection_setup_dut.dstl_load_and_activate_internet_connection_profile()

    socket_listener = SocketProfile(test.dut, "2", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                    host="listener", localport=65100)
    socket_listener.dstl_generate_address()
    test.expect(socket_listener.dstl_get_service().dstl_load_profile())

    test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
    test.dut.dstl_collect_result('Preparation for triggering NF-02: Define and open TCP listener service.',test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n")))
    test.sleep(2)
    test.expect(test.dut.at1.send_and_verify("ATV0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=0", "0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))

    test.log.step('NF-01: Check for listener mode')
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.dut.dstl_collect_result('NF-01: Check for listener mode', True)
        result = True
        test.log.step(
            'NF-02: Check the DCD line for an ongoing data transmission.Repeat it until the DCD line becomes inactive.')
        while (result):
            if smart_meter_init_module_normal_flow.check_dcd_line(test) is False:
                break
        test.dut.dstl_collect_result('NF-02: Check the DCD line for an ongoing data transmission.Repeat it until the DCD line becomes inactive.', True)

        test.log.step('NF-03: Close the listener')
        if smart_meter_init_module_normal_flow.close_listener(test) == False:
            test.log.error('Close the listener is failed.')
            test.dut.dstl_collect_result('NF-03: Close the listener', False)
            os._exit(1)
        test.dut.dstl_collect_result('NF-03: Close the listener', True)
    else:
        test.dut.dstl_collect_result('NF-01: Check for listener mode', False)

    test.log.step('NF-04: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-04: Close, configure and restart the IP service bearer 1.', smart_meter_init_module_normal_flow.restart_ip_service_bearer(test))

    test.log.step('NF-05: start this NTP service to query the UTC info (e.g. addressing "pool.ntp.org")')
    test.log.step('NF-06: Adjusts its clock with received UTC info')
    test.dut.dstl_collect_result('NF-05---NF-06', test.expect(convert_utc_to_local(test)))

    test.log.step('NF-07: check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-07: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-07: Check for listener mode', True)

    test.dut.dstl_print_results()
    test.log.info('*** adjust_clock_alternative_flow end ***')

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
        result = result & test.expect(
            test.dut.at1.send_and_verify('AT+CCLK="' + local_date_str + tz_label + timezone + '"', ".*OK|.*0"))
    result = result & results

    result = result & test.expect(test.dut.at1.send_and_verify("AT+CTZU=0", ".*OK|.*0"))
    return result


if "__main__" == __name__:
    unicorn.main()
