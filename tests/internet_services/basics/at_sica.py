# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0095688.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.packet_domain.ps_attach_detach import dstl_ps_detach
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object


class Test(BaseTest):
    """
    Intention:
    Check basic AT^SICA functionality.

    Description:
    1. Detach Module from network
    2. Define two PDP contexts using AT+CGDCONT command
    3. Read current state of internet service connections using AT^SICA? command
    4. Activate 1st internet connection using SICA command (some modules may need attach first).
    5. Read current state of internet service connections using AT^SICA? command
    6. Activate 2nd internet connection using SICA command
    7. Read current state of internet service connections using AT^SICA? command
    8. Deactivate 1st internet connection using SICA command
    9. Read current state of internet service connections using AT^SICA? command
    10. Activate 1st internet connection using SICA command
    11. Deactivate 2nd internet connection using SICA command
    12. Read current state of internet service connections using AT^SICA? command
    13. Deactivate 1st internet connection using SICA command (in 4G it may not be possible)
    14. Read current state of internet service connections using AT^SICA? command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_enter_pin(test.dut)
        test.sleep(5)

    def run(test):
        test.log.info("TC0095688.001 AtSica")
        test.log.step('1. Detach Module from network')
        dstl_ps_detach(test.dut)

        test.log.step('2. Define two PDP contexts using AT+CGDCONT command')
        connection_setup_1 = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.expect(connection_setup_1.dstl_define_pdp_context())
        connection_setup_2 = dstl_get_connection_setup_object(test.dut, ip_version='IPv4',
                                                                          ip_public=True)
        connection_setup_2.cgdcont_parameters['cid'] = "2"
        test.expect(connection_setup_2.dstl_define_pdp_context())

        test.log.step('3. Read current state of internet service connections using AT^SICA? '
                      'command')
        test.expect(test.dut.at1.send_and_verify('AT^SICA?', expect="^SICA: 1,0\r\n^SICA: 2,0"))

        test.log.step('5. Activate 1st internet connection using SICA command (some modules may'
                      ' need attach first).')
        test.expect(connection_setup_1.dstl_activate_internet_connection())

        test.log.step('6. Read current state of internet service connections using AT^SICA? '
                      'command')
        test.expect(test.dut.at1.send_and_verify('AT^SICA?', expect="^SICA: 1,1\r\n^SICA: 2,0"))

        test.log.step('6. Activate 2nd internet connection using SICA command')
        test.expect(connection_setup_2.dstl_activate_internet_connection())

        test.log.step('7. Read current state of internet service connections using AT^SICA? '
                      'command')
        test.expect(test.dut.at1.send_and_verify('AT^SICA?', expect="^SICA: 1,1\r\n^SICA: 2,1"))

        test.log.step('8. Deactivate 1st internet connection using SICA command')
        test.expect(connection_setup_1.dstl_deactivate_internet_connection())

        test.log.step('9. Read current state of internet service connections using AT^SICA? '
                      'command')
        test.expect(test.dut.at1.send_and_verify('AT^SICA?', expect="^SICA: 1,0\r\n^SICA: 2,1"))

        test.log.step('10. Activate 1st internet connection using SICA command')
        test.expect(connection_setup_1.dstl_activate_internet_connection())

        test.log.step('11. Deactivate 2nd internet connection using SICA command')
        test.expect(connection_setup_2.dstl_deactivate_internet_connection())

        test.log.step('12. Read current state of internet service connections using AT^SICA? '
                      'command')
        test.expect(test.dut.at1.send_and_verify('AT^SICA?', expect="^SICA: 1,1\r\n^SICA: 2,0"))

        test.log.step('13. Deactivate 1st internet connection using SICA command (in 4G it may not '
                      'be possible)')
        test.expect(connection_setup_1.dstl_deactivate_internet_connection())

        test.log.step('14. Read current state of internet service connections using AT^SICA? '
                      'command')
        test.expect(test.dut.at1.send_and_verify('AT^SICA?', expect="^SICA: 1,0\r\n^SICA: 2,0"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()