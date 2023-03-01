#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0087908.001,TC0087908.004


import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
import re

class Test(BaseTest):
    '''
       TC0087908.001 - gprs_context_acti_deactivated
       Goal of this TC is to check whenever it is possible to continously activate and
       deactivate PDP contexts.
    '''

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.apn_v4 = test.dut.sim.apn_v4_2nd
        test.apn_v6 = test.dut.sim.apn_v6

    def run(test):
        test.log.info('Part 1. IPV4 test. Step 1: Set pdp context')
        test.config_pdp_context('ipv4')
        for i in range(100):
            test.log.info(f'Start IPV4 Loop {i+1}')
            test.step2to6_ipv4()

        test.log.info('Part 2. IPV6 test. Step 1: Set pdp context')
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=1,1,1,1", ".*OK.*"))
        test.config_pdp_context('ipv6')
        for i in range(100):
            test.log.info(f'Start IPV6 Loop {i + 1}')
            test.step2to6_ipv6()

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=0", ".*OK.*"))

    def config_pdp_context(test, ipver):
        if ipver == 'ipv4':
            test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=5,"IP","{test.apn_v4}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=5,"IPV6","{test.apn_v6}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*"))

    def check_ip_address(test, ipver):

        regex_ipv4='((25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)\\.){3,3}(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)'
        regex_ipv6 = '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'

        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=5", ".*OK.*"))
        res = test.dut.at1.last_response
        if ipver == 'ipv4':
            result = bool(re.findall(regex_ipv4, res))
        else:
            result = bool(re.findall(regex_ipv6, res))
        if result:
            test.log.info('IP address found')
        else:
            test.log.info('IP address not found')
        return result

    def step2to6_ipv4(test):
        test.log.info('Step 2: Activate PDP context')
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,5", ".*OK.*"))
        test.sleep(5)
        test.log.info('Step 3: Check is module is still attached to the network')
        test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "CGATT: 1"))
        test.log.info('Step 4: Check IP address')
        test.expect(test.check_ip_address('ipv4'))
        test.log.info('Step 5: Deactivate PDP context')
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,5", ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", "CGACT: 5,0.*OK.*"))
        test.log.info('Step 6: Check IP address (there should be no IP address)')
        test.expect(test.check_ip_address('ipv4') == False)

    def step2to6_ipv6(test):
        test.log.info('Step 2: Activate PDP context')
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,5", ".*OK.*"))
        test.sleep(5)
        test.log.info('Step 3: Check is module is still attached to the network')
        test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "CGATT: 1"))
        test.log.info('Step 4: Check IP address')
        test.expect(test.check_ip_address('ipv6'))
        test.log.info('Step 5: Deactivate PDP context')
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,5", ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", "CGACT: 5,0.*OK.*"))
        test.log.info('Step 6: Check IP address (there should be no IP address)')
        test.expect(test.check_ip_address('ipv6') == False)

if (__name__ == "__main__"):
    unicorn.main()
