#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091792.001 TC0091792.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.configuration import functionality_modes
from dstl.identification import get_identification
from dstl.identification import check_identification_ati

class AtIBasic(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")
        # Response of AT^CICRET should be validated during manual tests
        # This scripts only check if the response is same before and after pin
        test.dut.at1.send_and_verify("AT^CICRET=\"SWN\"")
        test.swn = test.dut.at1.last_response.split('\r\n')[-1]

    def run(test):
        """
            Check basic function of AtI
        """
        if hasattr(test, 'function_mode'):
            test.log.info('******** TC0091792.002 TpAtIBasic ********')
            test.log.info('******** This procedure provides during "Factory Test Mode" the '
                          'possibility of basic tests for the exec command of ATI. ********')
            test_modes = [test.function_mode]
        else:
            test.log.info('******** TC0091792.001 TpAtIBasic ********')
            test.log.info('******** This procedure provides the possibility of basic tests for '
                          'the exec command of ATI. ********')
            test_modes = [1, 5]

        for mode in test_modes:
            test.dut.dstl_lock_sim()
            test.dut.dstl_restart()
            test.sleep(5)
            test.log.step(f"1. Set module to mode {mode}")
            if mode == 5 and not test.dut.dstl_is_factory_test_mode_supported():
                test.log.info("Current product is configured as not supported FACTORY TEST MODE. "
                              "Exit tests for CFUN: 5.")
                break
            test.expect(test.dut.at1.send_and_verify(f"AT+CFUN={mode}",
                                                     expect='OK|\^SYSSTART FACTORY TEST MODE',
                                                     wait_for='OK|\^SYSSTART FACTORY TEST MODE'))
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify(f"AT+CFUN?", expect=f'\+CFUN: {mode}'))

            test.log.step(f"2. Valid parameters without pin - mode: {mode}")
            test.expect(test.dut.at1.send_and_verify("at+cpin?", ".*SIM PIN.*"))
            test.loop_ati_with_parameters(pin_locked=True)

            test.log.step(f"3. Invalid parameters without pin - mode: {mode}")
            test.expect(test.dut.at1.send_and_verify("ati=?", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati?", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati=0", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati-9876", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati=-1", ".*ERROR.*"))

            test.log.step(f"4. Software Revision without pin - mode: {mode}")
            test.expect(test.dut.at1.send_and_verify("AT^CICRET= \"SWN\"", test.swn))

            test.log.step(f"5. Valid parameters with pin - mode: {mode}")
            test.dut.dstl_enter_pin()
            test.loop_ati_with_parameters(pin_locked=False)

            test.log.step(f"6. Invalid parameters with pin - mode: {mode}")
            test.expect(test.dut.at1.send_and_verify("ati=?", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati?", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati=0", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati-9876", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("ati=-1", ".*ERROR.*"))

            test.log.step(f"7. Software Revision with pin - mode: {mode}")
            test.expect(test.dut.at1.send_and_verify("AT^CICRET= \"SWN\"", test.swn))

    def cleanup(test):
        test.expect(test.dut.dstl_set_full_functionality_mode())

    def loop_ati_with_parameters(test, pin_locked):
        test.log.info("Check all ATI commands.")

        test.log.info(' 1). Check response of command "ATI".')
        ati_main_info = test.dut.dstl_collect_ati_information_from_other_commands()
        expect_ati = "\s+{}\s+OK\s+".format(ati_main_info)
        test.expect(test.dut.at1.send_and_verify("ATI", expect_ati))

        ati_params = test.dut.dstl_get_defined_ati_parameters()
        if 'undefined' in ati_params:
            test.expect(False, msg='Ati parameters are not defined for {test.dut.project}, skip tests')
        else:
            test.log.info(f"Check response of ATI with parameters {ati_params}")
            index = 2
            for ati_param in ati_params:
                test.log.info(f' {index}). Check response of command "ATI{ati_param}".')
                if ati_param == 2:
                    test.expect(eval(f'test.dut.dstl_check_ati{ati_param}_response')(pin_locked))
                else:
                    test.expect(eval(f'test.dut.dstl_check_ati{ati_param}_response()'))
                index += 1

if "__main__" == __name__:
    unicorn.main()
