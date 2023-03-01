# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107945.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention:
    To check if defining Http profiles using SISS command works fine

    Description:
    1) Power on Module
    2) On first SISS profile define http get profile with only mandatory set of parameters
    3) On second SISS profile define http post profile with only mandatory set of parameters
    4) On third SISS profile define http head profile with only mandatory set of parameters
    5) Check if profiles were correctly defined using AT^SISS? command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.get_addr = "http://147.135.208.186:1"
        test.post_addr = "http://testserver:65535"
        test.head_addr = "http://test123"


    def run(test):
        test.log.info("TC0107945.001 SissHttp_basic")
        test.log.step('1) Power on Module')
        dstl_restart(test.dut)

        test.log.step('2) On first SISS profile define http get profile with only mandatory set of'
                      ' parameters')
        test.http_get = HttpProfile(test.dut, "0", "1", address=test.get_addr, http_command="get")
        test.expect(test.http_get.dstl_get_service().dstl_load_profile())

        test.log.step('3) On second SISS profile define http post profile with only mandatory set'
                      ' of parameters')
        test.http_post = HttpProfile(test.dut, "1", "1", address=test.post_addr,
                                     http_command="post", hc_cont_len="1000")
        test.expect(test.http_post.dstl_get_service().dstl_load_profile())

        test.log.step('4) On third SISS profile define http head profile with only mandatory set of'
                      ' parameters')
        test.http_head = HttpProfile(test.dut, "2", "1", address=test.head_addr,
                                     http_command="head")
        test.expect(test.http_head.dstl_get_service().dstl_load_profile())

        test.log.step('5) Check if profiles were correctly defined using AT^SISS? command')
        dstl_check_siss_read_response(test.dut, [test.http_get, test.http_post, test.http_head])

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))


if "__main__" == __name__:
    unicorn.main()