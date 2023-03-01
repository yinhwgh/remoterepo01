# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107456.001
# feature: LM0007763.001
# remarks: similar to manual TCs: TC0096486.001 AtCRTDCPBasic,TC0096483.001 AtCSODCPBasic, TC0105010.001 CSODCPBasic


#!/usr/bin/env unicorn

import unicorn
import time
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_nbiot, dstl_register_to_network


class Test(BaseTest):

    def setup(test):
        """Setup method.
        Steps to be executed before test is run.
        Examples:
        """

        test.dut.dstl_detect()
        test.pin1_value = test.dut.sim.pin1
        test.apn_nonip = test.dut.sim.apn_nonip

        # test.require_parameter() does not work for SIM parameters, we chech it this way:
        if test.apn_nonip == "":
            test.expect(False, critical=True, msg='SIM parameter "APN_NonIP" is empty - abort')

        pass


    def run(test):
        test.dut.at1.send_and_verify('at+CGDCONT=3,"Non-IP",{}'.format(test.apn_nonip))
        test.dut.dstl_register_to_nbiot()       # non-ip works in Ericsson test network only on NB-IoT
        time.sleep(25)                          # after registration module needs some time - why? tested in LTE-TN in Berlin
        test.dut.at1.send_and_verify('AT+CRTDCP=1')
        time.sleep(2)
        test.dut.at1.send_and_verify('AT^SMONI')
        time.sleep(2)
        user_data_60 = '222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222'
        user_data_20 = '3333333333333333333333333333333333333333'
        user_data_40 = '44444444444444444444444444444444444444444444444444444444444444444444444444444444'

        test.expect(test.dut.at1.send_and_verify('at+csodcp=3,60,{},0,0'.format(user_data_60)))
        time.sleep(1)
        test.expect(test.dut.at1.send_and_verify('at+csodcp=3,40,{},1,0'.format(user_data_40)))
        time.sleep(1)
        test.expect(test.dut.at1.send_and_verify('at+csodcp=3,20,{},2,0'.format(user_data_20)))
        time.sleep(1)
        test.expect(test.dut.at1.send_and_verify('at+csodcp=3,60,{},0,1'.format(user_data_60)))
        time.sleep(1)
        test.expect(test.dut.at1.send_and_verify('at+csodcp=3,40,{},1,1'.format(user_data_40)))
        time.sleep(1)
        test.expect(test.dut.at1.send_and_verify('at+csodcp=3,20,{},2,1'.format(user_data_20)))
        time.sleep(1)


        time.sleep(15)
        pass


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CRTDCP=0'))
        test.dut.at1.send_and_verify('AT+COPS=2', "^.*OK.*$", timeout=35)
        test.expect(test.dut.at1.send_and_verify('at+CGDCONT=3'))
        test.expect(test.dut.at1.send_and_verify('AT+CRTDCP=0', '+CME ERROR: operation not allowed'))
        test.dut.dstl_register_to_network()
        # test.dut.at1.send_and_verify('AT+COPS=0', "^.*OK.*$", timeout=35)
        # test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[79].*', timeout=95, append=True))
        pass


if "__main__" == __name__:
    unicorn.main()
