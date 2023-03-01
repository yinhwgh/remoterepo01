# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107973.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention:
    To check if defining COAP profiles using SISS command work fine

    Description:
    1) Power on Module
    2) On first SISS profile define coap "get" profile with only mandatory set of parameters
    3) On second SISS profile define coap "put" profile with only mandatory set of parameters
    4) On third SISS profile define coap "empty" profile with only mandatory set of parameters
    5) On fourth SISS profile define coap "delete" profile with only mandatory set of parameters
    6) Check if profiles were correctly defined using AT^SISS? command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.coap_ip_addr = "coap://147.135.208.186:1"
        test.coap_fqdn_addr = "coap://testserver:65535"
        test.coap_noport_addr = "coap://213.167.189.245"

    def run(test):
        test.log.info("TC0107973.001 SissCoap_basic")
        test.log.step('1) Power on Module')
        dstl_restart(test.dut)

        test.log.step('2) On first SISS profile define coap "get" profile with only mandatory '
                      'set of parameters')
        test.coap_get_profile = test.define_coap_profile(0, "get", test.coap_ip_addr)

        test.log.step('3) On second SISS profile define coap "put" profile with only mandatory '
                      'set of parameters')
        test.coap_put_profile = test.define_coap_profile(1, "put", test.coap_fqdn_addr)

        test.log.step('4) On third SISS profile define coap "empty" profile with only mandatory '
                      'set of parameters')
        test.coap_empty_profile = test.define_coap_profile(2, "empty", test.coap_noport_addr)

        test.log.step('5) On fourth SISS profile define coap "delete" profile with only mandatory '
                      'set of parameters')
        test.coap_delete_profile = test.define_coap_profile(3, "delete", test.coap_ip_addr)

        test.log.step('6) Check if profiles were correctly defined using AT^SISS? command')
        test.expect(test.dut.at1.send_and_verify('AT^SISS?', expect="OK"))
        test.compare_siss("0", "get", test.coap_ip_addr)
        test.compare_siss("1", "put", test.coap_fqdn_addr)
        test.compare_siss("2", "empty", test.coap_noport_addr)
        test.compare_siss("3", "delete", test.coap_ip_addr)

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))

    def define_coap_profile(test, siss_id, coap_cmd, coap_addr):
        test.expect(test.dut.at1.send_and_verify(f'AT^SISS={siss_id},srvtype,coap', expect="OK"))
        test.expect(test.dut.at1.send_and_verify(f'AT^SISS={siss_id},conid,1', expect="OK"))
        test.expect(test.dut.at1.send_and_verify(f'AT^SISS={siss_id},cmd,{coap_cmd}',
                                                                                    expect="OK"))
        test.expect(test.dut.at1.send_and_verify(f'AT^SISS={siss_id},address,{coap_addr}',
                                                                                    expect="OK"))

    def compare_siss(test, siss_id, coap_cmd, coap_addr):
        test.expect(f'SISS: {siss_id},"srvType","Coap"' in test.dut.at1.last_response)
        test.expect(f'SISS: {siss_id},"conId","1"' in test.dut.at1.last_response)
        test.expect(f'SISS: {siss_id},"address","{coap_addr}"' in test.dut.at1.last_response)
        test.expect(f'SISS: {siss_id},"cmd","{coap_cmd}"' in test.dut.at1.last_response)


if "__main__" == __name__:
    unicorn.main()