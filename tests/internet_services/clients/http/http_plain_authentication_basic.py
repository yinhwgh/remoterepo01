#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0094548.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_get_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Intention:
        Check http plain authentication with Internet service profile parameters and address parameters syntax

    Precondition:
        One module with SIM card is required.
        Enter PIN and attatch module to the network.
        Http server with plain authentication.
        Activate TCP/IP URCs.

    Description:
        1. Define PDP context for Internet services.
        2. Activate Internet service connection.
        3. Define HTTP GET profile to HTTP web page with plain authentication
        (e.g. http://www.httpbin.org/basic-auth/user01/pass987).
        4. Set up user parameter (e.g. user01).
        5. Set up password parameter (e.g. pass987).
        6. Check current settings of all Internet service profiles.
        7. Open HTTP profile.
        8. Check service state.
        9. Read all data.
        10. Check service state.
        11. Close HTTP service.

        A) Repeat the test steps 6-11 with wrong user parameter.
        B) Repeat the test steps 6-11 with wrong password parameter.
        C) Repeat the test steps 6-11 with username and pass set as address parameters
        (e.g. http://user01:pass987@www.httpbin.org/basic-auth/user01/pass987).
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_scfg_tcp_with_urcs(test.dut, "on")
        dstl_enter_pin(test.dut)



    def run(test):
        test.log.info("Starting TC0094548.001 HttpPlainAuthenticationBasic")
        correct_user = "new_user2"
        incorrect_user = "incorrect_user"
        correct_password = "XXXpAsswOrd!!!"
        incorrect_password = "incorrect password"

        test.log.step("1. Define PDP context for Internet services. ")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile to HTTP web page with plain authentication \n"
                      " (e.g. http://www.httpbin.org/basic-auth/user01/pass987).")
        test.server = HttpServer("IPv4")
        test.profile = HttpProfile(test.dut, "0", connection_setup.dstl_get_used_cid(), alphabet=1, http_command="get",
                              http_path="basic-auth/{}/{}".format(correct_user, correct_password))
        test.profile.dstl_set_host(test.server.dstl_get_server_ip_address())
        test.profile.dstl_set_port(test.server.dstl_get_server_port())
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("4. Set up user parameter (e.g. user01).")
        test.profile.dstl_set_user(correct_user)
        test.expect(test.profile.dstl_get_service().dstl_write_user())

        test.log.step("5. Set up password parameter (e.g. pass987).")
        test.profile.dstl_set_passwd(correct_password)
        test.expect(test.profile.dstl_get_service().dstl_write_passwd())

        test.log.info("Execution original scenario")
        test.steps_6_to_11("0", True)

        test.log.info("Scenario A - Repeat the test steps 6-11 with wrong user parameter.")
        test.profile.dstl_set_user(incorrect_user)
        test.expect(test.profile.dstl_get_service().dstl_write_user())
        test.steps_6_to_11("A", False)

        test.log.info("Scenario B - Repeat the test steps 6-11 with wrong password parameter..")
        test.profile.dstl_set_user(correct_user)
        test.expect(test.profile.dstl_get_service().dstl_write_user())
        test.profile.dstl_set_passwd(incorrect_password)
        test.expect(test.profile.dstl_get_service().dstl_write_passwd())
        test.steps_6_to_11("B", False)

        test.log.info("Scenario C - Repeat the test steps 6-11 with username and pass set as address parameters ")
        test.profile = HttpProfile(test.dut, "0", connection_setup.dstl_get_used_cid(), is_concatenated_address=True,
                        user="UserForLaststep_C", passwd="Super__Password!!!!!!laststep", alphabet=1,
                        http_path="basic-auth/UserForLaststep_C/Super__Password!!!!!!laststep", http_command="get")
        test.profile.dstl_set_host(test.server.dstl_get_server_ip_address())
        test.profile.dstl_set_port(test.server.dstl_get_server_port())
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.steps_6_to_11("C", True)

    def cleanup(test):
        try:
            test.server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

    def steps_6_to_11(test, scenario, correct_steps):
        test.log.step("6.{} Check current settings of all Internet service profiles.".format(scenario))
        test.dut.at1.send_and_verify("at^siss?", "OK", wait_for="OK")
        test.check_service(test.dut.at1.last_response)

        test.log.step("7.{} Open HTTP profile.".format(scenario))
        if correct_steps:
            test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
            test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", "\"Http connect"))
            test.expect(test.profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        else:
            test.expect(test.profile.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared("0", "200", "\".*authentication failed\""))
            test.expect(test.profile.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("8.{} Check service state.".format(scenario))
        if correct_steps:
            test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 4)
        else:
            test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 6)

        test.log.step("9.{} Read all data.".format(scenario))
        test.expect(test.profile.dstl_get_service().dstl_read_data(1500))

        test.log.step("10.{} Check service state.".format(scenario))
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 6)

        test.log.step("11.{} Close HTTP service.".format(scenario))
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

    def check_service(test, response):
        test.expect("\"srvType\",\"Http\"" in response)
        test.expect("\"address\",\"{}\"".format(test.profile._model.address) in response)
        test.expect("\"cmd\",\"get\"" in response)
        test.expect("\"conId\",\"{}\"".format(test.profile._model.con_id) in response)
        for i in range(1, 10):
            test.expect("{},\"srvType\",\"\"".format(i) in response)


if "__main__" == __name__:
    unicorn.main()
