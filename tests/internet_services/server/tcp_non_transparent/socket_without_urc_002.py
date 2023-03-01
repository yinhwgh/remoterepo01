#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0012078.002, TC0012078.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Testing Socket-Tcp, setup socket connection (client and server)
        and send /receive data from client to server. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)

    def run(test):
        test.log.h2("Executing test script for TC0012078.002/003 SocketWithoutUrc")

        test.log.step("1) Define PDP context/connection profile and activate it if applicable.")
        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_and_activate_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Set URC mode to 'off' with AT^SCFG command on both modules.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "off"))

        test.log.step("3) Define services - non transparent TCP listener and client.")
        srv_id = '1'
        test.socket_listener = SocketProfile(test.dut, srv_id, conn_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                             host="listener", localport=8888)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.check_no_urc("SIS: {},5".format(srv_id))
        listener_parser = test.socket_listener.dstl_get_parser()
        dut_ip_address_and_port = listener_parser.dstl_get_service_local_address_and_port(ip_version='IPv4')

        test.socket_client = SocketProfile(test.r1, srv_id, conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                           address=dut_ip_address_and_port)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())
        client_service = test.socket_client.dstl_get_service()
        client_parser = test.socket_client.dstl_get_parser()

        test.log.step("4) Open services - firstly on listener, then on client.")
        test.log.info("Listener service has been opened in previous step.")
        test.expect(client_service.dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('1'))
        new_srv_id = test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id()

        test.socket_server = SocketProfile(test.dut, new_srv_id, conn_setup_dut.dstl_get_used_cid())
        server_service = test.socket_server.dstl_get_service()
        server_parser = test.socket_server.dstl_get_parser()
        test.expect(server_service.dstl_open_service_profile())
        test.check_no_urc("SISW: {},1".format(srv_id))

        test.log.step("5) Check if client-server is connected (check service states).")
        test.expect(server_parser.dstl_get_service_state() == ServiceState.UP.value)
        test.expect(client_parser.dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("6) Client send data to server until writing data isn't available (server should not read data).")
        client_service.dstl_send_sisw_command_and_data(1500)
        while client_service.dstl_get_confirmed_write_length() == 1500:
            client_service.dstl_send_sisw_command_and_data(1500)

        test.log.step("7) Client: compare txCount and ackData and unackData (with at^sisi and at^sisw)")
        test.check_counters_on_client(client_parser, client_service)

        test.log.step("8) Server: polling for read data available and read the peak value of the internal buffer")
        test.expect(server_parser.dstl_get_peek_value_of_data_to_read() > 0)

        test.log.step("9) Server: read data until no data in the buffer")
        test.expect(server_service.dstl_read_all_data(1500, expect_urc_eod=False))

        test.log.step("10) Server: compare rxCount with txCount on client.")
        test.compare_rx_tx_counters(server_parser, client_parser)

        test.log.step("11) Client: compare txCount and ackData and unackData (with at^sisi and at^sisw)")
        test.check_counters_on_client(client_parser, client_service)

        test.log.step("12) Client send data to server until writing data isn't available "
                      "(server should not read data)")
        client_service.dstl_send_sisw_command_and_data(1500)
        while client_service.dstl_get_confirmed_write_length() == 1500:
            client_service.dstl_send_sisw_command_and_data(1500)

        test.log.step("13) Client: when data can't be written nevertheless send end of data flag "
                      "(should not take effect)")
        test.expect(client_service.dstl_send_sisw_command(10, eod_flag='1', expected='SISW:.*OK'))

        test.log.step("14) Server: polling for read data available and read the peak value of the internal buffer")
        test.expect(server_parser.dstl_get_peek_value_of_data_to_read() > 0)

        test.log.step("15) Server: read data until no data in the buffer")
        test.expect(server_service.dstl_read_all_data(1500, expect_urc_eod=False))

        test.log.step("16) Server: compare rxCount with txCount on client.")
        test.compare_rx_tx_counters(server_parser, client_parser)

        test.log.step("17) Client: compare txCount and ackData and unackData (with at^sisi and at^sisw)")
        test.check_counters_on_client(client_parser, client_service)

        test.log.step("18) Client send some data with end of data flag")
        test.expect(client_service.dstl_send_sisw_command_and_data(1400, eod_flag='1'))

        test.log.step("19) Client: negativtest: send some data")
        test.expect(client_service.dstl_send_sisw_command(100, expected='ERROR'))

        test.log.step("20) Server: polling for read data available and read the peak value of internal buffer")
        test.expect(server_parser.dstl_get_peek_value_of_data_to_read() > 0)

        test.log.step("21) Server: read data until end of data (no URC should appear)")
        test.expect(server_service.dstl_read_data(1400))
        test.check_no_urc("SISR: {},2".format(srv_id))

        test.log.step("22) Server: compare rxCount with txCount on client")
        test.compare_rx_tx_counters(server_parser, client_parser)

        test.log.step("23) Server: use at^sise to check that remote service has closed the connection")
        test.expect(test.dut.at1.send_and_verify('AT^SISE={}'.format(new_srv_id)))
        test.expect('Remote peer has closed the connection' in test.dut.at1.last_response)

        test.log.step("24) Client: check service state, then close connection and check the service state again")
        test.expect(client_parser.dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(client_service.dstl_close_service_profile())
        test.expect(client_parser.dstl_get_service_state() == ServiceState.ALLOCATED.value)

        test.log.step("25) Server: send some data to Client (isn't possible!)")
        test.expect(client_service.dstl_send_sisw_command(100, expected='ERROR'))

        test.log.step("26) Server: check service state, then close connection and check the service state again")
        test.expect(server_parser.dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(server_service.dstl_close_service_profile())
        test.expect(server_parser.dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.expect(dstl_reset_internet_service_profiles(test.r1, force_reset=True))

    def check_no_urc(test, urc):
        test.sleep(20)
        test.dut.at1.read(append=True)
        test.expect(urc not in test.dut.at1.last_response)

    def check_counters_on_client(test, client_parser, client_service):
        client_tx_counter = client_parser.dstl_get_service_data_counter('tx', Command.SISI_WRITE)
        client_ack_data = client_parser.dstl_get_service_ack_data(Command.SISI_WRITE)
        client_unack_data = client_parser.dstl_get_service_unack_data(Command.SISI_WRITE)
        test.expect(client_tx_counter == client_ack_data + client_unack_data)
        test.expect(client_service.dstl_send_sisw_command(0))
        test.expect(client_service.dstl_get_unacknowledged_data() == client_unack_data)

    def compare_rx_tx_counters(test, server_parser, client_parser):
        server_rx_counter = server_parser.dstl_get_service_data_counter('rx', Command.SISI_WRITE)
        client_tx_counter = client_parser.dstl_get_service_data_counter('tx', Command.SISI_WRITE)
        test.expect(server_rx_counter == client_tx_counter)


if "__main__" == __name__:
    unicorn.main()
