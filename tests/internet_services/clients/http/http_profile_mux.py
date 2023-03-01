# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0010971.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Use three HTTP profiles with multiplexer, read/write data at mux-interface simultaneous.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.dut.at1.close()
        mux_interface = 'dut_mux_1'
        test.remap({'dut_at1': mux_interface})

    def run(test):
        test.log.info("Executing TS for TC0010971.001 HttpProfileMux")
        test.log.info("TS automated for Serval product which supports AT commands on MUX1 and MUX2 "
                      "only")
        test.server = HttpServer("IPv4")
        test.server_address = test.server.dstl_get_server_FQDN()
        test.server_port = test.server.dstl_get_server_port()

        test.log.step("1. Setup Internet connection profile.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, device_interface="mux_1")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.con_id = test.connection_setup.dstl_get_used_cid()

        test.log.step('2) Set internet service URC mode: AT^SCFG="Tcp/WithURCs","on".')
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on", device_interface="mux_1"))

        test.log.step("3) On first MUX define HTTP GET.")
        test.http_profiles = []
        test.package = 1500
        redirection_path = "absolute-redirect/7"
        test.http_profiles.append(test.define_http_profile(1, 'get', "", "mux_1"))

        test.log.step("4) On second MUX define HTTP GET with redirection.")
        test.http_profiles.append(test.define_http_profile(2, 'get', redirection_path, "mux_2"))

        test.log.step("5) On third MUX define HTTP POST. (on some products only 2 MUX ports are "
                      "available for AT commands, then use second port ).")
        test.log.info("On Serval only 2 MUX ports can be used for AT Commands, so step executed"
                          " on MUX2")
        test.http_profiles.append(test.define_http_profile(3, 'post', "post", "mux_2"))

        test.log.step("6) Open all profile simultaneously.")
        thread_1 = test.thread(test.expect(test.http_profiles[0].dstl_get_service().
                                           dstl_open_service_profile))
        thread_2 = test.thread(test.expect(test.http_profiles[1].dstl_get_service().
                                           dstl_open_service_profile))
        thread_1.join()
        thread_2.join()
        test.log.info("Due to only 2 mux ports on Serval can support AT commands third service "
                      "profile is not opened simultaneously")
        test.expect(test.http_profiles[2].dstl_get_service().dstl_open_service_profile())

        test.log.step("7) In the same time read (on 1st and 2nd MUX) and write (on 3rd MUX) "
                      "some data.")
        test.log.info("Due to only 2 mux ports can support AT commands on Serval writing data "
                      "is not done simultaneously with reading")
        test.expect(test.http_profiles[2].dstl_get_service().dstl_send_sisw_command_and_data,
                    test.package)
        thread_1 = test.thread(test.http_profiles[0].dstl_get_service().dstl_read_all_data,
                               test.package)
        thread_2 = test.thread(test.http_profiles[1].dstl_get_service().dstl_read_all_data,
                               test.package)
        thread_1.join()
        thread_2.join()
        test.sleep(3)
        test.expect(test.http_profiles[0].dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(test.http_profiles[1].dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

        test.log.step("8) Close profile one after another but check the service after close "
                      "one profile.")
        for srv_id in range(0, 3):
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_close_service_profile())
            test.expect(test.http_profiles[srv_id].dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.ALLOCATED.value)
            test.expect(test.http_profiles[srv_id].dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        try:
            test.server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True,
                                                         device_interface="mux_1")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True,
                                                         device_interface="mux_2")
        test.dut.mux_1.close()
        test.dut.mux_2.close()

    def define_http_profile(test, srv_id, cmd, http_path, mux_port):
        http_client = HttpProfile(test.dut, srv_id, test.con_id, http_command=cmd,
                                  host=test.server_address, http_path=http_path,
                                  device_interface=mux_port, port=test.server_port)
        if cmd == "post":
            http_client.dstl_set_hc_cont_len(test.package)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        return http_client


if "__main__" == __name__:
    unicorn.main()
