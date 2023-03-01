# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0011600.001, TC0011600.004

import unicorn
from random import randint
from core.basetest import BaseTest
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    This test checks a possibility to read data from different URLs with different block sizes.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.iterations = 400
        test.data_blocks = [512, 700, 1024, 1500]
        test.http_server = HttpServer("IPv4", test_duration=8)

        test.log.step("1. Define PDP context and activate it (if module doesn't support PDP "
                      "context, define connection profile")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Configure HTTP GET service profile.")
        test.random_data_block = test.data_blocks[randint(0, 3)]
        test.http_service = HttpProfile(test.dut, cid, connection_setup.dstl_get_used_cid(),
                                        alphabet=1, http_command="get",
                                        host=test.http_server.dstl_get_server_ip_address(),
                                        port=test.http_server.dstl_get_server_port(),
                                        ip_version="IPv4",
                                        http_path="/bytes/{}".format(test.random_data_block))
        test.http_service.dstl_generate_address()
        test.expect(test.http_service.dstl_get_service().dstl_load_profile())

        for iteration in range(1, test.iterations + 1):
            execute_steps_3_5(test, iteration)

    def cleanup(test):
        try:
            test.http_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


def execute_steps_3_5(test, iteration):
    if iteration > 1:
        test.random_data_block = test.data_blocks[randint(0, 3)]
        test.log.info("Setting block size to {} bytes".format(test.random_data_block))
        test.http_service.dstl_set_http_path("/bytes/{}".format(test.random_data_block))
        test.http_service.dstl_generate_address()
        test.expect(test.http_service.dstl_get_service().dstl_write_address())

    test.log.step("3. Open HTTP connection to URLs with different different block sizes (e.g. "
                  "512/700/1024/1500).\nIteration: {} of {}".format(iteration,
                                                                    test.iterations))
    test.expect(test.http_service.dstl_get_service().dstl_open_service_profile(expected=
                                                                               ".*OK.*|.*ERROR.*"))
    if 'OK' not in test.dut.at1.last_response:
        test.expect(False, msg="Service cannot be opened, current iteration will be skipped.")
        return

    test.log.step("4. When data is ready for reading (URC is indicated), read data until finish "
                  "reading URC "
                  "appeared."
                  "\nIteration: {} of {}".format(iteration, test.iterations))
    test.http_service.dstl_get_service().dstl_read_data(test.random_data_block)
    test.expect(test.http_service.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

    test.log.step("5. Close HTTP service. \nIteration: {} of {}".format(iteration, test.iterations))
    test.expect(test.http_service.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
