#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0092291.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Testing UDP data transfer (client - endpoint; endpoint - client))"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.r1.at1.send_and_verify('at+cscs="GSM"')

    def run(test):
        test.log.info("Executing script for test case: 'TC0092291.001 TcSocketUdpBasicDataTransfer'")

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_enter_pin(test.r1))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Define PDP contexts on both modules and activate them.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_remote = dstl_get_connection_setup_object(test.r1)
        test.expect(connection_setup_remote.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define service profiles: \n"
                      "- on DUT: Non Transparent UDP Endpoint \n"
                      "- on Remote: Non Transparent UDP Client")
        test.endpoint = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="udp", port=65100)
        test.endpoint.dstl_generate_address()
        test.expect(test.endpoint.dstl_get_service().dstl_load_profile())
        test.log.info("Non Transparent UDP Client will be defined in next step - after opening endpoint service.")

        test.log.step("4) Firstly open service on Endpoint, then on Client.")
        test.expect(test.endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = test.endpoint.dstl_get_parser().dstl_get_service_local_address_and_port("IPv4")

        test.client = SocketProfile(test.r1, 1, connection_setup_remote.dstl_get_used_cid(), protocol="udp",
                                    address=dut_ip_address_and_port)
        test.client.dstl_generate_address()
        test.expect(test.client.dstl_get_service().dstl_load_profile())

        test.expect(test.client.dstl_get_service().dstl_open_service_profile())

        test.log.step("5) Wait for write URC on Remote.")
        test.expect(test.client.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("6) Send data from Remote to DUT: 3 x 1460bytes (4380bytes).")
        test.client.dstl_get_service().dstl_send_sisw_command_and_data(1460, repetitions=3)

        test.log.step("7) Wait for read URC on DUT. ")
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.log.info("Check if read URC appeared on DUT side only once.")
        test.expect(len(test.dut.at1.last_response.split("SISR: {},1")) == 1)

        test.log.step("8) Read 1460 bytes of data on DUT.")
        test.expect(test.endpoint.dstl_get_service().dstl_read_data(1460))
        test.expect(test.endpoint.dstl_get_service().dstl_get_confirmed_read_length() == 1460)

        test.log.step("9) Read 1500 bytes of data on DUT.")
        test.expect(test.endpoint.dstl_get_service().dstl_read_data(1500))
        test.expect(test.endpoint.dstl_get_service().dstl_get_confirmed_read_length() == 1460)

        test.log.step("10) Wait for ^SISR: x,1 URC.")
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("11) Read 1500 bytes of data on DUT.")
        test.expect(test.endpoint.dstl_get_service().dstl_read_data(1500))
        test.expect(test.endpoint.dstl_get_service().dstl_get_confirmed_read_length() == 1460)

        test.log.step("12) Try to read 5 times 1460 bytes of data.")
        for i in range(5):
            test.expect(test.endpoint.dstl_get_service().dstl_read_data(1460))
            test.expect(test.endpoint.dstl_get_service().dstl_get_confirmed_read_length() == 0)

        test.log.step("13) Check amount of received data.")
        test.expect(test.endpoint.dstl_get_parser().dstl_get_service_data_counter("RX") == 1460*3)

        test.log.step("14) Release the connections.")
        test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
        test.expect(test.client.dstl_get_service().dstl_close_service_profile())

        test.log.step("15) Repeat the test but this time DUT (Endpoint) will send data to the Remote "
                      "and remote will read them.")

        test.log.step("15.4) Firstly open service on Endpoint, then on Client.")
        test.expect(test.endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        test.expect(test.client.dstl_get_service().dstl_open_service_profile())

        test.log.step("15.5) Wait for write URC on Remote.")
        test.expect(test.client.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("15.6) Send data from DUT to remote: 3 x 1460bytes (4380bytes).")
        test.log.info("First send any data from client to get client IP address and port.")
        test.expect(test.client.dstl_get_service().dstl_send_sisw_command_and_data(3))
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.expect(test.endpoint.dstl_get_service().dstl_read_data(2))
        remote_ip_address_and_port = test.endpoint.dstl_get_service().dstl_get_udp_rem_client()
        test.expect(remote_ip_address_and_port != -1, critical=True)
        test.expect(test.endpoint.dstl_get_service().dstl_send_sisw_command_and_data_UDP_endpoint(1460,
                                                            remote_ip_address_and_port, eod_flag="0", repetitions=3))

        test.log.step("15.7) Wait for read URC on remote. ")
        test.expect(test.client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("15.8) Read 1460 bytes of data on remote.")
        test.expect(test.client.dstl_get_service().dstl_read_data(1460))
        test.expect(test.client.dstl_get_service().dstl_get_confirmed_read_length() == 1460)

        test.log.step("15.9) Read 1500 bytes of data on Remote.")
        test.expect(test.client.dstl_get_service().dstl_read_data(1500))
        test.expect(test.client.dstl_get_service().dstl_get_confirmed_read_length() == 1460)

        test.log.step("15.10) Wait for ^SISR: x,1 URC.")
        test.expect(test.client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("15.11) Read 1500 bytes of data on Remote.")
        test.expect(test.client.dstl_get_service().dstl_read_data(1500))
        test.expect(test.client.dstl_get_service().dstl_get_confirmed_read_length() == 1460)

        test.log.step("15.12) Try to read 5 times 1460 bytes of data.")
        for i in range(5):
            test.expect(test.client.dstl_get_service().dstl_read_data(1460))
            test.expect(test.client.dstl_get_service().dstl_get_confirmed_read_length() == 0)

        test.log.step("15.13) Check amount of received data.")
        test.expect(test.client.dstl_get_parser().dstl_get_service_data_counter("RX") == 1460 * 3)

        test.log.step("15.14) Release the connections.")
        test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
        test.expect(test.client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.client.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("'SocketProfile' object was not created.")


if "__main__" == __name__:
    unicorn.main()
