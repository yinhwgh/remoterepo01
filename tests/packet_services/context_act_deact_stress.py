# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0010244.004,TC0010244.005

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import *
from dstl.packet_domain.ps_attach_detach import *
from dstl.packet_domain.pdp_activate_deactivate import *
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses

class Test(BaseTest):
    """
    Goal of this TC is to check whenever it is possible to continously activate and deactivate PDP contexts.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
       
    def run(test):
        test.log.step('Step 1. Activate and deactivate of PDP context; activate context, check if module is attached, deactivate context.(Repeat step 30 times)')
        if test.network == 'GPRS':
            test.expect(dstl_register_to_gsm(test.dut))
        elif test.network == 'LTE':
            test.expect(dstl_register_to_lte(test.dut))
        else:
            test.log.error('Please check config file.Only "GPRS" or "LTE" is supported')
        for i in range(1,31):
            test.log.step('loop time :'+str(i))
            dstl_ps_detach(test.dut)
            dstl_pdp_activate(test.dut,cid=1)
            dstl_verify_attachment_state(test.dut,expect_state=1)
            dstl_pdp_deactivate(test.dut,cid=1)

        test.log.step(
            'Step 2. Activate and deactivate of PDP context; by using +CGDATA command.(Repeat step 30 times)')
        for i in range(1, 31):
            test.log.step('loop time :' + str(i))
            dstl_ps_detach(test.dut)
            test.expect(test.dut.at1.send_and_verify('AT+CGDATA="PPP",1', expect=".*CONNECT.*",wait_for='.*CONNECT.*'))
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
            dstl_verify_pdp_activation_state(test.dut,cid=1,expect_state=1)
            dstl_verify_attachment_state(test.dut, expect_state=1)

        test.log.step(
            'Step 3. Activate and deactivate of PDP context; by using ATD*99.(Repeat step 30 times)')
        for i in range(1, 31):
            test.log.step('loop time :' + str(i))
            dstl_ps_detach(test.dut)
            test.expect(test.dut.at1.send_and_verify('atd*99#', expect=".*CONNECT.*",wait_for='.*CONNECT.*'))
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
            dstl_verify_pdp_activation_state(test.dut,cid=1,expect_state=1)
            dstl_verify_attachment_state(test.dut, expect_state=1)

    def cleanup(test):
        pass




if "__main__" == __name__:
    unicorn.main()
