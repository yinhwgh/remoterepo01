# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0094892.001, TC0094893.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """This test checks functionality of both directions communication
        using TCP IPV4 or IPv6 Non-Transparent connections.
        :param ip_version (String): Internet Protocol version to be used. Allowed values:
        'IPv4', 'IPv6'."""


    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.ip_version = test.ip_version
        test.echo_server1 = EchoServer(test.ip_version, 'TCP', extended=True)
        test.echo_server2 = EchoServer(test.ip_version, 'TCP', extended=True)
        test.block_size = 1000
        test.port = 65100

    def run(test):
        test.log.h2("Executing test script for: SocketNonTransparentTcp_{}".format(test.ip_version))
        test.log.info("Netcat servers will be used as Remote")

        test.log.step("1. Enable URC mode for Internet Service commands")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.log.step("2. Define PDP context and activate it (if module doesn't "
                      "support PDP context, define connection profile).")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut,
                                                                ip_version=test.ip_version,
                                                                ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. On 1st profiles set TCP Non-transparent Listener on DUT "
                      "and TCP Non-transparent Client on Remote side.")
        test.socket_listener = SocketProfile(test.dut, "0",
                                        connection_setup_dut.dstl_get_used_cid(),
                                        protocol="tcp", host="listener", localport=test.port,
                                        alphabet=1, ip_version=test.ip_version)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.log.step("4. On 2nd profiles set TCP Non-transparent Client on DUT "
                      "and TCP Non-transparent Listener on Remote side.")
        test.socket_client = SocketProfile(test.dut, "1", connection_setup_dut.dstl_get_used_cid(),
                                           protocol="tcp", alphabet=1, ip_version=test.ip_version)
        test.socket_client.dstl_set_parameters_from_ip_server(test.echo_server2)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("5. Set IpVer to {} for all profiles.".format(test.ip_version))
        test.log.info("Executed in previous steps.")

        test.log.step("6. Open Listener service profiles on both modules.")
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        dut_ip_address_and_port = test.socket_listener.dstl_get_parser()\
            .dstl_get_service_local_address_and_port(ip_version=test.ip_version)
        dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

        test.log.step("7. Open client service profiles. Accept the connections on Listeners side.")
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.echo_server1.dstl_run_ssh_nc_process(dut_ip_address, test.port)
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server = SocketProfile(test.dut,
                                test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                           connection_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_server.dstl_get_service().dstl_open_service_profile())

        test.log.step("8. Send some data from Clients to Listeners and from Listeners to Clients.")
        test.log.info("Will bo done in next step")

        test.log.step("9. Read all data on both side")
        test.log.info("Sending and reading data is checked together.")
        data = dstl_generate_data(test.block_size)
        test.echo_server1.dstl_send_data_from_ssh_server(data)
        test.read_received_data(test.socket_server, test.block_size)
        test.expect(test.socket_server.dstl_get_service().dstl_send_sisw_command_and_data(
                                                                            test.block_size))
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(
                                                                            test.block_size))
        test.read_received_data(test.socket_client, test.block_size)

        test.log.step("10. Check Rx/Tx counters on both side.")
        test.check_counters(test.socket_client)
        test.check_counters(test.socket_server)

        test.log.step("11. Close services")
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())
        test.echo_server1.dstl_stop_ssh_nc_process()
        test.echo_server2.dstl_stop_ssh_nc_process()

    def cleanup(test):
        test.log.info("Closing and deleting all profiles.")
        test.clean_echo_server(test.echo_server1)
        test.clean_echo_server(test.echo_server2)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def read_received_data(test, profile, size):
        test.expect(profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(profile.dstl_get_service().dstl_read_data(size))

    def check_counters(test, profile):
        test.expect(profile.dstl_get_parser().dstl_get_service_data_counter("RX") == 1000)
        test.expect(profile.dstl_get_parser().dstl_get_service_data_counter("TX") == 1000)

    def clean_echo_server(test, profile):
        try:
            if not profile.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            profile.dstl_stop_ssh_nc_process()
        except AttributeError:
            test.log.error("Problem with server object.")


if "__main__" == __name__:
    unicorn.main()