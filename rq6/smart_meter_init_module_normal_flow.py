# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0105595.001
# Hints:
# ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import time
import re
from core.basetest import BaseTest
import dstl.auxiliary.devboard.devboard
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import smart_meter_adjust_clock_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import smart_meter_provide_data_connection_normal_flow

listener_mode=True
restart_cuunter=1
run_all = True #False for normal flow,which does not need retry.
dcd_active = False
re_init=False #if re_init is Ture,do not continue with normal flow after re-init
#stop_dcd_thread will be set to True, when need to stop checking dcd thread.
stop_dcd_thread = False

#dcd_thread_is_started will be set to Ture after check dcd line thread is starded.
#In order to avoid starting the smamee thread twice when calling check_dcd_line() function.
dcd_thread_is_started = False

at_expect_response_1='^0\r\n$'
at_expect_response_2='\s+0\r\n$'
class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        set_run_all(False)
        uc_init_module(test,1)

    def cleanup(test):
        pass


def uc_init_module(test, start_step,alternative_step=0):

    if start_step == 1:
        test.log.step('[Init]:NF-01:powers the module')
        test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK')
    if start_step <= 2:
        if start_step == 2:
            test.log.step('***** uc_init_module re-init flow start *****')
        test.log.step('[Init]:NF-02:boots up the module via the ignition line')
        test.dut.devboard.send_and_verify('MC:igt=1100', 'OK')
        time.sleep(10)
        test.log.step('[Init]:NF-03:check the AT command communication with the module ')
        test.expect(test.dut.at1.send_and_verify("AT"))

    test.log.step(
        '[Init]:NF-04:configures the AT command communication as follows: no local echo, numeric result codes, HW flow control, numeric error codes, automatic answering to calls disabled')
    retry(test,NF_04_configures,AF_A_restart,3)
    if get_reinit_flag() is True:
        return True
    test.log.step('[Init]:NF-06:collects module and SIM identity information')
    test.expect(test.dut.at1.send_and_verify("AT+CGSN", at_expect_response_2))
    test.expect(test.dut.at1.send_and_verify("AT+CGMM", at_expect_response_2))
    test.expect(test.dut.at1.send_and_verify("AT+CGMR", at_expect_response_2))
    test.expect(test.dut.at1.send_and_verify("AT+CIMI", at_expect_response_2))

    test.log.step('[Init]:NF-07:switches off the URCs for: registration, temperature, IP services')
    retry(test, NF_07_switch_off_urc, AF_A_restart, 3)
    if get_reinit_flag() is True:
        return True
    test.log.step(
        '[Init]:NF-08:configures SMS: text mode, select SIM as storage location for all messages, enable incoming message notification')
    if alternative_step==8:
        mc_remove_sim(test)
    retry(test, NF_08_config_sms, AF_A_restart, 1)
    if get_reinit_flag() is True:
        return True
    test.log.step('[Init]:NF-09:enables both PDP types IPv4 and IPv6 and configures the DNS addresses')
    retry(test, NF_09_enable_ipv4v6, AF_A_restart, 1)
    if get_reinit_flag() is True:
        return True
    test.log.step('[Init]:NF-10:enables IPv6 mapping, if a static IP address is used')
    retry(test, NF_10_enable_ipv6mapping, AF_A_restart, 1)
    if get_reinit_flag() is True:
        return True
    test.log.step('[Init]:NF-11:enables automatic registration')
    if alternative_step==11:
        mc_remove_sim(test)
    retry(test, NF_11_automatic_registration, AF_A_restart, 1 )
    if get_reinit_flag() is True:
        return True
    test.log.step('[Init]:NF-12:registers the module,the application waits for 2 minutes')
    if run_all:
        sleep_time=5
    else:
        sleep_time=120
    time.sleep(sleep_time)

    test.log.step('[Init]:NF-13:check the network registration')
    if alternative_step==13:
        mc_deregister_network(test)
    retry(test, NF_13_check_registration, AF_A_restart, 1)
    if get_reinit_flag() is True:
        return True
    test.log.step('[Init]:NF-14:executes the UC "ReadStatus"')
    if alternative_step==14:
        test.log.step('***** uc_init_module normal flow end without read status *****')
        return True
    smart_meter_read_status_normal_flow.uc_read_status(test)

    test.log.step('[Init]:NF-05:executes the UC "AdjustClock"')
    smart_meter_adjust_clock_normal_flow.uc_adjust_clock_normal_flow(test)

    test.log.step('[Init]:NF-15:checks for listener mode')
    check_listener_mode(test)
    test.log.step('[Init]:Init or re-init end')
    return True


def retry(test, fun_name, error_handling, retry_counter):
    set_reinit_flag(False)
    if run_all is False:
        return fun_name(test)
    while (retry_counter > 0):
        if fun_name(test) is True:
            return True
        else:
            retry_counter = retry_counter - 1

    test.log.step('Retry failed,start to re-init')
    test.expect(error_handling(test))
    set_reinit_flag(True)
    return False

def set_reinit_flag(value):
    global re_init
    re_init=value
    return
def get_reinit_flag():
    return re_init

