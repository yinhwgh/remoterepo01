# responsible: tomasz.brzyk@globallogic.com
# location: Wroclaw
# TC0010973.001, TC0010973.003

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import SocketState, ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_get_siss_read_response \
    import dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """ TC intention: Testing the HTTP profiles with different parameters.
        Checking if all connections can be established at the same time, if upload/download
        data is possible after that closing the connections.

         Due to issue described in IPIS100310012, TC must be performed using an external HTTP
        server (e.g. httpbin.org) instead of IP server. Therefore, the HTTP server address has
         been hardcoded."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))


    def run(test):
        test.log.info("Executing TS for TC0010973.001/003 HttpMaxProfile")
        test.log.step("1. Setup Internet connection profile.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.con_id = test.connection_setup.dstl_get_used_cid()

        test.log.step("2. Set HTTP service on all Internet Service Profiles "
                      "(Use GET, POST and HEAD methods).")
        test.hccontent = "Data sent for TC0010973.001/003 HttpMaxProfile"
        test.http_server = "www.httpbin.org"
        test.http_profiles = []
        package_to_read = 1500
        for srv_id in range(10):
            if srv_id % 3 == 0:
                test.http_profiles.append(test.define_http_profile(srv_id, 'get'))
            elif srv_id % 3 == 1:
                test.http_profiles.append(test.define_http_profile(srv_id, 'head'))
            else:
                test.http_profiles.append(test.define_http_profile(srv_id, 'post'))
        test.expect(dstl_get_siss_read_response(test.dut))

        test.log.step("3. Open all defined profiles one by one.")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_open_service_profile())
            test.expect(test.http_profiles[srv_id].dstl_get_urc().dstl_is_sisr_urc_appeared(1))
            test.sleep(3)

        test.log.step("4. Check all received URC")
        test.log.info("Checked in the previous step")

        test.log.step("5. Check service and Internet connection profile states.")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.UP.value)
            test.expect(test.http_profiles[srv_id].dstl_get_parser().dstl_get_socket_state() ==
                        SocketState.CLIENT.value)

        test.log.step("6. On GET and HEAD profiles read all available data.")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_read_all_data
                        (package_to_read))

        test.log.step("7. On POST profiles write declared data length with EOD flag, "
                      "if EOD supported. Read data if server sends any response")
        test.log.info("Done in previous step - due the problem with quick closing POST profiles by "
                      "server data were sent during opening the service (hc content param)")

        test.log.step("8. Check service states")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.DOWN.value)
            test.expect(test.http_profiles[srv_id].dstl_get_parser().dstl_get_socket_state() ==
                        SocketState.CLIENT.value)

    def cleanup(test):
        test.log.step("9. Close all HTTP service profiles.")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_close_service_profile())
            test.expect(test.http_profiles[srv_id].dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.ALLOCATED.value)
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_reset_service_profile())

        test.log.step("10.Check service states")
        test.log.info("Done in previous step")

    def define_http_profile(test, srv_id, cmd):
        http_client = HttpProfile(test.dut, srv_id, test.con_id, http_command=cmd,
                                  host=test.http_server, http_path=cmd)
        if srv_id % 3 == 2:
            http_client.dstl_set_hc_content(test.hccontent)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        return http_client


if "__main__" == __name__:
    unicorn.main()