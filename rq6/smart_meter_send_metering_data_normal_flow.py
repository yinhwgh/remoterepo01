#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105604.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import time
import datetime
import re
import random
from core.basetest import BaseTest

from dstl.network_service import register_to_network
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import Command
from tests.rq6 import smart_meter_init_module_normal_flow as init
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import smart_meter_download_configuration_file_normal_flow
from tests.rq6 import smart_meter_provide_data_connection_normal_flow

ftpes_flag=False
blocks_number=250
at_expect_response_1='^0\r\n$'
at_expect_response_2='\s+0\r\n$'
class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        init.set_run_all(False)
        init.uc_init_module(test, 1)
        init.set_listener_mode(False)
        ipv4v6='ipv4'
        for i in range(1,3):
            if i==2:
                test.ftps_server = test.ftps_server_ipv6
                ipv4v6 = 'ipv6'
            else:
                test.ftps_server = test.ftps_server_ipv4
            test.log.step(f'***** [{ipv4v6}]:uc_send_metering_data normal flow start with FTPS*****')
            uc_send_metering_data(test, ftpes=False)
            test.log.step(f'***** [{ipv4v6}]:uc_send_metering_data normal flow end*****')
            test.log.step(f'***** [{ipv4v6}]:uc_send_metering_data normal flow start with FTPES*****')
            uc_send_metering_data(test, ftpes=True)
            test.log.step(f'***** [{ipv4v6}]:uc_send_metering_data normal flow end*****')
    def cleanup(test):
        pass

def uc_send_metering_data(test,exceptional_step=0,ftpes=False,expect_dcd_active=False):
    global ftpes_flag
    try:
        test.ftps_server
    except AttributeError:
        test.ftps_server = test.ftps_server_ipv4
    ftpes_flag = ftpes
    test.log.step('[SendMeterData]:NF-01 checks for listener mode')
    if init.check_listener_mode(test):
        if init.check_dcd_line(test) is True:
            if expect_dcd_active is False:
                test.log.error('Expect DCD line is inactive here!')
            return
        else:
            if expect_dcd_active is True:
                test.log.error('Expect DCD line is active here!')
            time.sleep(5)
            init.close_listener(test)
    test.log.step('[SendMeterData]:NF-02 executes UC "ReadStatus"')
    smart_meter_read_status_normal_flow.uc_read_status(test)
    test.log.step('[SendMeterData]:NF-03 close, configure and restart the IP service bearer')
    if exceptional_step == 3:
        init.mc_remove_sim(test)
    init.retry(test,init.restart_ip_service_bearer,init.AF_A_restart,3)
    if init.get_reinit_flag() is True:
        return True
    test.log.step('[SendMeterData]:NF-04 switches on the IP URCs')
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', at_expect_response_2))
    test.log.step('[SendMeterData]:NF-05 close and configure the IP service profile 1 as FTPES or FTPS client and switch on the TLS handshake URC')
    if exceptional_step == 5:
        init.mc_deregister_network(test)
    init.retry(test,configure_open_FTPS_client,init.AF_A_restart,3)
    if init.get_reinit_flag() is True:
        return True
    test.log.step('[SendMeterData]:NF-06 starts this IP service profile,waits for the TLS handshake URC andand sends the metering data file')
    test.expect(wait_for_tls_urc(test))
    test.expect(send_metering_data(test))
    test.log.step('[SendMeterData]:NF-07 [server] receives the file and acknowledges the correct reception')
    test.expect(configure_open_FTPS_client_get(test))
    test.log.step('[SendMeterData]:NF-08 delete the locally stored metering data, if NF-07 was successful')
    test.log.step('[SendMeterData]:NF-09 switch off the IP URCs')
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","off"', at_expect_response_2))
    test.log.step('[SendMeterData]:NF-10 checks for listener mode')
    if init.check_listener_mode(test):
        test.log.step('***** uc_send_metering_data normal flow end, go to uc_provide_data_connection*****')
        smart_meter_provide_data_connection_normal_flow.set_time_to_sleep(10)
        smart_meter_provide_data_connection_normal_flow.uc_provide_data_connection(test)
    return True

def configure_open_FTPS_client(test):
    result=True
    result = result &test.expect(test.dut.at1.send_and_verify("AT^SISC=1", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object()
    ftp_con_id = connection_setup_dut.dstl_get_used_cid()
    global ftps_client
    ftps_client = FtpProfile(test.dut, srv_profile_id=1, con_id=ftp_con_id, command='put', host=test.ftps_server,
                            user=test.ftps_username_ipv4, passwd=test.ftps_password_ipv4, files='metering_data.txt',
                            secopt=1, secure_connection=True,ftpes=ftpes_flag)
    ftps_client.dstl_generate_address()
    ftps_client.dstl_get_service().dstl_load_profile()
    result = result & test.expect(test.dut.at1.send_and_verify('at^sind="is_cert",1', at_expect_response_2))
    ftps_client.dstl_get_service().dstl_open_service_profile(expected=at_expect_response_1)
    result = result &ftps_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                   '"Ftp connect {}:'.format(test.ftps_server.upper()))
    result = result &test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared(urc_cause_id=1,timeout=200))

    return result

def configure_open_FTPS_client_get(test):
    test.expect(test.dut.at1.send_and_verify("AT^SISC=3", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object()
    ftp_con_id = connection_setup_dut.dstl_get_used_cid()
    global ftps_client
    ftps_client = FtpProfile(test.dut, srv_profile_id=3, con_id=ftp_con_id, command='fget', host=test.ftps_server_ipv4,
                            user=test.ftps_username_ipv4, passwd=test.ftps_password_ipv4, files='metering_data.txt',
                            secopt=1, secure_connection=True,ftpes=ftpes_flag)
    ftps_client.dstl_generate_address()
    ftps_client.dstl_get_service().dstl_load_profile()

    ftps_client.dstl_get_service().dstl_open_service_profile(expected=at_expect_response_1)
    ftps_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                   '"Ftp connect {}:'.format(test.ftps_server_ipv4))
    test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared(urc_cause_id=2, timeout=120))
    test.expect(test.dut.at1.send_and_verify("at^siso=3,1", at_expect_response_2))
    counter_value = int(test.dut.at1.last_response.split(',')[4])
    if counter_value == 1000*blocks_number:
        return True
    else:
        return False
def wait_for_tls_urc(test):
    if re.search('\+CIEV: is_cert,1,',test.dut.at1.last_response):
        return True
    else:
        return False
def send_metering_data(test):
    for i in range(1,blocks_number):
        test.log.info('Times of write ' + str(i))
        ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(1000,timeout=0.5)
    ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(1000, eod_flag="1",timeout=0.5)
    test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared(urc_cause_id=2, timeout=60))

    test.expect(test.dut.at1.send_and_verify("at^siso?", at_expect_response_2))
    counter_value = int(re.search('\^SISO: 1,"Ftp",6,2,0,(\d+),',test.dut.at1.last_response).group(1))
    if counter_value == 1000*blocks_number:
        return True
    else:
        return False


if "__main__" == __name__:
    unicorn.main()