def NF_04_configures(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("ATV0", 'OK\r\n$|'+at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify("ATE0", at_expect_response_1+'|'+at_expect_response_2))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify("AT\Q3", at_expect_response_1))
    return result

def NF_07_switch_off_urc(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CREG=0", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SCTM=0,1", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","off"', at_expect_response_2))

    return result

def NF_08_config_sms(test):
    result = True

    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMGF=1", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CPMS="SM","SM","SM"', at_expect_response_2))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1,0,0,1", at_expect_response_1))

    return result
def NF_09_enable_ipv4v6(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6",'+test.dut.sim.apn_v4, at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SICS=1,"dns1",' + test.dns1, at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SICS=1,"ipv6dns1",' + test.ipv6dns1, at_expect_response_1))
    return result

def NF_10_enable_ipv6mapping(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SCFG="TCP/RemappingIpv6IID","1"', at_expect_response_2))

def NF_11_automatic_registration(test):
    return test.expect(test.dut.at1.send_and_verify('AT+COPS=0', at_expect_response_1,timeout=120))

def NF_13_check_registration(test):
    result = True
    result &=test.expect(test.dut.at1.send_and_verify("AT+CREG=2", at_expect_response_1))
    result &=test.expect(test.dut.at1.send_and_verify("AT+CREG?", ".*\+CREG: 2,1,.*"))
    result &=test.expect(test.dut.at1.send_and_verify("AT+CREG=0",at_expect_response_1))

    return result

def AF_A_restart(test):
    global restart_cuunter
    test.log.info('restart_counter is {}'.format(str(restart_cuunter)))
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')

    restart_cuunter = restart_cuunter + 1
    test.log.step("[precondition] restore")
    mc_insert_sim(test)
    mc_register_network(test)
    test.log.step("*****Shut down module *****")
    test.dut.at1.send_and_verify("AT^SMSO", at_expect_response_1)
    time.sleep(5)
    
    test.log.step("*****Re-init module *****")
    test.expect(uc_init_module(test,2))

    return True


def set_listener_mode(listener_state):
    global listener_mode
    listener_mode = listener_state
    return True


def check_listener_mode(test):
    if listener_mode is True:
        test.log.info('***** check_listener_mode return True *****')
    else:
        test.log.info('***** check_listener_mode return False *****')
    return listener_mode

def set_run_all(value):
    global run_all
    run_all = value
    return True
def get_run_all():
    return run_all

def restart_ip_service_bearer(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SICA=0,1", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6",' + test.dut.sim.apn_v4, at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SGAUTH=1,0", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CGATT?", at_expect_response_2))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SICA=1,1", at_expect_response_1))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=1", at_expect_response_2))

    return result

def close_listener(test):
    stop_thread()
    test.dut.at1.send_and_verify('AT^SISC=2', at_expect_response_1)
    test.dut.at1.send_and_verify('AT^SISO=2,1', at_expect_response_1)
    if re.match('.*SISO: 2,"Socket",2,1,.*', test.dut.at1.last_response, re.DOTALL):
        test.log.info("***** Close listener successfully *****")
        return True
    else:
        test.log.info("***** Close listener unsuccessfully *****")
        return False

def check_dcd_line(test):
    global dcd_thread_is_started
    if dcd_thread_is_started is False:
        test.thread(update_dcd_flag, test)
        dcd_thread_is_started = True
    time.sleep(10)
    if dcd_active is False:
        test.log.info("***** No data transmission ongoing,check dcd line return False *****")
    else:
        test.log.info("***** Data transmission is ongoing,check dcd line return True *****")
    return dcd_active


def stop_thread():

    global stop_dcd_thread,dcd_thread_is_started
    stop_dcd_thread=True
    dcd_thread_is_started=False
    time.sleep(1)
    stop_dcd_thread = False



def update_dcd_flag(test):
    while stop_dcd_thread is False:
        test.dut.devboard.send_and_verify('MC:ASC0', 'OK')
        global dcd_active
        if re.match('.*>MC:.*DCD0: 1.*', test.dut.devboard.last_response, re.DOTALL):
            dcd_active = False
            test.log.info('DCD line is inactive')
        else:
            dcd_active = True
            test.log.info('DCD line is active')

def mc_deregister_network(test):
    test.log.step('[precondition] set:deregister from network through remove antenna   ')
    result=False;i=0
    while result is False and i<10:
        test.dut.devboard.send_and_verify('MC:ant3=off', 'OK')
        time.sleep(20)
        result=test.dut.at1.send_and_verify('at+cops?', r'\+COPS: [01]\s+0\s+')
        i=i+1
    if result is False:
        test.log.error('deregister from network failed')
    else:
        return True
    
    
def mc_register_network(test):
    test.dut.devboard.send_and_verify('MC:ant3=on', 'OK')
    return True

def mc_remove_sim(test):
    test.log.step('[precondition] set:remove sim')
    test.dut.dstl_remove_sim()
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", at_expect_response_1))
    return True

def mc_insert_sim(test):
    test.dut.dstl_insert_sim()
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", at_expect_response_1+'|'+at_expect_response_2))
    return True
    

if "__main__" == __name__:
    unicorn.main()
