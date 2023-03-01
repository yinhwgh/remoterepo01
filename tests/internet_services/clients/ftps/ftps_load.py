# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107603.001

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
    To checks long time stability of the FTPs service.

    Description:
	1. Depends on product:
    - Set Connection Profile (GPRS)
    - Define and activate PDP Context.
    2. Install certificates.
    3. Configure a FTPs "put" session (with secopt 1).
    4. Open the service profile and wait for "^SISW:" URC.
    5. Send some data to the service (~3KB).
    6. Close the service profile.
    7. Configure a FTPs "get" session. In address field enter the path to the file that you created
     earlier.
    8. Open the service profile and wait for "^SISR:" URC.
    9. Read all data from file on the FTP server.
    10. Close the service profile.
    11. Configure a FTPs "delete" session.
    12. Open the service profile and wait until srvState changes to DOWN.
    13. Close the service profile.
    14. Open FTPs "get" session.
    15. Check if file exist.
    16. Close the service profile.
    17. Repeat Testcase (steps 4-16) 800 times.
    18. Remove certificates and services profiles.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.file_name = "FTPs#3KB.txt"
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        receive_loops = 2
        data_length = 1500
        file_length = 3000
        test_loops = 800

        test.log.info("TC0107603.001 FtpsLoad")
        test.log.step("1	1. Depends on product:\r\n "
                      "- Set Connection Profile (GPRS).\r\n "
                      "- Define and activate PDP Context. ")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftps_server = FtpsServer("IPv4", test, test.connection_setup.dstl_get_used_cid(),
                                      test_duration=8)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("2. Install certificates.")
        test.certificates = InternetServicesCertificates(test.dut)
        test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_certificate_at_index_0(
                                (join("openssl_certificates", "client.der")),
                                (join("openssl_certificates", "private_client_key")))
        test.certificates.dstl_upload_server_certificate("1", join("echo_certificates",
                                                                   "client", "ca.der"))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("3. Configure a FTPs put session (with secopt 1).")
        test.ftps_client_put = FtpProfile(test.dut, 0, test.cid, command="put", alphabet="1",
                                      files=test.file_name, secopt="1", secure_connection=True)
        test.ftps_client_put.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_client_put.dstl_generate_address()
        test.expect(test.ftps_client_put.dstl_get_service().dstl_load_profile())

        test.log.info("Creating GET (step 7) and DEL(step 11) profiles will be done here "
                      "to avoid defining them every loop")
        test.ftps_client_get = FtpProfile(test.dut, 1, test.cid, command="get", alphabet="1",
                                          files=test.file_name, secopt="1", secure_connection=True,
                                          are_concatenated=True, files_in_address=True)
        test.ftps_client_get.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_client_get.dstl_generate_address()
        test.expect(test.ftps_client_get.dstl_get_service().dstl_load_profile())
        test.ftps_client_del = FtpProfile(test.dut, 2, test.cid, command="del", alphabet="1",
                                         files=test.file_name, secopt="1", secure_connection=True)
        test.ftps_client_del.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_client_del.dstl_generate_address()
        test.expect(test.ftps_client_del.dstl_get_service().dstl_load_profile())

        for loop in range(test_loops):
            test.log.step("Starting {} out of {} loops\r\n4. Open the service profile and wait "
                          "for ^SISW: URC".format(loop+1, test_loops))
            test.expect(test.ftps_client_put.dstl_get_service().dstl_open_service_profile())

            test.log.step("5. Send some data to the service (~3KB)")
            test.expect(test.ftps_client_put.dstl_get_service().dstl_send_sisw_command_and_data(
                                                data_length, expected="OK"))
            test.expect(test.ftps_client_put.dstl_get_service().dstl_send_sisw_command_and_data(
                                                data_length, eod_flag="1"))
            test.expect(test.ftps_client_put.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
            test.expect(test.ftps_client_put.dstl_get_parser().dstl_get_service_state() ==
                                                ServiceState.DOWN.value)
            test.expect(test.ftps_client_put.dstl_get_parser().dstl_get_service_data_counter("tx")
                                                == file_length)

            test.log.step("6. Close the service profile")
            test.expect(test.ftps_client_put.dstl_get_service().dstl_close_service_profile())

            test.log.step("7. Configure a FTPs get session. In address field enter the path to "
                                                   "the file that you created earlier.")
            test.log.info("done is step 3")

            test.log.step("8. Open the service profile and wait for ^SISR: URC")
            test.expect(test.ftps_client_get.dstl_get_service().dstl_open_service_profile())

            test.log.step("9. Read all data from file on the FTP server.")
            test.expect(test.ftps_client_get.dstl_get_service().dstl_read_data(data_length,
                                                                    repetitions=receive_loops))
            test.expect(test.ftps_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
            test.expect(test.ftps_client_get.dstl_get_parser().dstl_get_service_state() ==
                                                                    ServiceState.DOWN.value)
            test.expect(test.ftps_client_get.dstl_get_parser().dstl_get_service_data_counter("rx")
                                                                    == file_length)

            test.log.step("10. Close the service profile.")
            test.expect(test.ftps_client_get.dstl_get_service().dstl_close_service_profile())

            test.log.step("11. Configure a FTPs delete session.")
            test.log.info("done is step 3")

            test.log.step("12. Open the service profile and wait until srvState changes to DOWN.")
            test.expect(test.ftps_client_del.dstl_get_service().dstl_open_service_profile())
            test.expect(test.ftps_client_del.dstl_get_urc().dstl_is_sis_urc_appeared("0","2100",
                                                                '"250 DELE command successful"'))

            test.log.step("13. Close the service profile.")
            test.expect(test.ftps_client_del.dstl_get_service().dstl_close_service_profile())

            test.log.step("14. Open FTPs get session.")
            test.expect(test.ftps_client_get.dstl_get_service().dstl_open_service_profile(
                                                                wait_for_default_urc=False))

            test.log.step("15. Check if file exist.")
            test.expect(test.ftps_client_get.dstl_get_urc().dstl_is_sis_urc_appeared("0", "100",
                                           '"ERR: 550 FTPs#3KB.txt: No such file or directory"'))

            test.log.step("16. Close the service profile.")
            test.expect(test.ftps_client_get.dstl_get_service().dstl_close_service_profile())

            test.log.step("17. Repeat Testcase (steps 4-16) 800 times.")

    def cleanup(test):
        test.log.step("18. Remove certificates and services profiles.")
        try:
            test.expect(test.certificates.dstl_delete_certificate(0))
            test.expect(test.certificates.dstl_delete_certificate(1))
        except AttributeError:
            test.log.error("certificates was not created.")

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


if __name__ == "__main__":
    unicorn.main()