# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107946.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention:
    To check if defining Ftp profiles using SISS command works fine

    Description:
    1) Power on Module
    2) On first SISS profile define ftp get profile with only mandatory set of parameters
    3) On second SISS profile define ftp put profile with only mandatory set of parameters
    4) On third SISS profile define ftp del profile with only mandatory set of parameters
    5) Check if profiles were correctly defined using AT^SISS? command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.get_addr = "ftp://147.135.208.186:1"
        test.put_addr = "ftp://testserver:65535"
        test.del_addr = "ftp://test123"
        test.file = "test1234.txt"

    def run(test):
        test.log.info("TC0107946.001 SissFtp_basic")
        test.log.step('1) Power on Module')
        dstl_restart(test.dut)

        test.log.step('2) On first SISS profile define ftp get profile with only mandatory set of'
                      ' parameters')
        test.ftp_get = FtpProfile(test.dut, "0", "1", address=test.get_addr, command="get",
                                   files=test.file)
        test.expect(test.ftp_get.dstl_get_service().dstl_load_profile())

        test.log.step('3) On second SISS profile define ftp put profile with only mandatory set of'
                      ' parameters')
        test.ftp_put = FtpProfile(test.dut, "1", "1", address=test.put_addr, command="put",
                                    files=test.file)
        test.expect(test.ftp_put.dstl_get_service().dstl_load_profile())

        test.log.step('4) On third SISS profile define ftp del profile with only mandatory set of'
                      ' parameters')
        test.ftp_del = FtpProfile(test.dut, "2", "1", address=test.del_addr, command="del",
                                    files=test.file)
        test.expect(test.ftp_del.dstl_get_service().dstl_load_profile())

        test.log.step('5) Check if profiles were correctly defined using AT^SISS? command')
        dstl_check_siss_read_response(test.dut, [test.ftp_get, test.ftp_put, test.ftp_del])

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))


if "__main__" == __name__:
    unicorn.main()