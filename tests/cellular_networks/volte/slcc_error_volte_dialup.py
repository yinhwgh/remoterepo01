#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0094826.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.call import enable_voice_call_with_ims
from dstl.call import extended_list_of_calls
from dstl.configuration import network_registration_status
from dstl.call import switch_to_command_mode

class Test(BaseTest):
    """
    TC0094826.002 - SlccErrorVolteDialUp
    """

    def setup(test):
        test.require_parameter("dut.mux_1", "dut.mux_2")
        test.dut.at1.close()
        test.dut.at2.close()
        test.log.info("Map ports test.dut.at1 to test.dut.mux_2, test.dut.at2 to test.dut.mux_1.")
        test.dut.at1 = test.dut.mux_2
        test.dut.at2 = test.dut.mux_1
        test.dut.detect()

    def run(test):
        test.log.step('1. Start module initialization for DUT and REM')
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.dstl_enable_voice_call_with_ims(manually_register_to_lte=True))
        test.expect(test.dut.dstl_enable_slcc_urc())
        test.expect(test.dut.dstl_set_network_registration_urc(domain="PS", urc_mode='2'))

        test.log.step('2. Start mobile originated call on DUT Mux application channel - '
                      'MO call DUT to REM.')
        test.dut.at1.send(f"ATD{test.r1.sim.nat_voice_nr};")
        test.expect(test.dut.dstl_check_slcc_urc(expect_status=2))
        test.log.info("AT+CLCC may be in status 2 (dialing) or 3 (alerting).")
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(expect_status=2) or
                    test.dut.dstl_check_voice_call_status_by_clcc(expect_status=3))

        test.log.step('3. While in dialing state perform "ATD*99***1#" command on DUT Mux modem '
                      'channel to start PPP Dial-up')
        test.expect(test.dut.at2.send_and_verify("ATD*99#", "CONNECT", wait_for=".*O.*"))
        test.sleep(5)
        mux_2_response = test.dut.at2.read(append=True)
        test.expect("SLCC" not  in mux_2_response and "CLCC" not in mux_2_response)
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses(device_interface='at2'))

    def cleanup(test):
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.dstl_disable_slcc_urc())
        test.dut.at1.close()
        test.dut.at2.close()
        test.log.info("Set test.dut.at1 back to asc_0, test.dut.at2 to asc_1")
        test.dut.at1 = test.dut.asc_0
        test.dut.at2 = test.dut.asc_1


if "__main__" == __name__:
    unicorn.main()