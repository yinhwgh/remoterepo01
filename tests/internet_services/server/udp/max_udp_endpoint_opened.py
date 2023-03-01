#responsible: michal.habrych@globallogic.com
#location: Wroclaw
#TC0102311.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile



class Test(BaseTest):
    """
    Intention:
    Check using maximum number of UDP endpoints

    Description:
    1. Prepare and activate PDP context
    2. Set maximum number of UDP endpoints on DUT.
    3. Open endpoints.
    4. Set UDP clients on REMOTE.
    5. Send data from clients to each of endpoints.
    6. Receive and read data on endpoints and check RX/TX.
    7. Close and remove all profiles.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)

    def run(test):
        test.log.info("Executing script for test case: 'TC0102311.001 MaxUdpEndpointOpened'")

        test.log.step("1. Prepare and activate PDP context")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_remote = dstl_get_connection_setup_object(test.r1)
        test.expect(connection_setup_remote.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Set maximum number of UDP endpoints on DUT.")
        test.endpoint_dut = []
        for profile_number in range(10):
            current_port = "600" + str(profile_number)
            test.endpoint_dut.append(SocketProfile(test.dut, profile_number, connection_setup_dut.dstl_get_used_cid(),
                                          protocol="udp", port=current_port))
            test.endpoint_dut[profile_number].dstl_generate_address()
            test.expect(test.endpoint_dut[profile_number].dstl_get_service().dstl_load_profile())

        test.log.step("3. Open endpoints.")
        for profile_number in range(10):
            test.expect(test.endpoint_dut[profile_number].dstl_get_service().dstl_open_service_profile())
            test.expect(test.endpoint_dut[profile_number].dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("4. Set UDP clients on REMOTE.")
        dut_ip = test.endpoint_dut[0].dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4'). \
            split(":")
        test.client_rem = []
        for profile_number in range(10):
            current_port = "600" + str(profile_number)
            test.client_rem.append(SocketProfile(test.r1, profile_number, connection_setup_remote.dstl_get_used_cid(),
                                             protocol="udp", host=dut_ip[0], port=current_port))
            test.client_rem[profile_number].dstl_generate_address()
            test.expect(test.client_rem[profile_number].dstl_get_service().dstl_load_profile())

        test.log.step("5. Send data from clients to each of endpoints.")
        for profile_number in range(10):
            test.expect(test.client_rem[profile_number].dstl_get_service().dstl_open_service_profile())
            test.expect(test.client_rem[profile_number].dstl_get_urc().dstl_is_sisw_urc_appeared(1))
            test.client_rem[profile_number].dstl_get_service().dstl_send_sisw_command_and_data(1000)
            test.expect(test.endpoint_dut[profile_number].dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("6. Receive and read data on endpoints and check RX/TX.")
        for profile_number in range(10):
            test.expect(test.endpoint_dut[profile_number].dstl_get_service().dstl_read_data(1000))
            test.expect(test.endpoint_dut[profile_number].dstl_get_parser().dstl_get_service_data_counter("rx") == 1000)
            test.expect(test.endpoint_dut[profile_number].dstl_get_parser().dstl_get_service_data_counter("tx") == 0)

    def cleanup(test):
        test.log.step("7. Close and remove all profiles.")
        try:
            for profile_number in range(10):
                test.expect(test.endpoint_dut[profile_number].dstl_get_service().dstl_close_service_profile())
                test.expect(test.endpoint_dut[profile_number].dstl_get_service().dstl_reset_service_profile())
                test.expect(test.client_rem[profile_number].dstl_get_service().dstl_close_service_profile())
                test.expect(test.client_rem[profile_number].dstl_get_service().dstl_reset_service_profile())
        except (AttributeError, IndexError):
            test.log.error("Problem with connection to module")


if "__main__" == __name__:
    unicorn.main()
