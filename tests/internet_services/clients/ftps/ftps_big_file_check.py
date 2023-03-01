# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107602.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftps_server import FtpsServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.network_service.register_to_network import dstl_enter_pin
from os.path import join


class Test(BaseTest):
    """
    Intention:
    Verify FTPs behavior during upload and download big file content.

    Description:
    1. Set PDP context/Connection profile.
    2. Set FTPs PUT profile  (in file name use specials characters and space).
    3. Install certs to FTPs server, set secopt to 1
    4. Open profile and upload file ~5MB.
    5. Set FTPs GET profile.
    6. Download file, check RX counter.
    7. Set FTPs DEL profile.
    8. Delete file on the server.
    9. Close all profiles and delete them
    10. Delete certificates
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.file_name = "FTPS @5M.txt"
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        send_loops = 3333
        receive_loops = send_loops + 1
        data_length = 1500
        file_length = 5001000

        test.log.info("TC0107602.001 FtpsBigFileCheck")
        test.log.step("1. Set PDP context/Connection profile.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftps_server = FtpsServer("IPv4", test, test.connection_setup.dstl_get_used_cid(),
                                      test_duration=8)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("2. Set FTPs PUT profile  (in file name use specials characters and space)")
        test.ftps_client_put = FtpProfile(test.dut, 0, test.cid, command="put", alphabet="1",
                                      files=test.file_name, secopt="1", secure_connection=True)
        test.ftps_client_put.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_client_put.dstl_generate_address()
        test.expect(test.ftps_client_put.dstl_get_service().dstl_load_profile())

        test.log.step("3. Install certs to FTPs server, set secopt to 1")
        test.certificates = InternetServicesCertificates(test.dut)
        test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_certificate_at_index_0(
                                (join("openssl_certificates", "client.der")),
                                (join("openssl_certificates", "private_client_key")))
        test.certificates.dstl_upload_server_certificate("1", join("echo_certificates",
                                                                   "client", "ca.der"))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Open profile and upload file ~5MB.")
        test.expect(test.ftps_client_put.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftps_client_put.dstl_get_service().dstl_send_sisw_command_and_data(
                                            data_length,repetitions=send_loops, expected="OK"))
        test.expect(test.ftps_client_put.dstl_get_service().dstl_send_sisw_command_and_data(
                                            data_length, eod_flag="1"))
        test.expect(test.ftps_client_put.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftps_client_put.dstl_get_parser().dstl_get_service_state() ==
                                            ServiceState.DOWN.value)
        test.expect(test.ftps_client_put.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                                            file_length)

        test.log.step("5. Set FTPs GET profile.")
        test.ftps_client_get = FtpProfile(test.dut, 1, test.cid, command="get", alphabet="1",
                                         files=test.file_name, secopt="1", secure_connection=True)
        test.ftps_client_get.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_client_get.dstl_generate_address()
        test.expect(test.ftps_client_get.dstl_get_service().dstl_load_profile())

        test.log.step("6. Download file, check RX counter.")
        test.expect(test.ftps_client_get.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftps_client_get.dstl_get_service().dstl_read_data(data_length,
                                                                repetitions=receive_loops))
        test.expect(test.ftps_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(test.ftps_client_get.dstl_get_parser().dstl_get_service_state() ==
                                                                ServiceState.DOWN.value)
        test.expect(test.ftps_client_get.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                                                                file_length)

        test.log.step("7. Set FTPs DEL profile.")
        test.ftps_client_del = FtpProfile(test.dut, 2, test.cid, command="del", alphabet="1",
                                         files=test.file_name, secopt="1", secure_connection=True)
        test.ftps_client_del.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_client_del.dstl_generate_address()
        test.expect(test.ftps_client_del.dstl_get_service().dstl_load_profile())

        test.log.step("8. Delete file on the server.")
        test.expect(test.ftps_client_del.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftps_client_del.dstl_get_urc().dstl_is_sis_urc_appeared("0","2100",
                                                                '"250 DELE command successful"'))

    def cleanup(test):
        test.log.step("9. Close all profiles and delete them")
        try:
            test.expect(test.ftps_client_put.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftps_client_put.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.ftps_client_get.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftps_client_get.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.ftps_client_del.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftps_client_del.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")
        try:
            test.ftps_server.dstl_ftp_server_delete_file(test.file_name)
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

        test.log.step("10. Delete certificates")
        try:
            test.expect(test.certificates.dstl_delete_certificate(0))
            test.expect(test.certificates.dstl_delete_certificate(1))
        except AttributeError:
            test.log.error("certificates was not created.")


if __name__ == "__main__":
    unicorn.main()