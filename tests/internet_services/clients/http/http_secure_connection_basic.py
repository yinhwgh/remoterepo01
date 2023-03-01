#responsible marek.kocela@globallogic.com
#Wroclaw
#TC TC0103709.001
import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile


class Test(BaseTest):
    """Short description:
       Checking secure connection to HTTP server.

       Detailed description:
       1. DUT attaches to the network
       2. Define and activate PDP context / connection Profile
       3. Define HTTPs profile
       4. Open and establish HTTPs connection
       5. Check URC shows that data can be read
       6. Read all data from server
       7. Close connection"""

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):

        test.log.info("TC0103709.001 - HttpSecureConnectionBasic")
              
        test.log.step("1) DUT attaches to the network")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("2) Define and activate PDP context / connection Profile")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define HTTPs profile")
        test.http_service = HttpProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(), http_command="get",
                                        secure_connection=True, secopt="0")
        test.ssl_server = SslServer("IPv4", "http_tls", "TLS_DHE_RSA_WITH_AES_128_CBC_SHA")
        test.http_service.dstl_set_parameters_from_ip_server(test.ssl_server)
        test.http_service.dstl_generate_address()
        test.expect(test.http_service.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open and establish HTTPs connection")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)
        test.expect(test.http_service.dstl_get_service().dstl_open_service_profile())

        test.log.step("5) Check URC shows that data can be read")
        test.expect(test.http_service.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("6) Read all data from server")
        test.expect(test.http_service.dstl_get_service().dstl_read_all_data(1500, 10))

        test.log.step("7) Close connection")
        test.expect(test.http_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")

        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()