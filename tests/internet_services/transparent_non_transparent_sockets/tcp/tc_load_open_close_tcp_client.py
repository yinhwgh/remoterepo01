#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094915.001, TC0094916.001


import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """The intention is to verify the stability of IP services (TCP) during IPv4 or IPv6 connection.
    A main purpose of this test is to check a fast switching between close/open internet connection states.
    :param ip_version (String): Internet Protocol version to be used. Allowed values: 'IPv4', 'IPv6'.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer(test.ip_version, "TCP")

    def run(test):
        iterations = 500

        test.log.info("Executing script for test case: 'TcLoadOpenCloseTcpClient_{}'".format(test.ip_version))

        test.log.step("1) Set {} TCP client socket profile on module".format(test.ip_version))
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version)
        test.socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="tcp",
                                    alphabet=1, ip_version=test.ip_version)
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        test.log.step("2) Open internet connection")
        test.expect(connection_setup_object.dstl_load_internet_connection_profile())
        test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

        for iteration in range(iterations+1):
            test.log.step("3) Open connection to server (or another module, which runs as TCP listener) "
                          "and wait for write URC\nIteration: {} of {} - start.".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_open_service_profile(expected=".*OK.*|.*ERROR.*"))
            if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4) Release connection. \nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            test.sleep(2)

            if iteration != iterations:
                test.log.step("5) Repeat steps 3 and 4 {} times using {} profile. "
                              "\nIteration: {} of {} - end.".format(iterations, test.ip_version, iteration, iterations))

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
