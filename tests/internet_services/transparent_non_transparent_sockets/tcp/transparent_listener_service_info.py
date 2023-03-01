#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0096184.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar


class Test(BaseTest):
    """Testing states of transparent TCP service profiles and DCD line state in case many opened services
    at the same time in different service states."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_restart(test.r1))
        test.expect(dstl_register_to_network(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")

    def run(test):
        test.log.h2("Executing test script for: TC0096184.001 TransparentListenerServiceInfo")
        test.amount_of_defined_services = 9

        test.log.step("1. define and activate PDP contexts for both modules")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile()

        test.log.step("2. activate DCD line for internet service (at&c=2)")
        test.expect(test.dut.at1.send_and_verify("AT&C2"))

        test.log.step("3. dut: define {} service profiles for transparent TCP listener".format(test.amount_of_defined_services))
        test.sockets_dut = []
        for i in range(test.amount_of_defined_services):
            test.sockets_dut.append(test.define_transparent_tcp_listener(test, i))

        test.log.step("4. dut: check service states with at^sisi and DCD line state")
        for i in range(test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.ALLOCATED.value)
        test.log.info("Checking DCD line state. State should be OFF.")
        test.expect(not test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

        test.log.step("5. dut: open all profiles")
        for i in range(test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_dut[i].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        test.log.info("Checking IP address for DUT.")
        test.dut_ip_address = \
        test.sockets_dut[0].dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

        test.log.step("6. dut: check service states with at^sisi and DCD line state")
        for i in range(test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.UP.value)
        test.log.info("Checking DCD line state. State should be ON.")
        test.expect(test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

        test.log.step("7. remote: define {} service profiles for transparent TCP client".format(test.amount_of_defined_services))
        test.sockets_r1 = []
        for i in range(test.amount_of_defined_services):
            test.sockets_r1.append(test.define_transparent_tcp_client(test, i))

        test.log.step("8. remote: open all {} profiles".format(test.amount_of_defined_services))
        amount_of_accepted_clients = 0
        for i in range(test.amount_of_defined_services):
            test.expect(test.sockets_r1[i].dstl_get_service().dstl_open_service_profile())
            if test.sockets_dut[i].dstl_get_urc().dstl_is_sis_urc_appeared("3", "0", timeout=10):
                amount_of_accepted_clients += 1
        test.expect(amount_of_accepted_clients > 0, msg="None of clients was accepted.")

        test.log.step("9. dut: check service states with at^sisi and DCD line state")
        test.dut.at1.read()
        for i in range(amount_of_accepted_clients):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.ALERTING.value)
        for i in range(amount_of_accepted_clients, test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.UP.value)
        test.log.info("Checking DCD line state. State should be ON.")
        test.expect(test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

        test.log.step("10. dut: accept clients requests")
        for i in range(amount_of_accepted_clients):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_dut[i].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("11. dut: check service states with at^sisi and DCD line state")
        for i in range(amount_of_accepted_clients):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.CONNECTED.value)
        for i in range(amount_of_accepted_clients, test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.UP.value)
        test.log.info("Checking DCD line state. State should be ON.")
        test.expect(test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

        test.log.step("12. remote: close rejected service profiles. "
                      "\nIn case all were accepted, steps 12-17 should be skipped.")
        if amount_of_accepted_clients == test.amount_of_defined_services:
            test.log.info("All clients were accepted, steps 12-17 will be skipped.")
        else:
            for i in range(amount_of_accepted_clients, test.amount_of_defined_services):
                test.expect(test.sockets_r1[i].dstl_get_service().dstl_close_service_profile())

            test.log.step("13. dut: close and reset one listener service")
            test.expect(test.sockets_dut[test.amount_of_defined_services-1].dstl_get_service().dstl_close_service_profile())
            test.expect(test.sockets_dut[test.amount_of_defined_services-1].dstl_get_service().dstl_reset_service_profile())
            test.amount_of_defined_services = test.amount_of_defined_services-1

            test.log.step("14. remote: open again one recently rejected service profile")
            test.expect(test.sockets_r1[amount_of_accepted_clients].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_r1[amount_of_accepted_clients].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            test.expect(test.sockets_dut[amount_of_accepted_clients].dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))

            test.log.step("15. dut: check service states with at^sisi")
            test.dut.at1.read()
            for i in range(amount_of_accepted_clients):
                test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                            == ServiceState.CONNECTED.value)
            test.expect(test.sockets_dut[amount_of_accepted_clients].dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISI_WRITE) == ServiceState.ALERTING.value)

            test.log.step("16. dut: accept client requests")
            test.expect(test.sockets_dut[amount_of_accepted_clients].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets_dut[amount_of_accepted_clients].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            amount_of_accepted_clients += 1

            test.log.step("17. dut: check service states with at^sisi")
            for i in range(amount_of_accepted_clients):
                test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                            == ServiceState.CONNECTED.value)

        test.log.step("18. switch to transparent mode on both modules")
        test.expect(test.sockets_dut[0].dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.sockets_r1[0].dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("19. dut: check DCD line state. State should be ON.")
        test.expect(test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

        test.log.step("20. exchange data from client to server and vice versa")
        test.sockets_dut[0].dstl_get_service().dstl_send_data(dstl_generate_data(100), expected="")
        test.sockets_r1[0].dstl_get_service().dstl_send_data(dstl_generate_data(100), expected="")
        test.sleep(3)

        test.log.step("21. switch back to command mode on both modules")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface="at2"))

        test.log.step("22. remote: close all profiles")
        for i in range(amount_of_accepted_clients):
            test.expect(test.sockets_r1[i].dstl_get_service().dstl_close_service_profile())
            test.sockets_dut[i].dstl_get_urc().dstl_is_sis_urc_appeared("0")

        test.log.step("23. dut: check service states with at^sisi and DCD line state")
        test.dut.at1.read()
        for i in range(test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.UP.value)
        test.log.info("Checking DCD line state. State should be ON.")
        test.expect(test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

        test.log.step("24. dut: close all profiles, check DCD line state after each closing operation")
        for i in range(test.amount_of_defined_services-1):
            test.expect(test.sockets_dut[i].dstl_get_service().dstl_close_service_profile())
            test.log.info("Checking DCD line state. State should be ON.")
            test.expect(test.dut.at1.connection.cd, msg="Incorrect DCD line state.")
        test.expect(test.sockets_dut[test.amount_of_defined_services-1].dstl_get_service().dstl_close_service_profile())

        test.log.step("25. dut: check service states with at^sisi and DCD line state")
        for i in range(test.amount_of_defined_services):
            test.expect(test.sockets_dut[i].dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
                        == ServiceState.ALLOCATED.value)
        test.log.info("Checking DCD line state. State should be OFF.")
        test.expect(not test.dut.at1.connection.cd, msg="Incorrect DCD line state.")

    @staticmethod
    def define_transparent_tcp_listener(test, srv_id):
        socket = SocketProfile(test.dut, srv_id, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                               host="listener", localport=65100+int(srv_id), connect_timeout=180, etx_char=26)
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        return socket

    @staticmethod
    def define_transparent_tcp_client(test, srv_id):
        socket = SocketProfile(test.r1, srv_id, test.connection_setup_r1.dstl_get_used_cid(), device_interface="at2",
                               protocol="tcp", host=test.dut_ip_address, port=65100+int(srv_id), etx_char=26)
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        return socket

    def cleanup(test):
        try:
            for i in range(test.amount_of_defined_services):
                test.expect(test.sockets_dut[i].dstl_get_service().dstl_close_service_profile(expected="O"))
            for i in range(test.amount_of_defined_services):
                test.expect(test.sockets_r1[i].dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_set_scfg_urc_dst_ifc(test.r1)


if "__main__" == __name__:
    unicorn.main()
