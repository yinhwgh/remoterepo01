# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0105923.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from re import search


class Test(BaseTest):
    """
    Intention:
    Intention of this TC is to verify http and https functionality of address extension

    Description:
    1. Define HTTP internet profile with extended address length (2044 characters). The whole
    address should be divided into address, address2, address3, and address4 parameters (each up to
    511 characters).
    2. Using read command AT^SISS, check if the divided address contains all characters defined in
    step 1.
    3. Define FTP internet profile with extended address length (2044 characters). The whole
    address should be divided into address, address2, address3, and address4 parameters (each up to
    511 characters).
    4. Using read command AT^SISS, check if the divided address contains all characters defined in
    step 3.
    5. Redefine FTP internet profile (from step 3) using only one address field.
    6. Using read command AT^SISS, check the address defined in step 5.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.long_path = "123.145.167.189:50000/1111111111111111111111111111111111111111111111111" \
                         "11111111111111111111111111111111111111111111111111111111111111111111111" \
                         "11111111111111111111111111111111111111111111111111111111111111111111111" \
                         "1111111111111111111111111111111111111111111111111111111111111111/222222" \
                         "22222222222222222222222222222222222222222222222222222222222222222222222" \
                         "22222222222222222222222222222222222222222222222222222222222222222222222" \
                         "22222222222222222222222222222222222222222222222222222222222222222222222" \
                         "222222222222222222222222222222222222/3333333333333333333333333333333333" \
                         "33333333333333333333333333333333333333333333333333333333333333333333333" \
                         "33333333333333333333333333333333333333333333333333333333333333333333333" \
                         "33333333333333333333333333333333333333333333333333333333333333333333333" \
                         "33333333/44444444444444444444444444444444444444444444444444444444444444" \
                         "44444444444444444444444444444444444444444444444444444444444444444444444" \
                         "44444444444444444444444444444444444444444444444444444444444444444444444" \
                         "444444444444444444444444444444444444444444444444444/5555555555555555555" \
                         "55555555555555555555555555555555555555555555555555555555555555555555555" \
                         "55555555555555555555555555555555555555555555555555555555555555555555555" \
                         "55555555555555555555555555555555555555555555555555555555555555555555555" \
                         "55555555555555555555555/66666666666666666666666666666666666666666666666" \
                         "66666666666666666666666666666666666666666666666666666666666666666666666" \
                         "66666666666666666666666666666666666666666666666666666666666666666666666" \
                         "666666666666666666666666666666666666666666666666666666666666666666/7777" \
                         "77777777777777777777777777777777777777777777777777777777777777777777777" \
                         "77777777777777777777777777777777777777777777777777777777777777777777777" \
                         "77777777777777777777777777777777777777777777777777777777777777777777777" \
                         "77777777777777777777777777777777777777/88888888888888888888888888888888" \
                         "88888888888888888888888888888888888888888888888888888888888888888888888" \
                         "88888888888888888888888888888888888888888888888888888888888888888888888" \
                         "8888888888888888888888888888888888/"
        test.http_file = "test_http1.txt"
        test.ftp_file = "test_ftp_1.txt"
        test.http_long = "http://" + test.long_path + test.http_file
        test.ftp_long = "ftp://" + test.long_path + test.ftp_file
        test.ftp_short = "ftp://" + test.long_path[0:278] + test.ftp_file

    def run(test):
        test.log.info("TC0105923.001 address_extension_basic")
        test.log.step("1. Define HTTP internet profile with extended address length (2044 "
                      "characters). The whole address should be divided into address, address2, "
                      "address3, and address4 parameters (each up to 511 characters).")
        test.http_client = HttpProfile(test.dut, '0', '1', http_command="get",
                            address=test.http_long[0:511], address2=test.http_long[511:1022],
                            address3=test.http_long[1022:1533], address4=test.http_long[1533:])
        test.expect(test.http_client.dstl_get_service().dstl_load_profile())

        test.log.step("2. Using read command AT^SISS, check if the divided address contains all "
                      "characters defined in step 1.")
        test.check_siss_addr_param('0', test.http_long[0:511], test.http_long[511:1022],
                                   test.http_long[1022:1533], test.http_long[1533:], 1)

        test.log.step("3. Define FTP internet profile with extended address length (2044 "
                      "characters). The whole address should be divided into address, address2, "
                      "address3, and address4 parameters (each up to 511 characters).")
        test.ftp_client = FtpProfile(test.dut, '1', '1', command="get", alphabet="1",
                            address=test.ftp_long[0:511], address2=test.ftp_long[511:1022],
                            address3=test.ftp_long[1022:1533], address4=test.ftp_long[1533:])
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("4. Using read command AT^SISS, check if the divided address contains all "
                      "characters defined in step 3")
        test.check_siss_addr_param('1', test.ftp_long[0:511], test.ftp_long[511:1022],
                            test.ftp_long[1022:1533], test.ftp_long[1533:], 1)

        test.log.step("5. Redefine FTP internet profile (from step 3) using only one address field")
        test.ftp_client = FtpProfile(test.dut, '1', '1', command="get", address=test.ftp_short)
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("6. Using read command AT^SISS, check the address defined in step 5")
        test.check_siss_addr_param('1', test.ftp_short, test.ftp_long[511:1022],
                            test.ftp_long[1022:1533], test.ftp_long[1533:], 0)

    def cleanup(test):
        try:
            test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.http_client.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")

    def check_siss_addr_param(test, conid, addr1, addr2, addr3, addr4, extended_addr_flag):
        dstl_get_siss_read_response(test.dut)
        if extended_addr_flag == 1:
            test.expect(search(fr'.*SISS: {conid},"address","{addr1}"', test.dut.at1.last_response))
            test.expect(search(fr'.*SISS: {conid},"address2","{addr2}"',
                               test.dut.at1.last_response))
            test.expect(search(fr'.*SISS: {conid},"address3","{addr3}"',
                               test.dut.at1.last_response))
            test.expect(search(fr'.*SISS: {conid},"address4","{addr4}"',
                               test.dut.at1.last_response))
        else:
            test.expect(search(fr'.*SISS: {conid},"address","{addr1}"', test.dut.at1.last_response))
            test.expect(not search(fr'.*SISS: {conid},"address2",".*"', test.dut.at1.last_response))
            test.expect(not search(fr'.*SISS: {conid},"address3",".*"', test.dut.at1.last_response))
            test.expect(not search(fr'.*SISS: {conid},"address4",".*"', test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()