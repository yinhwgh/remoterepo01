#responsible grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0012087.003, TC0012087.004

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command


class Test(BaseTest):
    """To check states of http service profiles and DCD line behavior, without limited up state
    (tested in another testcase)."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.server_ip_address = 'httpbin.org'
        test.hc_cont_len = 100

    def run(test):
        test.log.info("Executing script for test case: 'TC0012087.003/004 "
                      "HttpConnectionServiceProfileInfo'")

        test.log.step("1) Define PDP context and activate it.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.con_id = connection_setup.dstl_get_used_cid()

        test.log.step("2) Activate DCD line for internet service (at&c2)")
        test.expect(test.dut.at1.send_and_verify('at&c2'))

        test.log.step("3) Set max number of http service profiles (usually 3 or 10 profiles "
                      "possible "
                      "- check product specification),\r\n - use get method for profile 0\r\n "
                      "- use head method for profile 1\r\n - use post method for profile 2\r\n "
                      "- use get method for profile 3\r\n - etc.")
        test.http_profiles=[]
        for srv_id in range(10):
            if srv_id % 3 == 0:
                test.http_profiles.append(test.define_http_profile(srv_id, 'get'))
            elif srv_id % 3 == 1:
                test.http_profiles.append(test.define_http_profile(srv_id, 'head'))
            else:
                test.http_profiles.append(test.define_http_profile(srv_id, 'post'))

        test.log.step("4) Check the service states with at^sisi and DCD line state")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_parser()
                        .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.ALLOCATED.value)
        test.log.info('Checking DCD line state. Expected state: OFF.')
        test.expect(not test.dut.at1.connection.cd)

        test.log.step("5) Open all profiles")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_open_service_profile())
            if srv_id % 3 == 2:
                test.expect(test.http_profiles[srv_id].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            else:
                test.expect(test.http_profiles[srv_id].dstl_get_urc().
                            dstl_is_sisr_urc_appeared("1"))

        test.log.step("6) Check the service states with at^sisi and DCD line state")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_parser()
                        .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.UP.value)
        test.log.info('Checking DCD line state. Expected state: ON.')
        test.expect(test.dut.at1.connection.cd)

        test.log.step("7) Read/write data at all profiles")
        for srv_id in range(10):
            if srv_id % 3 == 2:
                test.expect(test.http_profiles[srv_id].dstl_get_service().
                            dstl_send_sisw_command_and_data(test.hc_cont_len))
                test.sleep(5) #sleep so data can be transferred
            else:
                test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_read_all_data(1500))

        test.log.step("8) Check service states, content of http post data and DCD line state")
        for srv_id in range(10):
            if srv_id % 3 == 2:
                test.expect(test.http_profiles[srv_id].dstl_get_parser()
                            .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.UP.value)
                test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_read_all_data(1500))
                test.sleep(5)  # sleep so URC can be processed correctly
                test.expect(test.http_profiles[srv_id].dstl_get_parser()
                            .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.DOWN.value)
            else:
                test.expect(test.http_profiles[srv_id].dstl_get_parser()
                            .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.DOWN.value)
        test.log.info('Checking DCD line state. Expected state: OFF.')
        test.expect(not test.dut.at1.connection.cd)

        test.log.step("9) Close several profiles")
        for srv_id in range(0, 10, 2):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_close_service_profile())

        test.log.step("10) Check the service states with at^sisi and DCD line state")
        for srv_id in range(10):
            if srv_id % 2 == 0:
                test.expect(test.http_profiles[srv_id].dstl_get_parser()
                            .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.ALLOCATED.
                            value)
            else:
                test.expect(test.http_profiles[srv_id].dstl_get_parser()
                            .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.DOWN.
                            value)
        test.log.info('Checking DCD line state. Expected state: OFF.')
        test.expect(not test.dut.at1.connection.cd)

        test.log.step("11) Close all profiles")
        for srv_id in range(1, 10, 2):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_close_service_profile())

        test.log.step("12) Check the service states with at^sisi and DCD line state")
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_parser()
                        .dstl_get_service_state(Command.SISI_WRITE) == ServiceState.ALLOCATED.value)
        test.log.info('Checking DCD line state. Expected state: OFF.')
        test.expect(not test.dut.at1.connection.cd)

    def cleanup(test):
        for srv_id in range(10):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_close_service_profile())
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_reset_service_profile())


    def define_http_profile(test, srv_id, cmd):
        http_client = HttpProfile(test.dut, srv_id, test.con_id, http_command=cmd,
                                  host=test.server_ip_address, http_path=cmd)
        if srv_id%3 == 2:
            http_client.dstl_set_hc_cont_len(test.hc_cont_len)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        return http_client


if "__main__" == __name__:
    unicorn.main()
