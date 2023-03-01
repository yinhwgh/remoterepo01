# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0094572.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_airplane_mode
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.packet_domain.config_pdp_context import dstl_delete_pdp_context


class Test(BaseTest):
    """
    Intention:
    This procedure tests the basic function of SICA command with/without PIN code

    Description:
    1. Module starts and do not enter PIN code.
    2. Check test command at^sica=?
    3. Check read command at^sica?
    4. Activate an internet connection: At^sica=1,x
    5. Enter PIN code.
    6. Define one PDP context files using at+cgdcont.
    7. Check test command at^sica=?
    8. Check read command at^sica?
    9. Activate an internet connection: At^sica=1,x
    - Check valid value of conProfileId is 1~11.
    10. Check status using read command at^sica?
    11. Check invalid value using write and read command.
    12. Switch to airplane mode, check if at^sica command can be executed.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.sleep(5)
        test.log.info("Clearing PDP Contexts / NV Bearers")
        for i in range(2, 16):
            dstl_delete_pdp_context(test.dut, i)
        test.error_sim = "+CME ERROR: SIM PIN required"
        test.error = "+CME ERROR:"
        test.sica_command = "AT^SICA{}"

    def run(test):
        test.log.info("TC0094572.001 SICABasicFunction")
        test.log.step('1. Module starts and do not enter PIN code.')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2. Check test command at^sica=?')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=?"), test.error_sim))

        test.log.step('3. Check read command at^sica?')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("?"), test.error_sim))

        test.log.step('4. Activate an internet connection: At^sica=1,x')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=1,1"), test.error_sim))

        test.log.step('5. Enter PIN code.')
        dstl_register_to_network(test.dut)
        test.sleep(10)

        test.log.step('6. Define one PDP context files using at+cgdcont.')
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.expect(test.connection_setup.dstl_define_pdp_context())
        test.sleep(5)

        test.log.step('7. Check test command at^sica=?')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=?"),
                                                                        "^SICA: (0,1),(1-16)"))

        test.log.step('8. Check read command at^sica?')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("?"), "^SICA: 1,0"))

        test.log.step('9. Activate an internet connection: At^sica=1,x')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=1,1"), "OK"))
        for i in range(2,16):
            test.expect(test.dut.at1.send_and_verify(f'AT^SICA=1,{i}', expect=test.error))

        test.log.step('10. Check status using read command at^sica?')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("?"), "^SICA: 1,1"))

        test.log.step('11. Check invalid value using write and read command.')
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=1,17"), test.error))
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=1,0"), test.error))
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=1,100"), test.error))

        test.log.step('12. Switch to airplane mode, check if at^sica command can be executed.')
        test.expect(dstl_set_airplane_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=?"), test.error))
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("?"), test.error))
        test.expect(test.dut.at1.send_and_verify(test.sica_command.format("=1,1"), test.error))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()