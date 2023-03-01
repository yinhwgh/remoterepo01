# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0106033.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles

class Test(BaseTest):
    """
    Intention:
        Check http plain authentication with Internet service profile parameters and address
        parameters syntax
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_enter_pin(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


    def run(test):
        test.user = "user01"
        test.passwd = "pass987"
        test.server = HttpServer("IPv4", extended=True)

        test.log.step("1. Define PDP context for Internet services. ")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile to HTTP web page with plain authentication "
                      "(e.g. http://www.httpbin.org/basic-auth/user01/pass987).")
        test.profile = HttpProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                   alphabet=1, http_command="get",
                                   http_path="basic-auth/{}/{}".format(test.user, test.passwd))
        test.profile.dstl_set_host(test.server.dstl_get_server_ip_address())
        test.profile.dstl_set_port(test.server.dstl_get_server_port())
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        execute_step_4_14(test, "", connection_setup)

        test.log.step("15. Repeat the test steps 3-14 with username and pass set as address "
                      "parameters (e.g. http://user01:pass987@www.httpbin.org/basic-auth/"
                      "user01/pass987).")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        dstl_reset_internet_service_profiles(test.dut, profile_id="0")

        test.log.step("15.3. Define HTTP GET profile to HTTP web page with plain authentication")
        test.profile.dstl_set_concatenated_address(True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        execute_step_4_14(test, "15.", connection_setup)

    def cleanup(test):
        try:
            test.server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

        try:
            test.ssl_tcpdump_thread.join()
        except AttributeError:
            test.log.error("Problem with joining the thread.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


def execute_step_4_14(test, step_fifteen, connection_setup):
    test.log.step("{}4. Set up correct user parameter (e.g. user01).".format(step_fifteen))
    if not step_fifteen:
        test.profile.dstl_set_user(test.user)
        test.expect(test.profile.dstl_get_service().dstl_write_user())
    else:
        test.log.info("done in previous step")

    test.log.step("{}5. Set up correct password parameter (e.g. pass987).".format(step_fifteen))
    if not step_fifteen:
        test.profile.dstl_set_passwd(test.passwd)
        test.expect(test.profile.dstl_get_service().dstl_write_passwd())
    else:
        test.log.info("done in previous step")

    test.log.step("{}6. Check current settings of all Internet service profiles "
                  "(start Wireshark trace log).".format(step_fifteen))
    dstl_check_siss_read_response(test.dut, [test.profile])

    module_ip = connection_setup.dstl_get_pdp_address()
    test.ssl_tcpdump_thread = test.thread(test.server.dstl_server_execute_linux_command,
                                          "sudo timeout 30 tcpdump host {} -A -i ens3".
                                          format(module_ip[0]))

    test.log.step("{}7. Open HTTP profile.".format(step_fifteen))
    test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
    test.expect(
        test.profile.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", "\"Http connect"))

    test.log.step("{}8. Check service state.".format(step_fifteen))
    test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 4)

    test.log.step("{}9. Read all data.".format(step_fifteen))
    test.expect(test.profile.dstl_get_service().dstl_read_all_data(1500))

    test.log.step("{}10. Check service state.".format(step_fifteen))
    test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 6)

    test.log.step("{}11. Close HTTP service.".format(step_fifteen))
    test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

    test.log.step("(Steps 12 - 14 should be executed only for "
                  "Cougar product)")
    test.log.info("not a cougar")

    test.log.step("{}12. Set HTTP post profile using e.g. http://ATRACK.COM.TW:8081 and user, "
                  "passwd ATrack (if supported by server)".format(step_fifteen))
    test.log.info("not a cougar")

    test.log.step("{}13. Open profile and send declared amount of data and check if data are "
                  "sent back".format(step_fifteen))
    test.log.info("not a cougar")

    test.log.step("{}14. Stop Wireshark trace and check if any errors occured".
                  format(step_fifteen))
    test.ssl_tcpdump_thread.join()
    test.log.info("TCPDUMP RESPONSE:")
    test.log.info(test.server.linux_server_response)
    test.expect(("HTTP/1.1 401 UNAUTHORIZED" in test.server.linux_server_response))
    test.expect(("HTTP/1.1 200" in test.server.linux_server_response))
    test.expect(('"authenticated":true,"user":"user01"' in test.server.linux_server_response))


if "__main__" == __name__:
    unicorn.main()