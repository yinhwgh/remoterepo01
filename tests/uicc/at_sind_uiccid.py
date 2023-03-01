#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0092874.001 - TPSindUiccID

"""
Two modules are needed.
DUT is needed to configure two serial interfaces.
MC test is needed for DUT.

"""


import unicorn
import time, threading
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import *
from dstl.call import setup_voice_call
from dstl.network_service import register_to_network
from dstl.sms import sms_center_address
from dstl.sms import sms_configurations
from dstl.sms import select_sms_format
from dstl.status_control import extended_indicator_control
from dstl.auxiliary import check_urc
from dstl.status_control import sind_parameters



class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_lock_sim()
        time.sleep(2)
        test.r1.dstl_register_to_network()

    def run(test):
        test.log.info('**** TpAtSindUiccid - Start ****')
        test.log.info('**** 1. Basic check ****')
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", ".*\^SIND: iccid,0.*OK.*"))
        test.expect(test.dut.dstl_check_indicator_value("iccid", 0))
        test.expect(test.dut.dstl_enable_one_indicator("iccid"))

        test.log.info('**** 2. Plug out/in SIM card and check URC ****')
        test.dut.dstl_remove_sim()
        time.sleep(2)
        test.dut.dstl_insert_sim()
        test.log.info('**** Wating for "iccid" URC ****')
        test.expect(test.dut.dstl_check_urc("+CIEV: iccid,"))

        test.log.info('**** 3. Restart module and check URC ****')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"', ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_check_indicator_value("iccid", 0))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_enable_one_indicator("iccid"))

        test.log.info('**** 4. Check URC during voice call ****')
        test.dut.dstl_register_to_network()
        if test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1_sim.nat_voice_nr)):
            test.sind_set_iccid()
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", ".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", ".*OK.*"))

        test.log.info('**** 5. Check URC during FFS copy ****')

        test.log.info('**** 6. Check URC during SMS ****')
        test.log.info("**** Set SCA to BEI Testnet ****")
        test.expect(test.dut.at2.send_and_verify('AT+CMGF=1', ".*OK.*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', ".*OK.*", timeout=30))
        test.dut.dstl_set_sms_center_address(test.dut_sim.sca_int, '145')
        test.log.info("**** Set SMS storage to SIM ****")
        test.dut.dstl_set_preferred_sms_memory('SM', )
        test.log.info("**** Set reception of SMS to index-indication ****")
        test.expect(test.dut.at2.send_and_verify('AT+CNMI=2,1', ".*OK.*", timeout=30))
        t1 = threading.Thread(target = test.sms_sending)
        t2 = threading.Thread(target = test.sind_set_iccid)
        t1.start()
        t2.start()
        t1.join()

        test.log.info('**** 7. Check URC during operating phonebook ****')
        test.log.info("**** Set phonebook storage to SIM ****")
        test.expect(test.dut.at2.send_and_verify('AT+CPBS=\"SM\"', ".*OK.*", timeout=30))
        t3 = threading.Thread(target=test.phonebook_writing)
        t4 = threading.Thread(target=test.sind_set_iccid)
        t3.start()
        t4.start()
        t3.join()

        test.log.info('**** Test end ***')


    def cleanup(test):
        test.dut.dstl_unlock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))


    def sms_sending(test):
        for i in range(0, 2):
            test.expect(test.dut.at2.send_and_verify("AT+CMGS=\"{}\"".format(test.dut_sim.nat_voice_nr), ".*>.*", wait_for=".*>.*"))
            test.expect(test.dut.at2.send_and_verify("this is a test {}".format(i+1), end="\u001A", expect=".*OK.*", timeout=70))

    def phonebook_writing(test):
        for i in range(0, 5):
            test.expect(test.dut.at2.send_and_verify("AT+CPBW=1,\"123456789\",,\"test {}\"".format(i+1), ".*OK.*", timeout=30))
            test.expect(test.dut.at2.send_and_verify("AT+CPBR=1", ".*\+CPBR: 1,\"123456789\",.*,\"test {}\"".format(i+1)+".*OK.*", timeout=30))

    def sind_set_iccid(test):
        time.sleep(2)
        test.expect(test.dut.dstl_disable_one_indicator("iccid"))
        test.expect(test.dut.dstl_enable_one_indicator("iccid"))



if (__name__ == "__main__"):
    unicorn.main()
