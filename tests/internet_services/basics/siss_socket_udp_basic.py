# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107954.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention:
    To check if defining UDP socket profiles using SISS command works fine

    Description:
    1) Power on Module
    2) On first SISS profile define Transparent UDP client with only mandatory set of parameters
    3) On second SISS profile define Non-Transparent UDP client with only mandatory set of parameters
    4) On third profile define UDP Endpoint with only mandatory set of parameters
    5) Check if profiles were correctly defined using AT^SISS? command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.transp_client_addr = "sockudp://147.135.208.186:1;etx=26"
        test.nontransp_client_addr = "sockudp://testserver:65535"
        test.endpoint_addr = "sockudp://:60000"

    def run(test):
        test.log.info("TC0107954.001 SissSocketUdp_basic")
        test.log.step('1) Power on Module')
        dstl_restart(test.dut)

        test.log.step('2) On first SISS profile define Transparent UDP client with only mandatory'
                      ' set of parameters')
        test.transp_client = SocketProfile(test.dut, "0", "1", address=test.transp_client_addr)
        test.expect(test.transp_client.dstl_get_service().dstl_load_profile())

        test.log.step('3) On second SISS profile define Non-Transparent UDP client with only'
                      ' mandatory set of parameters')
        test.nontransp_client = SocketProfile(test.dut, "1", "1",
                                              address=test.nontransp_client_addr)
        test.expect(test.nontransp_client.dstl_get_service().dstl_load_profile())

        test.log.step('4) On third profile define UDP Endpoint with only mandatory set of'
                      ' parameters')
        test.endpoint = SocketProfile(test.dut, "2", "1", address=test.endpoint_addr)
        test.expect(test.endpoint.dstl_get_service().dstl_load_profile())

        test.log.step('6) Check if profiles were correctly defined using AT^SISS? command')
        dstl_check_siss_read_response(test.dut, [test.transp_client, test.nontransp_client,
                                                 test.endpoint])

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))


if "__main__" == __name__:
    unicorn.main()