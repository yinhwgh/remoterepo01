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
from dstl.call.switch_to_command_mode import *
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import smart_meter_init_module_normal_flow as init
from dstl.auxiliary.init import dstl_detect

time_to_sleep=900
ipver=''
at_expect_response_1='^0\r\n$'
at_expect_response_2='\s+0\r\n$'
class Test(BaseTest):
    def setup(test):
        test.r1.dstl_detect()
        test.r1.at1.send_and_verify(f'at+cgdcont=1,"ipv4v6",{test.r1.sim.apn_v4}')
        pass

    def run(test):
        init.set_run_all(False)
        init.uc_init_module(test, 1)
        for i in range(1, 4):
            global ipver
            if i==2:
                ipver='6'
            elif i==3:
                ipver='4'
            test.log.step('***** uc_provide_data_connection normal flow start *****')
            uc_provide_data_connection(test)
            test.log.info('NF-13 repeats the normal flow go to NF-01')
            test.log.step('*****one loop of uc_provide_data_connection normal flow end *****')

        test.log.step('*****Three loops of uc_provide_data_connection normal flow end *****')

    def cleanup(test):
        pass
def uc_provide_data_connection(test,start=1,end=12):
    for i in range(start,end+1):
        call_step(test,i)
        if init.get_reinit_flag() is True:
            break
    return True
    

def call_step(test,step_number):
    step_name='NF_'+str(step_number)
    test.log.info('Call step: '+step_name)
    eval(step_name)(test)
    return

def NF_1(test):
    test.log.step('[ProvideConnection]:NF-01 executes UC "ReadStatus"')
    smart_meter_read_status_normal_flow.uc_read_status(test)
    return
def NF_2(test):
    test.log.step('[ProvideConnection]:NF-02 close,configure and restart the IP service bearer 1')
    init.retry(test, init.restart_ip_service_bearer, init.AF_A_restart, 3)
    return
def NF_3(test):
    test.log.step(
        '[ProvideConnection]:NF-03 close and configure the IP service profile 2 as listener with port number 50001, default escape sequence, Nagle timer 200 ms and autoconnect')
    init.retry(test, NF_03_config_listener, init.AF_A_restart, 3)
    return
def NF_4(test):
    test.log.step('[ProvideConnection]:NF-04 start the listener')
    init.retry(test, NF_04_start_listener, init.AF_A_restart, 3)
    return
def NF_5(test):
    test.log.step('[ProvideConnection]:NF-05 check the listener')
    init.retry(test, NF_05_check_listener, init.AF_A_restart, 3)
    return
def NF_6(test):
    test.log.step('[ProvideConnection]:NF-06 waits for 15 minutes')
    time.sleep(time_to_sleep)
    test.expect(test.dut.at1.send_and_verify('AT^SISO=2,1', '.*SISO: 2,"Socket",4,3'))
    return
def NF_7(test):
    test.log.step(
        '[ProvideConnection]:NF-07 	server 	register to network,activate the first PDP context.')
    test.r1.dstl_register_to_lte()
    test.expect(test.r1.at1.send_and_verify('AT^SICA=1,1', "OK"))
    test.ping_execution = InternetServiceExecution(test.r1.at1, 1)
    if ipver is '6':
        test.expect(test.ping_execution.dstl_execute_ping(listener_address[0:-6], 10, 10000))
    else:
        test.expect(test.ping_execution.dstl_execute_ping(listener_address.split(':')[0], 10, 10000))
    return
def NF_8(test):
    test.log.step('[ProvideConnection]:NF-08 server establishes a TCP connection to the socket using the listener')
    test.r1.at1.send_and_verify('AT^SISC=1', ".*0.*|.*4.*|.*OK.*|.*ERROR.*", timeout=20)
    test.expect(test.r1.at1.send_and_verify('AT^SISS=1,srvtype,"socket"', "OK"))
    test.expect(test.r1.at1.send_and_verify('AT^SISS=1,conid,1', "OK"))
    test.expect(test.r1.at1.send_and_verify('AT^SISS=1,address,"socktcp://' + listener_address + ';etx"', "OK"))
    test.expect(test.r1.at1.send_and_verify('AT^SISO=1', "OK"))
    test.r1.at1.wait_for('^SISW: 1,1',60)
    test.expect(test.dut.at1.wait_for('CONNECT', 60))
    return
def NF_9(test):
    test.log.step('[ProvideConnection]:NF-09 server exchanges some data with the application 	from 50kBytes to 500kBytes')
    test.expect(test.r1.at1.send_and_verify('AT^SIST=1','CONNECT',wait_for='CONNECT'))
    data = dstl_generate_data(500)
    length=0
    for i in range(1,1025):
        test.r1.at1.send(data,end='')
        test.dut.at1.wait_for(data)
        length=length+data.__len__()
        test.log.info('The total length data sent is '+str(length))
    return
