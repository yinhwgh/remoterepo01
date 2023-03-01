#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105601.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import re

from core.basetest import BaseTest
from tests.rq6 import smart_meter_init_module_normal_flow as init

at_expect_response_1='^0\r\n$'
at_expect_response_2='\s+0\r\n$'
class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        init.set_run_all(False)
        init.uc_init_module(test, 1, 14)
        uc_read_status(test)

    def cleanup(test):
        pass

def uc_read_status(test,exceptional_step=0):
    test.log.step('***** uc_read_status normal flow start *****')
    test.log.step('[ReadStatus]:NF-01 query the service provider')
    test.expect(test.dut.at1.send_and_verify('at+cops?', at_expect_response_2))
    test.log.step('[ReadStatus]:NF-02 query the serving cell')
    test.expect(test.dut.at1.send_and_verify('at^smoni', at_expect_response_2))
    test.log.step('[ReadStatus]:NF-03 query the registration status')
    init.NF_13_check_registration(test)
    test.log.step('[ReadStatus]:NF-04 read the modules temperature')
    test.expect(test.dut.at1.send_and_verify("AT^SCTM?", at_expect_response_2))
    test.log.step('[ReadStatus]:NF-05 read the number of stored short messages')
    if exceptional_step==5:
        init.mc_remove_sim(test)
    init.retry(test, NF_05_read_sms, init.AF_A_restart, 1)
    if init.get_reinit_flag() is True:
        return True
    result = re.findall(r"\+CPMS: \"\w+\",(\d+),\d+", test.dut.at1.last_response)
    if result[0] is not '0':
        test.log.step('***** uc_read_status normal flow end,go to AF-A_Read messages  *****')
        AF_A_read_message(test)
    else:
        test.log.step('***** uc_read_status normal flow end *****')

def NF_05_read_sms(test):
    return test.expect(test.dut.at1.send_and_verify("AT+CPMS?", at_expect_response_2))

def AF_A_read_message(test):
    test.log.step('***** AF-A_Read messages start  *****')
    test.log.info('AF_A_01 reads the received messages')
    test.expect(test.dut.at1.send_and_verify('at+cmgl="REC UNREAD"', at_expect_response_2))
    test.log.info('AF_A_02 deletes the received messages')
    delete_messages(test)
    test.log.step('***** AF-A_Read messages end  *****')

def delete_messages(test):
    test.expect(test.dut.at1.send_and_verify('AT+CMGL="REC READ"', at_expect_response_2))
    result = re.findall('\+CMGL: (\d+),"REC READ"', test.dut.at1.last_response)
    for index in result:
        test.expect(test.dut.at1.send_and_verify('AT+CMGD='+index, at_expect_response_1))
    test.expect(test.dut.at1.send_and_verify('AT+CMGL="REC READ"', at_expect_response_1))
    result = re.findall('\+CMGL: (\d+),"REC READ"', test.dut.at1.last_response)
    if len(result) == 0:
        test.log.info('***** message has been deleted *****')
    else:
        test.log.error("delete message return error!!")


if "__main__" == __name__:
    unicorn.main()
