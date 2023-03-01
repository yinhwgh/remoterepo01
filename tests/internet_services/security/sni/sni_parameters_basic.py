# responsible: michal.kopiel@globallogic.com
# location: Wroclaw
# TC0105649.001

import unicorn
from core.basetest import BaseTest

from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response


class Test(BaseTest):
    """
    1. Create HTTPS service profile with "secsni" parameter set to "1" 
    2. Check the value of parameter "secsni"
    3. Set SNI Extension to "0"
    4. Check the value of parameter "secsni"
    5. Set 255 character long name using "sniname" parameter
    6. Check the value of parameter "sniname"
    """

    def setup(test):
        test.srv_id_0 = '0'
        test.con_id = '1'

        dstl_detect(device=test.dut)
        dstl_get_imei(device=test.dut)

    def run(test):
        test.log.step("1. Create HTTPS service profile with \"secsni\" parameter set to \"1\"")
        https_server = "https://www.httpbin.org"

        test.https_profile = HttpProfile(device=test.dut, srv_profile_id=test.srv_id_0,
                                         secure_connection=True, con_id=test.con_id,
                                         address=https_server, http_command="get", secsni='1')
        test.expect(test.https_profile.dstl_get_service().dstl_load_profile())

        test.log.step("2. Check the value of parameter \"secsni\"")
        test.expect(dstl_get_siss_read_response(device=test.dut))
        test.expect(
            f'SISS: {test.srv_id_0},"secsni","{1}"' in test.dut.at1.last_response)
        dstl_check_siss_read_response(device=test.dut, service_profiles=[test.https_profile])

        test.log.step("3. Set SNI Extension to \"0\"")
        test.https_profile.dstl_set_secsni(secsni='0')
        test.expect(test.https_profile.dstl_get_service().dstl_write_secsni())

        test.log.step("4. Check the value of parameter \"secsni\"")
        test.expect(dstl_get_siss_read_response(device=test.dut))
        test.expect(
            f'SISS: {test.srv_id_0},"secsni","{0}"' in test.dut.at1.last_response)
        dstl_check_siss_read_response(device=test.dut, service_profiles=[test.https_profile])

        test.log.step("5. Set 255 character long name using \"sniname\" parameter")
        sniname = dstl_generate_data(length=255)
        test.https_profile.dstl_set_sniname(sniname=sniname)
        test.expect(test.https_profile.dstl_get_service().dstl_write_sniname())

        test.log.step("6. Check the value of parameter \"sniname\"")
        test.expect(dstl_get_siss_read_response(device=test.dut))
        test.expect(
            f'SISS: {test.srv_id_0},"sniname","{sniname}"' in test.dut.at1.last_response)
        dstl_check_siss_read_response(device=test.dut, service_profiles=[test.https_profile])

    def cleanup(test):
        test.expect(test.https_profile.dstl_get_service().dstl_reset_service_profile())


if __name__ == "__main__":
    unicorn.main()
