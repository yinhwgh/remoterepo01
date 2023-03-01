# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0095597.002

import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
import dstl.identification.check_identification_ati
from dstl.identification.get_identification import dstl_get_defined_ati_parameters
from dstl.network_service.register_to_network import  dstl_enter_pin
from dstl.usim.sset_mode_control import dstl_wait_for_sim_ready


class Test(BaseTest):
    """
    1. Identify module and get list of all supported ATI commands.
        (example of supported ATI<x> commands for Bobcat S2: x=1, 2, 3, 8, 51, 61, 176, 255, 281)

    2. ATI check without PIN:
    2.1. Assure SIM-PIN is not entered. (AT+CPIN?)
    2.2. Check answer for each supported command ATI<x>.

    3. ATI check with PIN:
    3.1. Enter SIM-PIN (AT+CPIN=9999)
    3.2. Check answer for each supported command ATI<x>.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_restart(test.dut)
        time.sleep(3)
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp="+CPIN: SIM PIN"))

    def run(test):
        test.log.step('1. Identify module and get list of all supported ATI commands.')
        supported_ati_prm = test.expect(dstl_get_defined_ati_parameters(test.dut))

        test.log.info('2. ATI check without PIN:')

        test.log.step('2.1. Assure SIM-PIN is not entered. (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp="+CPIN: SIM PIN"))

        test.log.step('2.2. Check answer for each supported command ATI<x>.')
        for param in supported_ati_prm:
            func = eval("dstl.identification.check_identification_ati.dstl_check_ati" + str(param)
                        + "_response")
            test.expect(func(test.dut))

        test.log.info('3. ATI check with PIN:')

        test.log.step('3.1. Enter SIM-PIN (AT+CPIN=9999)')
        test.expect(dstl_enter_pin(test.dut))

        test.log.step('3.2. Check answer for each supported command ATI<x>.')
        for param in supported_ati_prm:
            func = eval("dstl.identification.check_identification_ati.dstl_check_ati" + str(param)
                        + "_response")
            test.expect(func(test.dut))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
