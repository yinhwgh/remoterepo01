#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094705.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from random import randint


class Test(BaseTest):
    """Checking HTTP service stability for IPv4 and IPv6 protocol stack."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.h2("Executing script for test case: 'TC0094705.001 HttpLoadOpenClose_IPv4_IPv6'")
        test.iterations = 100
        test.amount_of_data = 10*1024
        test.data_blocks = [512, 700, 1024, 1500]
        test.http_server = HttpServer("IPv4", test_duration=4)

        test.log.step("1) Depends on Module: set up PDP context and activate it or define Connection Profile")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.expect(test.connection_setup.dstl_activate_internet_connection(), critical=True)

        test.log.step("2) Set up two HTTP GET IPv4 services: "
                      "\n- First using IP address in address field "
                      "\n- Second using FQDN address in address field")
        http_client_1 = define_http_profile(test, 1, 'IPv4', test.http_server.dstl_get_server_ip_address())
        http_client_2 = define_http_profile(test, 2, 'IPv4', test.http_server.dstl_get_server_FQDN())

        for iteration in range(1, test.iterations+1):
            execute_steps_3_5(test, "", http_client_1, iteration)

            test.log.step("6) Repeat step 3-5. for second defined service profile."
                          "\nIteration: {} of {}".format(iteration, test.iterations))
            execute_steps_3_5(test, "6.", http_client_2, iteration)

            test.log.step("7) Close both services.\nIteration: {} of {}".format(iteration, test.iterations))
            test.expect(http_client_1.dstl_get_service().dstl_close_service_profile())
            test.expect(http_client_2.dstl_get_service().dstl_close_service_profile())

            test.log.step("8) Repeat steps 3-7. {0} times.\nIteration: {1} of {0} finished.".format(test.iterations, iteration))

        test.log.step("9) Clear all service profiles. Do not reboot the module.")
        test.expect(http_client_1.dstl_get_service().dstl_reset_service_profile())
        test.expect(http_client_2.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())
        test.expect(test.http_server.dstl_server_close_port())

        test.log.step("10) Perform steps 2-9 for IPv6 services.")
        test.http_server = HttpServer("IPv6", test_duration=4)
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv6')
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.expect(test.connection_setup.dstl_activate_internet_connection(), critical=True)

        test.log.step("10.2) Set up two HTTP GET IPv6 services: "
                      "\n- First using IP address in address field "
                      "\n- Second using FQDN address in address field")
        http_client_1 = define_http_profile(test, 1, 'IPv6', test.http_server.dstl_get_server_ip_address())
        http_client_2 = define_http_profile(test, 2, 'IPv6', test.http_server.dstl_get_server_FQDN())

        for iteration in range(1, test.iterations + 1):
            execute_steps_3_5(test, "10.", http_client_1, iteration)

            test.log.step("10.6) Repeat step 3-5. for second defined service profile."
                          "\nIteration: {} of {}".format(iteration, test.iterations))
            execute_steps_3_5(test, "10.6.", http_client_2, iteration)

            test.log.step("10.7) Close both services.\nIteration: {} of {}".format(iteration, test.iterations))
            test.expect(http_client_1.dstl_get_service().dstl_close_service_profile())
            test.expect(http_client_2.dstl_get_service().dstl_close_service_profile())

            test.log.step("10.8) Repeat steps 3-7. {0} times.\nIteration: {1} of {0} finished.".format(test.iterations, iteration))

        test.log.step("10.9) Clear all service profiles. Do not reboot the module.")
        test.expect(http_client_1.dstl_get_service().dstl_reset_service_profile())
        test.expect(http_client_2.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


def define_http_profile(test, profile_id, ip_version, host_address):
    http_client = HttpProfile(test.dut, profile_id, test.connection_setup.dstl_get_used_cid(), alphabet=1,
                              http_command="get", host=host_address, port=test.http_server.dstl_get_server_port(),
                              ip_version=ip_version, http_path="/bytes/{}".format(test.amount_of_data))
    http_client.dstl_generate_address()
    test.expect(http_client.dstl_get_service().dstl_load_profile())
    return http_client


def execute_steps_3_5(test, init_step, http_client, iteration):
    test.log.step("{}3) Open first service profile, wait for data read URC."
                  "\nIteration: {} of {}".format(init_step, iteration, test.iterations))
    test.expect(http_client.dstl_get_service().dstl_open_service_profile(expected=".*OK.*|.*ERROR.*", urc_timeout=60))
    if 'OK' not in test.dut.at1.last_response:
        test.expect(False, msg="Service cannot be opened, current iteration will be skipped.")
        return
    test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

    test.log.step("{}4) Read data using different blocksizes (e.g. 512, 700, 1024, 1500)."
                  "\nIteration: {} of {}".format(init_step, iteration, test.iterations))
    read_data(test, http_client)

    test.log.step("{}5) Check service information and verify downloaded data."
                  "\nIteration: {} of {}".format(init_step, iteration, test.iterations))
    test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
    test.expect(http_client.dstl_get_parser().dstl_get_service_data_counter("rx") == test.amount_of_data)


def read_data(test, http_profile):
    for i in range(20):
        http_profile.dstl_get_service().dstl_read_data(test.data_blocks[randint(0, 3)])
        if http_profile.dstl_get_service().dstl_get_confirmed_read_length() == -2:
            return
        elif http_profile.dstl_get_service().dstl_get_confirmed_read_length() == 0:
            test.sleep(5)


if "__main__" == __name__:
    unicorn.main()
