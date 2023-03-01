# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0012099.003, TC0012099.004

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """Testing basic functionalities of http-service without URC """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_get_bootloader(test.dut))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: "
                      "'TC0012099.003/004 HttpBasicfunctionWithoutUrc'")
        test.http_server = HttpServer("IPv4")
        server_fqdn_address = test.http_server.dstl_get_server_FQDN()
        server_port = test.http_server.dstl_get_server_port()
        user = "TestUser_001...wahhh"
        user_incorrect = "TestUser_incorrect"
        passwd = "Passworord12312425435XXZ"
        passwdincorrect = "PassworIncorrect"
        hc_content = "HttpBasicfunctionWithoutUrc"
        test.srv_id_0 = "0"
        test.srv_id_1 = "1"
        test.srv_id_2 = "2"
        test.srv_id_3 = "3"
        con_id = test.connection_setup.dstl_get_used_cid()
        http_post_server = "http://www.httpbin.org/post"

        test.log.step('1. Set internet services polling mode: AT^SCFG="Tcp/WithURCs",off.')
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))

        test.log.step("2.1. Http get: set http service profile, use get method.")
        test.http_client_get = HttpProfile(test.dut, test.srv_id_0, con_id, http_command="get",
                                           host=server_fqdn_address, port=server_port,
                                           http_path="bytes/6666")
        test.http_client_get.dstl_generate_address()
        test.expect(test.http_client_get.dstl_get_service().dstl_load_profile())

        test.log.step("2.2. Open service and poll for read data.")
        test.open_service_check_read_urc(test.http_client_get)

        test.log.step("2.3. Read data until end of data indicated (^sisr: id, -2).")
        test.read_all_data(test.http_client_get, test.srv_id_0)

        test.log.step("2.4. Check the state of service and amount of received/send data.")
        test.check_state_data_amount_close_service(test.http_client_get, rx=6666, tx=0, step="2.5")

        test.log.step("3.1. Http head: set http service profile, use head method.")
        test.http_client_head = HttpProfile(test.dut, test.srv_id_1, con_id, http_command="head",
                                            host=server_fqdn_address, port=server_port,)
        test.http_client_head.dstl_generate_address()
        test.expect(test.http_client_head.dstl_get_service().dstl_load_profile())

        test.log.step("3.2. Open service and poll for read data.")
        test.open_service_check_read_urc(test.http_client_head)

        test.log.step("3.3. Read data until end of data indicated (^sisr: id, -2).")
        test.read_all_data(test.http_client_head, test.srv_id_1)

        test.log.step("3.4. Check the state of service and amount of received/send data.")
        test.check_state_data_amount_close_service(test.http_client_head, rx=100, tx=0, step="3.5")

        test.log.step("4.1. Http post - set service with post method (post with hcContent).")
        test.http_client_post = HttpProfile(test.dut, test.srv_id_2, con_id,
                                            address=http_post_server, http_command="post",
                                            hc_cont_len=0, hc_content=hc_content)
        test.expect(test.http_client_post.dstl_get_service().dstl_load_profile())

        test.log.step("4.2. Open service, poll for read data available and read data.")
        test.open_service_check_read_urc(test.http_client_post)
        test.read_all_data(test.http_client_post, test.srv_id_2)

        test.log.step("4.3. Check the state of service and amount of received/send data.")
        test.check_state_data_amount_close_service(test.http_client_post, rx=100,
                                                   tx=len(hc_content), step="4.4")

        test.log.step("5.1. Set service with post method (post with at^sisw).")
        test.http_client_post.dstl_set_hc_cont_len(2500)
        test.expect(test.http_client_post.dstl_get_service().dstl_write_hc_cont_len())

        test.log.step("5.2. Open service and poll for write data available.")
        test.expect(test.http_client_post.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.expect(not test.http_client_post.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("5.3. Send post data.")
        test.expect(test.http_client_post.dstl_get_service().dstl_send_sisw_command_and_data(
            1250, repetitions=2))

        test.log.step("5.4. Poll for read data available.")
        test.expect(not test.http_client_post.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("5.5. Read data until end of data indicated (^sisr: id, -2)")
        test.read_all_data(test.http_client_post, test.srv_id_2)

        test.log.step("5.6. Check the state of service and amount of received/send data.")
        test.check_state_data_amount_close_service(test.http_client_post, rx=2500, tx=2500,
                                                   step="5.7")

        test.log.step("6.1. Http authentication with correct credentials: set get service profile.")
        test.http_client_auth = HttpProfile(test.dut, test.srv_id_3, con_id, http_command="get",
                                            host=server_fqdn_address, port=server_port, alphabet=1,
                                            http_path="basic-auth/{}/{}".format(user, passwd),
                                            user=user, passwd=passwd)
        test.http_client_auth.dstl_generate_address()
        test.expect(test.http_client_auth.dstl_get_service().dstl_load_profile())

        test.log.step("6.2. Reopen http service and poll for read data available.")
        test.open_service_check_read_urc(test.http_client_auth)

        test.log.step("6.3. Read data until end of data indicated (^sisr: id, -2)")
        test.read_all_data(test.http_client_auth, test.srv_id_3)

        test.log.step("6.4. Check the state of service and amount of received/send data.")
        test.check_state_data_amount_close_service(test.http_client_auth, rx=15, tx=0, step="6.5")

        test.log.step("7.1. Http authentication with wrong credentials: use wrong password.")
        test. http_client_auth.dstl_set_passwd(passwdincorrect)
        test.expect(test.http_client_auth.dstl_get_service().dstl_write_passwd())

        test.log.step("7.2. Reopen http service.")
        test.open_service_check_read_urc(test.http_client_auth)

        test.log.step("7.3. Polling for read data available.")
        test.log.info("Checked in previous step")

        test.log.step("7.4. Check the state of service.")
        test.check_state_data_amount_close_service(test.http_client_auth, rx= 0, tx=0, step="7.5")

        test.log.step("8.1. Http authentication with wrong credentials: use wrong user name.")
        test.http_client_auth.dstl_set_user(user_incorrect)
        test.expect(test.http_client_auth.dstl_get_service().dstl_write_user())
        test.http_client_auth.dstl_set_passwd(passwd)
        test.expect(test.http_client_auth.dstl_get_service().dstl_write_passwd())

        test.log.step("8.2. Reopen http service.")
        test.open_service_check_read_urc(test.http_client_auth)

        test.log.step("8.3. Polling for read data available.")
        test.log.info("Checked in previous step")

        test.log.step("8.4. Check the state of service.")
        test.expect(test.http_client_auth.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("8.5. Close http service.")
        test.expect(test.http_client_get.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_client_get.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.http_client_head.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_client_head.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.http_client_post.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_client_post.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.http_client_auth.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_client_auth.dstl_get_service().dstl_reset_service_profile())
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def open_service_check_read_urc(test, client):
        test.expect(client.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.expect(not client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        client.dstl_get_service().dstl_read_return_data(req_read_length=0)

    def read_all_data(test, client, srv_id):
        client.dstl_get_service().dstl_read_all_data(1111, expect_urc_eod=False)
        test.expect("SISR: {},-2\r\n".format(srv_id) in test.dut.at1.last_response)

    def check_state_data_amount_close_service(test, client, rx, tx, step):
        test.expect(client.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(client.dstl_get_parser().dstl_get_socket_state() ==
                    ServiceState.ALLOCATED.value)
        test.expect(client.dstl_get_parser().dstl_get_service_data_counter("rx") >= rx)
        test.expect(client.dstl_get_parser().dstl_get_service_data_counter("tx")
                    == tx)
        test.log.step("{}. Close http service.".format(step))
        test.expect(client.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
