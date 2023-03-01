#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093569.001, TC0093569.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile

class Test(BaseTest):
    """Testing UDP data transfer for endpoint and client services for IPv6"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer("IPv6", "UDP")

    def run(test):
        test.log.info("Executing script for test case: 'TC0093569.001/002 SocketUdpDataTransfer_IPv6'")

        test.log.step("1) Define PDP context and activate it. "
                      "If module doesn't support PDP contexts, define connection profile.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv6')
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Define service profiles:"
                      "\r\n - Non transparent UDP Endpoint.\r\n- Non transparent UDP Client.")
        test.endpoint = SocketProfile(test.dut, 1, connection_setup.dstl_get_used_cid(), protocol="udp",
                                      port=65100, ip_version='IPv6', alphabet='1')
        test.endpoint.dstl_generate_address()
        test.expect(test.endpoint.dstl_get_service().dstl_load_profile())

        test.client = SocketProfile(test.dut, 2, connection_setup.dstl_get_used_cid(), protocol="udp",
                                    ip_version='IPv6', alphabet='1')
        test.client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client.dstl_generate_address()
        test.expect(test.client.dstl_get_service().dstl_load_profile())

        test.log.step("3) Open services.")
        test.expect(test.endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sis_urc_appeared('5\r\n'))
        test.expect(test.client.dstl_get_service().dstl_open_service_profile())

        test.log.step("4) Wait for write urc.")
        test.expect(test.client.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("5) Send 10/100/33/1460 bytes from each service, each one 60 times. "
                      "Read data sent from server.")
        data_packages = [10, 100, 33, 1460]
        repetitions = 60
        test.server_address_and_port = '[{}]:{}'.format(test.echo_server.dstl_get_server_ip_address(),
                                                 test.echo_server.dstl_get_server_port())
        for data_package in data_packages:
            test.execute_data_transfer(data_package, repetitions)

        test.log.step("6) Check services information.")
        all_data_amount = (data_packages[0] + data_packages[1] + data_packages[2] + data_packages[3]) * repetitions
        test.expect(test.endpoint.dstl_get_parser().dstl_get_service_data_counter("TX") == all_data_amount)
        test.expect(test.endpoint.dstl_get_parser().dstl_get_service_data_counter("RX") >= all_data_amount * 0.8)
        test.expect(test.client.dstl_get_parser().dstl_get_service_data_counter("TX") == all_data_amount)
        test.expect(test.client.dstl_get_parser().dstl_get_service_data_counter("RX") >= all_data_amount * 0.8)

        test.log.step("7) Close services.")
        test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
        test.expect(test.client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.client.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("'SocketProfile' object was not created.")

    def execute_data_transfer(test, data_package, repetitions):
        blocks = 12
        delay = data_package / 1000
        repetitions_in_block = int(repetitions/blocks)
        for block in range(blocks):
            test.log.info('Endpoint: send data package {} bytes {} times.'.format(data_package, repetitions_in_block))
            test.endpoint.dstl_get_service().dstl_send_sisw_command_and_data_UDP_endpoint(data_package,
                                                    udp_rem_client=test.server_address_and_port,
                                                    eod_flag='0', repetitions=repetitions_in_block, delay_in_ms=delay)
            test.log.info('Endpoint: read data package {} bytes {} times.'.format(data_package, repetitions_in_block))
            test.endpoint.dstl_get_service().dstl_read_data(data_package, repetitions=repetitions_in_block)
            test.log.info('Client: send data package {} bytes {} times.'.format(data_package, repetitions_in_block))
            test.client.dstl_get_service().dstl_send_sisw_command_and_data(data_package,
                                                            repetitions=repetitions_in_block, delay_in_ms=delay)
            test.log.info('Client: read data package {} bytes {} times.'.format(data_package, repetitions_in_block))
            test.client.dstl_get_service().dstl_read_data(data_package, repetitions=repetitions_in_block)


if "__main__" == __name__:
    unicorn.main()
