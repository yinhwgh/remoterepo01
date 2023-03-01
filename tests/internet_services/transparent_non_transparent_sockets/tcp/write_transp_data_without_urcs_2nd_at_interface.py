#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0096361.001, TC0096362.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses, dstl_switch_to_command_mode_by_etxchar


class Test(BaseTest):
    """This test checks behavior of module during Transparent TCP Socket connection without URCs on two interface.
    Perform for IPv4 or IPv6.
    Args:
        ip_version (String): Internet Protocol version to be used. Allowed values: 'IPv4', 'IPv6'.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")

    def run(test):
        test.log.h2("Executing test script for: WriteTranspDataWithoutURCs2ndAtInterface_{}".format(test.ip_version))

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Set the URC mode for Internet Service commands to \"off\".")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off", device_interface='at2'))

        test.log.step("3) Define PDP context and activate it (if module doesn't support PDP context, define connection profile).")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2", ip_version=test.ip_version)
        test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile()

        test.log.step("4) Define TCP transparent listener on DUT. Use {}.".format(test.ip_version))
        socket_dut_1 = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                   host="listener", localport=65100, etx_char=26, alphabet=1,
                                   ip_version=test.ip_version)
        socket_dut_1.dstl_generate_address()
        test.expect(socket_dut_1.dstl_get_service().dstl_load_profile())

        test.log.step("5) Define transparent TCP client on Remote. Use {}".format(test.ip_version))
        test.log.info("Service profile on remote will be done in step 8.")

        execute_steps_6_to_20(test, socket_dut_1, 'at1', base_step="")

        test.log.step("21) Repeat steps 6-20 but use the second interface "
                      "(if products supports transparent mode on the second interface)")
        socket_dut_2 = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), device_interface='at2')
        execute_steps_6_to_20(test, socket_dut_2, 'at2', base_step="21.")

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on", device_interface='at2'))
        dstl_set_scfg_urc_dst_ifc(test.r1)


def execute_steps_6_to_20(test, socket_dut, device_interface, base_step):
    test.log.step("{}6) Open listener on DUT. Use the first interface.".format(base_step))
    test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
    check_no_urc(test, device_interface, "SIS: {},5".format(socket_dut._model.srv_profile_id))
    if base_step == "":
        dut_ip_address_and_port = socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version=test.ip_version)
        dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

    test.log.step("{}7) Check service and socket state on Listener.".format(base_step))
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value,
                msg="Incorrect socket state.")

    test.log.step("{}8) Open client on Remote.".format(base_step))
    if base_step == "":
        test.socket_r1 = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(), device_interface="at2",
                                  protocol="tcp", host=dut_ip_address, port=65100, etx_char=26,
                                  alphabet=1, ip_version=test.ip_version)
        test.socket_r1.dstl_generate_address()
        test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())

    test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())
    test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

    test.log.step("{}9) Wait for SIS URC: ^SIS: ,3,0,\"x.x.x.x\" on Listener side.".format(base_step))
    test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
    test.expect("-1" not in socket_dut.dstl_get_urc().dstl_get_sis_urc_client_ip_address())

    test.log.step("{}10) Check service state on Listener.".format(base_step))
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALERTING.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)

    test.log.step("{}11) Accept the connection and wait for OK.".format(base_step))
    test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
    check_no_urc(test, device_interface, "SISW: {},1".format(socket_dut._model.srv_profile_id))

    test.log.step("{}12) Check service and socket state on Listener.".format(base_step))
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)

    test.log.step("{}13) Establish transparent mode.".format(base_step))
    test.expect(socket_dut.dstl_get_service().dstl_enter_transparent_mode())
    test.expect(test.socket_r1.dstl_get_service().dstl_enter_transparent_mode())

    test.log.step("{}14) Send 1995 bytes from Listener to Client.".format(base_step))
    data_block_size = 399
    amount_of_data_blocks = 5
    data = dstl_generate_data(data_block_size)
    test.expect(socket_dut.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))
    test.sleep(10)

    test.log.step("{}15) Switch to command mode with \"+++\.".format(base_step))
    test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface=device_interface))
    if not test.expect(socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode()):
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26, device_interface=device_interface))
    dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface='at2')
    test.expect(test.socket_r1.dstl_get_service().dstl_check_if_module_in_command_mode())

    test.log.step("{}16) Check service state and amount data.".format(base_step))
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
    test.expect(test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)

    test.log.step("{}17) Close service on Remote side.".format(base_step))
    test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
    check_no_urc(test, device_interface, "SIS: {},0".format(socket_dut._model.srv_profile_id))

    test.log.step("{}18) Check service and socket state on Listener.".format(base_step))
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

    test.log.step("{}19) Close service on DUT side.".format(base_step))
    test.expect(socket_dut.dstl_get_service().dstl_close_service_profile())

    test.log.step("{}20) Check service and socket state on Listener.".format(base_step))
    test.expect(socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
    test.expect(socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)


def check_no_urc(test, device_interface, urc):
    test.sleep(20)
    eval("test.dut." + device_interface).read(append=True)
    test.expect(urc not in eval("test.dut." + device_interface).last_response)


if "__main__" == __name__:
    unicorn.main()
