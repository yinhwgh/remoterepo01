#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094680.001, TC0094680.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from time import sleep
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr, dstl_switch_to_command_mode_by_etxchar


class Test(BaseTest):
    """ This test checks the functionality of nagle timer parameter on UDP client. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.dut.at1.send_and_verify("AT&D2")
        try:
            test.dut.devboard.send_and_verify("mc:asc0=ext", "OK")
        except:
            test.log.warn("dut_devboard is not defined in configuration file")
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")

    def run(test):
        test.log.info("Executing script for test case: 'TC0094680.002 TransparentUDPClientNagleAlgorithm'")
        nagle_timers = [300, 0, 500]

        test.log.step("1. Define and activate internet connection.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define UDP endpoint on Remote.")
        test.socket_endpoint = SocketProfile(test.r1, "1", connection_setup_dut.dstl_get_used_cid(),
                                             protocol="udp", localport='9876')
        test.socket_endpoint.dstl_generate_address()
        test.expect(test.socket_endpoint.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_endpoint.dstl_get_urc().dstl_is_sis_urc_appeared("5"))
        r1_ip_address_and_port = test.socket_endpoint.dstl_get_parser() \
            .dstl_get_service_local_address_and_port('IPv4')

        for nagle_timer in nagle_timers:
            test.log.step("3. Define transparent UDP client on DUT "
                          "and set 'timer' parameter to {}ms.".format(nagle_timer))
            test.socket_client = SocketProfile(test.dut, "1", connection_setup_dut.dstl_get_used_cid(),
                                               protocol="udp", address=r1_ip_address_and_port, etx_char=26,
                                               nagle_timer=str(nagle_timer))
            test.socket_client.dstl_generate_address()
            test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

            test.log.step("4. Open services - firstly open Remote then DUT and wait for proper URC.")
            if nagle_timer == 300:
                test.log.info("Endpoint service has been already opened in step 2.")
            else:
                test.expect(test.socket_endpoint.dstl_get_service().dstl_open_service_profile())
                test.expect(test.socket_endpoint.dstl_get_urc().dstl_is_sis_urc_appeared("5"))

            test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("5. Establish transparent mode on DUT side and wait for proper URC.")
            test.expect(test.socket_client.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("6. Send 20 bytes every 100ms, until summarized time will be greater than <timer> x5. "
                          "So within 300ms you must send (3 x 20-bytes packages) x5. "
                          "(For case when <timer>=0, send 20 bytes for every 100ms until 1000ms)")
            single_package_size = 20
            data = dstl_generate_data(single_package_size)
            if nagle_timer == 300:
                packages_to_send = 15
                packages_to_read = 5
                expected_read_package_size = single_package_size * 3
            elif nagle_timer == 0:
                packages_to_send = 10
                packages_to_read = 10
                expected_read_package_size = single_package_size
            elif nagle_timer == 500:
                packages_to_send = 25
                packages_to_read = 5
                expected_read_package_size = single_package_size * 5

            for i in range(packages_to_send):
                test.dut.at1.send(data, end='')
                sleep(0.1)

            test.log.step("7. Switch to command mode by DTR.")
            test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
            if not test.expect(test.socket_client.dstl_get_service().dstl_check_if_module_in_command_mode()):
                test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, etx_char=26))

            test.log.step("8. Check the number and size of packages.")
            test.r1.at1.read()
            for package in range(packages_to_read-1):
                test.expect(test.socket_endpoint.dstl_get_service().dstl_read_data(200))
                read_package_size = test.socket_endpoint.dstl_get_service().dstl_get_confirmed_read_length()
                if nagle_timer:
                    # in case timer 300 or 500 it is possible that package is greater as it is hard to send one
                    # package exactly every 100ms; the most important to check is that packages are grouped
                    test.expect(read_package_size == expected_read_package_size or
                                read_package_size == expected_read_package_size + single_package_size)
                else:
                    test.expect(read_package_size == expected_read_package_size)
                test.sleep(2)
            # the last package size may be different, so it is not verified
            test.expect(test.socket_endpoint.dstl_get_service().dstl_read_data(200))

            test.log.step("9. Close the services.")
            test.expect(test.socket_endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

            test.log.step('Change "timer" parameter to 0ms and later 500ms on DUT. Repeat steps from 3 to 9.')

    def cleanup(test):
        try:
            test.socket_endpoint.dstl_get_service().dstl_close_service_profile()
            test.socket_endpoint.dstl_get_service().dstl_reset_service_profile()
            test.socket_client.dstl_get_service().dstl_close_service_profile()
            test.socket_client.dstl_get_service().dstl_reset_service_profile()
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
