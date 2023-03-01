#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0087360.003

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar, dstl_switch_to_command_mode_by_pluses


class Test(BaseTest):
    """Up and download data via socket UDP transparent mode."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)

    def run(test):
        test.log.info("Executing script for test case: 'TC0087360.003 LoadUdpTransparentSendReceiveData'")
        iterations = 250

        test.log.step("1. Modules attach to network if not ready done.")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_enter_pin(test.r1))
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_internet_connection_profile())
        test.expect(connection_setup_dut.dstl_activate_internet_connection(), critical=True)
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_internet_connection_profile())
        test.expect(connection_setup_r1.dstl_activate_internet_connection(), critical=True)

        test.log.step("2. URC mode is on for internet service.")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)

        for iteration in range (1, iterations + 1):
            test.log.step("3. Establish udp transparent connection (client service) to remote module (UDP endpoint service)."
                          "\nIteration: {} of {}".format(iteration, iterations))

            if iteration == 1:
                test.endpoint = SocketProfile(test.r1, 1, connection_setup_r1.dstl_get_used_cid(), protocol="udp", port=65100)
                test.endpoint.dstl_generate_address()
                test.expect(test.endpoint.dstl_get_service().dstl_load_profile())

            test.expect(test.endpoint.dstl_get_service().dstl_open_service_profile())
            test.expect(test.endpoint.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

            if iteration == 1:
                dut_ip_address_and_port = test.endpoint.dstl_get_parser().dstl_get_service_local_address_and_port("IPv4")
                test.client = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="udp",
                                            address=dut_ip_address_and_port, etx_char=26)
                test.client.dstl_generate_address()
                test.expect(test.client.dstl_get_service().dstl_load_profile())

            test.expect(test.client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4. Switch to transparent mode on DUT.\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.client.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("5. Send data 1812 bytes from client to server.\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.client.dstl_get_service().dstl_send_data(dstl_generate_data(906), expected="", repetitions=2))
            test.expect(test.endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(test.endpoint.dstl_get_service().dstl_read_data(906))
            dut_ip_address_and_port = test.endpoint.dstl_get_service().dstl_get_udp_rem_client()
            test.expect(test.endpoint.dstl_get_service().dstl_read_data(906))

            test.log.step("6. Send data 4096 bytes to client and wait 30 sec.\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.endpoint.dstl_get_service().dstl_send_sisw_command_and_data_UDP_endpoint(1024, dut_ip_address_and_port,
                                                                                                      eod_flag="0", repetitions=4))
            test.sleep(30)

            test.log.step("7. Switch to command mode on DUT.\nIteration: {} of {}".format(iteration, iterations))
            switch_to_command_mode(test)

            test.log.step("8. Check service state and amount of data.\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
            test.expect(test.client.dstl_get_parser().dstl_get_service_data_counter("RX") >= 1024*3) # one can be lost for UDP
            test.expect(test.client.dstl_get_parser().dstl_get_service_data_counter("TX") >= 1812)

            test.log.step("9. Close the connection.\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.client.dstl_get_service().dstl_close_service_profile())

            test.log.step("10. Wait 30 sec then restart the test again {} times (estimated ~12h)."
                          "\nIteration: {} of {} finished.".format(iterations, iteration, iterations))
            test.sleep(30)

    def cleanup(test):
        try:
            test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
            if not test.expect(test.client.dstl_get_service().dstl_check_if_module_in_command_mode()):
                test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
            test.expect(test.client.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("'SocketProfile' object was not created.")


def switch_to_command_mode(test):
    if not test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26)):
        test.dut.at1.close()
        test.dut.at1.open()
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
    test.expect(test.client.dstl_get_service().dstl_check_if_module_in_command_mode(), critical=True)


if "__main__" == __name__:
    unicorn.main()
