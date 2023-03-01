# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0011247.003

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """ Testing Socket-Tcp, setup socket connection (client and server)
    and send /receive data from client to server and vice versa """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.port = 65100
        test.block_size = 1500

    def run(test):
        test.log.info("Executing script for test case: 'TC0011247.003 SocketEodWithURC'")

        test.log.info("===== Executing Scenario: DUT = Listener + Server, RMT = Client =====")
        test.execute_test_steps(server="DUT", client="RMT")

        test.log.info("===== Executing Scenario: RMT = Listener + Server, DUT = Client =====")
        test.execute_test_steps(server="RMT", client="DUT")

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def execute_test_steps(test, server, client):
        device_server = test.dut if server == "DUT" else test.r1
        device_client = test.dut if client == "DUT" else test.r1

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Define PDP context and activate it. "
                      "If remote doesn't support PDP contexts, define connection profile.")
        connection_setup_server = dstl_get_connection_setup_object(device_server, ip_public=True)
        test.expect(connection_setup_server.dstl_load_and_activate_internet_connection_profile())
        connection_setup_client = dstl_get_connection_setup_object(device_client, ip_public=True)
        test.expect(connection_setup_client.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define service profiles: \n"
                      "- socket TCP server on the first module \n"
                      "- socket TCP client on the second module")
        test.log.info("=== Defining server service on DUT module. ===")
        test.socket_listener = SocketProfile(
            device_server, "0", connection_setup_server.dstl_get_used_cid(), protocol="tcp",
            host="listener", localport=test.port, alphabet=1, ip_version="IPv4")
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.log.info("=== Defining client service will be done during step 6 "
                      "(after opening server service). ===")

        test.log.step('4) Set URC mode to "on" with AT^SCFG command on both modules.')
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))

        test.log.step("5) Server: open the connection.")
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        server_ip = test.socket_listener.dstl_get_parser(). \
            dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        test.log.step("6) Client: open the connection.")
        test.log.info("=== Defining server service first, next open connection. ===")
        test.socket_client = SocketProfile(
            device_client, "0", connection_setup_client.dstl_get_used_cid(), protocol="tcp",
            host=server_ip, port=test.port, alphabet=1, ip_version="IPv4")
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("7) Server: accepts incoming connection.")
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server = SocketProfile(
            device_server, test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
            connection_setup_server.dstl_get_used_cid())
        test.expect(test.socket_server.dstl_get_service().dstl_open_service_profile())

        test.log.step("8) Client: send data to server until writing data isn't available "
                      "- don't read data on server!")
        test.send_data_to_server_until_full(device_client)

        test.log.step("9) Server: receive URC informing that there are data to read.")
        test.expect(test.socket_server.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("10) Client: compare txCount and ackData and unackData.")
        test.compare_tx_counter_and_ackdata_and_unackdata()

        test.log.step("11) Server: read the peak value of the internal buffer "
                      "until all data will be read.")
        test.expect(test.socket_server.dstl_get_service().
                    dstl_read_all_data(test.block_size, delay_in_ms=1000, expect_urc_eod=False))

        test.log.step("12) Server: compare rxCount with txCount on client.")
        test.compare_rx_counter_and_tx_counter()

        test.log.step("13) Client: receive URC which informs that data can be written again.")
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("14) Client: compare txCount and ackData and unackData.")
        test.compare_tx_counter_and_ackdata_and_unackdata(check_after_read=True)

        test.log.step("15) Client: send data to server until writing data isn't available "
                      "- don't read data on server!")
        test.send_data_to_server_until_full(device_client)

        test.log.step("16) Server: receive URC informing that there are data to read.")
        test.expect(test.socket_server.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("17) Client: when data can't be written nevertheless send end of data flag.")
        test.expect(test.socket_client.dstl_get_service().
                    dstl_send_sisw_command(test.block_size, eod_flag="1"))
        test.tx_counter = test.expect(test.socket_client.dstl_get_parser().
                                      dstl_get_service_data_counter("TX"))

        test.log.step("18) Server: read the peak value of the internal buffer "
                      "until all data will be read.")
        test.expect(test.socket_server.dstl_get_service().
                    dstl_read_all_data(test.block_size, delay_in_ms=1000, expect_urc_eod=False))

        test.log.step("19) Server: compare rxCount with txCount on client.")
        test.compare_rx_counter_and_tx_counter()

        test.log.step("20) Client: receive URC which informs that data can be written again.")
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("21) Client: compare txCount and ackData and unackData")
        test.compare_tx_counter_and_ackdata_and_unackdata(check_after_read=True)

        test.log.step("22) Client: send eod flag.")
        test.expect(test.socket_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.block_size, eod_flag="1"))

        test.log.step("23) Client: Try to send some data.")
        test.expect(not test.socket_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.block_size))

        test.log.step("24) Server: read the peak value of the internal buffer "
                      "until all data will be read.")
        test.expect(test.socket_server.dstl_get_service().dstl_read_data(test.block_size))

        test.log.step('25) Server: received URC: "Remote peer has closed the connection"')
        test.expect(test.socket_server.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "48", '"Remote peer has closed the connection"'))

        test.log.step("26) Server: received URC which informs that there are no data to read.")
        test.expect(test.socket_server.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("27) Server: compare rxCount with txCount on client.")
        test.tx_counter = test.expect(test.socket_client.dstl_get_parser().
                                      dstl_get_service_data_counter("TX"))
        test.compare_rx_counter_and_tx_counter()

        test.log.step("28) Server: try to send some data to client.")
        test.expect(not test.socket_server.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.block_size))

        test.log.step("29) Client: check service state.")
        test.expect(test.socket_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("30) Server: check service state.")
        test.expect(test.socket_server.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("31) Client: close the connection.")
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("32) Client: check service state again.")
        test.expect(test.socket_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.ALLOCATED.value)

        test.log.step("33) Server: close all connections.")
        test.expect(test.socket_server.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())

        test.log.step("34) Server: check services states again.")
        test.expect(test.socket_server.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(test.socket_listener.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.ALLOCATED.value)

    def send_data_to_server_until_full(test, device_client):
        test.expect(test.socket_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.block_size))
        while True:
            test.expect(test.socket_client.dstl_get_service().
                        dstl_send_sisw_command(test.block_size))
            if not re.search(r".*SISW: 0,0,.*", device_client.at1.last_response):
                data_to_send = dstl_generate_data(test.block_size)
                test.expect(test.socket_client.dstl_get_service().
                            dstl_send_data(data_to_send, expected="\r\nOK\r\n"))
            else:
                test.log.info("=== Data write is no longer available - Buffer is full ===")
                break

    def compare_tx_counter_and_ackdata_and_unackdata(test, check_after_read=False):
        test.tx_counter = test.expect(test.socket_client.dstl_get_parser().
                                      dstl_get_service_data_counter("TX"))
        ack = test.expect(test.socket_client.dstl_get_parser().dstl_get_service_ack_data())
        if check_after_read:
            test.expect(test.socket_client.dstl_get_parser().dstl_get_service_unack_data() == 0)
            test.log.info(f"=== Value of unackData: 0 ===\n"
                          f"=== Check if txCounter: {test.tx_counter} == ackData: {ack} ===")
            test.expect(test.tx_counter == ack)
        else:
            unack = test.expect(test.socket_client.dstl_get_parser().dstl_get_service_unack_data())
            test.log.info(f"=== Check if txCounter: {test.tx_counter} == "
                          f"ackData: {ack} + unackData: {unack} ===")
            test.expect(test.tx_counter == (ack + unack))

    def compare_rx_counter_and_tx_counter(test):
        rx_counter = test.expect(test.socket_server.dstl_get_parser().
                                 dstl_get_service_data_counter("RX"))
        test.log.info(f"=== Check if rxCount: {rx_counter} == txCount: {test.tx_counter} ===")
        test.expect(rx_counter == test.tx_counter)


if "__main__" == __name__:
    unicorn.main()