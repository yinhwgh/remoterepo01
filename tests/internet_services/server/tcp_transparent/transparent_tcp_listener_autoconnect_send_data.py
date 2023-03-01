#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093720.001, TC0093721.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar


class Test(BaseTest):
    """This test checks beahaviour of module during transparent connection and functionally
    of the "autoconnect" parameter using IPv4 or IPv6 address.
    Args:
        ip_version (String): Internet Protocol version to be used. Allowed values: 'IPv4', 'IPv6'.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")

    def run(test):
        test.log.h2("Executing test script for: TransparentTCPListenerAutoconnectSendData_{}".format(test.ip_version))

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Depends on product: \n - Set Connection Profile (GPRS) \n - Define PDP Context")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2", ip_version=test.ip_version)
        test.connection_setup_r1.dstl_load_internet_connection_profile()

        test.log.step("3) Set service profiles: TCP transparent listener on DUT and TCP transparent client on Remote.")
        socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                   host="listener", localport=65100, etx_char=26, alphabet=1, ip_version=test.ip_version)
        socket_dut.dstl_generate_address()
        test.expect(socket_dut.dstl_get_service().dstl_load_profile())
        test.log.info("Service profile on remote will be done in step 5.")

        test.log.step("4) Depends on product: \n - Activate PDP Context.")
        test.expect(test.connection_setup_dut.dstl_activate_internet_connection())
        test.expect(test.connection_setup_r1.dstl_activate_internet_connection())

        test.log.step("5) Open services - firstly open DUT then Remote.")
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version=test.ip_version)
        dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

        socket_r1 = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(), device_interface="at2",
                                  protocol="tcp", host=dut_ip_address, port=65100, etx_char=26,
                                  alphabet=1, ip_version=test.ip_version)
        socket_r1.dstl_generate_address()
        test.expect(socket_r1.dstl_get_service().dstl_load_profile())

        test.expect(socket_r1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6) Switch to Transparent mode on both modules.")
        test.expect(socket_dut.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(socket_r1.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("7) Send 50 x 100 bytes from DUT to Remote and from Remote to DUT.")
        data_block_size = 100
        amount_of_data_blocks = 50
        data = dstl_generate_data(data_block_size)
        test.expect(socket_dut.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))
        test.expect(socket_r1.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))

        test.log.step("8) Exit from transparent mode.")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface='at2'))

        test.log.step("9) Check service information.")
        test.dut.at1.read()
        test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
        test.expect(socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)
        test.r1.at1.read()
        test.expect(socket_r1.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
        test.expect(socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)

        test.log.step("10) Close services.")
        test.expect(socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_r1.dstl_get_service().dstl_close_service_profile())

        test.log.step("11) On DUT change \"autoconnect\" to enable")
        socket_dut.dstl_set_autoconnect("1")
        socket_dut.dstl_generate_address()
        test.expect(socket_dut.dstl_get_service().dstl_write_address())

        test.log.step("12) Open services - firstly open DUT then Remote")
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.expect(socket_r1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "1"))
        test.expect(socket_dut.dstl_get_service().dstl_enter_transparent_mode(send_command=False))
        test.expect(socket_r1.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("13) Send 50 x 100 bytes from DUT to Remote and from Remote to DUT")
        test.expect(socket_dut.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))
        test.expect(socket_r1.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))

        test.log.step("14) Exit from transparent mode")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface='at2'))

        test.log.step("15) Check service information")
        test.dut.at1.read()
        test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
        test.expect(socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)
        test.r1.at1.read()
        test.expect(socket_r1.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
        test.expect(socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)

        test.log.step("16) Close services")
        test.expect(socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_r1.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        dstl_set_scfg_urc_dst_ifc(test.r1)


if "__main__" == __name__:
    unicorn.main()