def NF_10(test):
    test.log.step('[ProvideConnection]:NF-10 server releases the connection to the socket')
    for i in(0,10):
        if test.r1.dstl_switch_to_command_mode_by_pluses():
            break
    test.r1.at1.send_and_verify('at^siso?')
    test.expect(test.r1.at1.send_and_verify('AT^SISC=1', "OK",timeout=20))
    '''
    In normal situation, after TCP client close the connection by at^sisc command, TCP listener should receive some
    "information" from network, 'NO CARRIER(Error code is 3)' URC should pop up on and DCD line become inactive.But in
    some conditions,such as poor network quality, TCP listener can not receive this "information", then URC will not
    popup, and DCD line will always be active.
    There is "three minutes" timeout for this no communication situation. If no response from client for three min then
    listener uses "+++"  to return in command mode.
    '''
    result=False
    '''
    result=True:Listener gets 'NO CARRIER(3)' URC in 3 minutes.No need to switch to command mode with "+++"
    result=False:Listener doesn't get 'NO CARRIER(3)' URC in 3 minutes.Need to switch to command mode with "+++".
    '''
    for j in range(0,18):# 18*10=180=3minutes
        time.sleep(10)
        test.dut.at1.read()
        if '3\r\n' in test.dut.at1.last_response:
            result=True
            break
    if result is False:
        test.log.warning('"3 minutes" timeout for no communication,client already close the connection,but there is no "NO CARRIER 3" on listener.')
        for i in range(0, 10):
            test.dut.at1.read()
            test.dut.at1.send(b'+++')
            if test.dut.at1.wait_for("0", timeout=20):
                dstl.log.info('TCP listener escape from data mode')
                break
        test.log.error('TCP listener switch to command mode failed.')
    return
def NF_11(test):
    test.log.step(
        '[ProvideConnection]:NF-11 checks the DCD line for an ongoing data transmission,repeat this step until the DCD line becomes inactive')
    if init.check_dcd_line(test) is True:
        test.log.error('Server has close TCP client,DCD line should be inactive.')
    return
def NF_12(test):
    test.log.step('[ProvideConnection]:NF-12 closes the listener')
    init.close_listener(test)
    return


def get_listener_address(test):
    if ipver is '6':
        
        test.expect(test.dut.at1.send_and_verify('AT+CGPIAF=1', at_expect_response_1))
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR', '\+CGPADDR: 1,.*'))
        address = '[' + re.search('\+CGPADDR: 1,".*","(.*)"', test.dut.at1.last_response).group(1) + ']:50001'
        test.expect(test.dut.at1.send_and_verify('AT+CGPIAF=0', at_expect_response_1))
    else:
        address = test.dut.at1.last_response.split(',')[6]
        address= address[1:len(address)-1]
    return address

def NF_03_config_listener(test):
    result=True
    result = result &test.expect(test.dut.at1.send_and_verify("AT^SISO?", at_expect_response_2))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=2", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    result = result &test.expect(test.dut.at1.send_and_verify('AT^SISS=2,srvType,"Socket"', at_expect_response_1))
    result = result &test.expect(test.dut.at1.send_and_verify('AT^SISS=2,conId,"1"', at_expect_response_1))
    result = result &test.expect(
        test.dut.at1.send_and_verify('AT^SISS=2,address,"socktcp://listener:50001;etx;timer=200;autoconnect=1"',
                                     at_expect_response_1))
    result = result &test.expect(test.dut.at1.send_and_verify('AT^SISS=2,tcpMR,"10"', at_expect_response_1))
    result = result &test.expect(test.dut.at1.send_and_verify('AT^SISS=2,tcpOT,"6000"', at_expect_response_1))
    if ipver is not'':
        result = result & test.expect(test.dut.at1.send_and_verify(f'AT^SISS=2,ipVer,{ipver}', at_expect_response_1))
    result = result &test.expect(test.dut.at1.send_and_verify('AT^SISO?', at_expect_response_2))

    return result

def NF_04_start_listener(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SISO=2', at_expect_response_1))

def NF_05_check_listener(test):
    result=True
    result = result &test.expect(test.dut.at1.send_and_verify('AT^SISO=2,1', '.*SISO: 2,"Socket",4,3'))
    global listener_address
    listener_address = get_listener_address(test)
    result = result &test.expect(test.dut.at1.send_and_verify('AT+CREG?', '\+CREG: 0,1'))

    return result
def set_time_to_sleep(value):
    global time_to_sleep
    time_to_sleep=value
if "__main__" == __name__:
    unicorn.main()
