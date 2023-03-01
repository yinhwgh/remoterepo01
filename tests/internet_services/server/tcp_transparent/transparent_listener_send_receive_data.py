#responsible: grzegorz.dziublinski@globallogic.com
#Wroclaw
#TC0087974.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """ Check data transfer """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_detect(test.r1)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2"))

    def run(test):
        test.log.info("Executing script for test case: 'TC0087974.001 TransparentListenerSendReceiveData'")
        amount_of_data_packages = 10
        package_size = 100
        iterations = 100

        test.log.step("1. Define connection profile or PDP context depending on product.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_internet_connection_profile())
        test.expect(connection_setup_dut.dstl_activate_internet_connection(), critical=True)
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.expect(connection_setup_r1.dstl_load_internet_connection_profile())
        test.expect(connection_setup_r1.dstl_activate_internet_connection(), critical=True)

        for iteration in range(iterations+1):
            test.log.step("2. Define socket transparent listener with parameters: autoconnect=1. \n"
                          "Iteration: {} of {} - start.".format(iteration, iterations))
            test.socket_dut = SocketProfile(test.dut, '1', connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                            host="listener", localport=65000, etx_char=26, autoconnect='1')
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

            test.log.step("3. Open listener. \nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
            dut_ip_address = test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

            test.log.step("4. Client request connection to server, connection has to be automatically accepted. \n"
                          "Iteration: {} of {}".format(iteration, iterations))
            test.socket_r1 = SocketProfile(test.r1, '1', connection_setup_r1.dstl_get_used_cid(), device_interface="at2",
                                           protocol="tcp", host=dut_ip_address, port=65000, etx_char=26)
            test.socket_r1.dstl_generate_address()
            test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())

            test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "1"))
            test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode(send_command=False))
            test.expect(test.socket_r1.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("5. Server sends data while client sends data to server. \n"
                          "Iteration: {} of {}".format(iteration, iterations))
            all_data = ''
            test.dut.at1.append(True)
            for package in range(amount_of_data_packages):
                data_package = dstl_generate_data(package_size)
                all_data += data_package
                test.socket_dut.dstl_get_service().dstl_send_data(data_package, expected="")
                test.socket_r1.dstl_get_service().dstl_send_data(data_package, expected="")

            test.log.step("6. Wait 300 sec then client switches to command mode. \n"
                          "Iteration: {} of {}".format(iteration, iterations))
            test.sleep(300)
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface='at2'))
            test.expect(test.socket_r1.dstl_get_service().dstl_check_if_module_in_command_mode())

            test.log.step("7. Check RX/TX counter on client side and release the session. \n"
                          "Iteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("tx")
                        == amount_of_data_packages*package_size)
            test.expect(test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx")
                        == amount_of_data_packages*package_size)
            test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())

            test.expect(test.socket_dut.dstl_get_urc()
                        .dstl_is_sis_urc_appeared("0", "48", '"Remote peer has closed the connection"'))
            test.log.info('Checking if all data was received on DUT side.')
            test.expect(all_data in test.dut.at1.last_response)
            test.dut.at1.append(False)
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

            test.log.step("Repeat steps 2-7 100 times. Iteration: {} of {} - end.".format(iteration, iterations))

    def cleanup(test):
        try:
            if not test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode():
                dstl_switch_to_command_mode_by_etxchar(test.dut, 26)
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
            if not test.socket_r1.dstl_get_service().dstl_check_if_module_in_command_mode():
                dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface='at2')
            test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_r1.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket profile object was not created.")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))


if "__main__" == __name__:
    unicorn.main()
