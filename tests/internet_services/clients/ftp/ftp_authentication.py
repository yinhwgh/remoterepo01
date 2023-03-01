# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0010957.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """This test checks behaviour of module while data transfer with using
     wrong username/password combinations."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.step("1. Enter PIN and attach module to network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Depends on product: - Set Connection Profile (GPRS) - Define PDP Context")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftp_server = FtpServer("IPv4", test, connection_setup.dstl_get_used_cid(),
                                    extended=True)
        data_50 = 50
        test.ftp_server.dstl_ftp_server_create_file("test.txt", data_50)

        test.log.step("3. Perform a FTP get session with correct password and username to "
                      "download data.")
        srv_id = "0"
        test.ftp_client = FtpProfile(test.dut, srv_id, connection_setup.dstl_get_used_cid(),
                                     command="get", ip_server=test.ftp_server, alphabet="1",
                                     files="test.txt")
        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.sleep(10)

        test.log.step("4. Open defined profile")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("5. Download some data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_50))
        test.expect(test.ftp_client.dstl_get_service().dstl_get_confirmed_read_length() == data_50)

        test.log.step("6. Close defined profile")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.perform_steps_3_to_6(test.ftp_client, data_50, 1)
        test.perform_steps_3_to_6(test.ftp_client, data_50, 2)
        test.perform_steps_3_to_6(test.ftp_client, data_50, 3)

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_clean_up_directories():
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())

    def perform_steps_3_to_6(test, ftp_client, data_50, case_of_perform):
        if case_of_perform == 1:
            test.log.step("7. Repeat steps 3-6 but set: a) correct username and invalid password")
            test.log.step("3. Perform a FTP get session with invalid password and correct username"
                          " to download data.")
            ftp_client.dstl_set_passwd("invalidPassword")
        elif case_of_perform == 2:
            test.log.step("7. Repeat steps 3-6 but set: b) invalid username and any password")
            test.log.step("3. Perform a FTP get session with any password and invalid username"
                          " to download data.")
            ftp_client.dstl_set_user("invalidUsername")
            ftp_client.dstl_set_passwd("anyPassword")

        elif case_of_perform == 3:
            test.log.step("7. Repeat steps 3-6 but set: c) correct username and empty password")
            test.log.step("3. Perform a FTP get session with empty password and correct username"
                          " to download data.")
            ftp_client.dstl_set_user(test.ftp_server.dstl_get_ftp_server_user())
            ftp_client.dstl_set_passwd("")

        test.expect(ftp_client.dstl_get_service().dstl_write_user())
        test.expect(ftp_client.dstl_get_service().dstl_write_passwd())

        test.log.step("4. Open defined profile")
        test.expect(ftp_client.dstl_get_service().dstl_open_service_profile(
            expected=".*100,\"ERR.*"))
        test.expect(ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared(2))

        test.log.step("5. Download some data.")
        test.expect(ftp_client.dstl_get_service().dstl_read_data(data_50, skip_data_check=True))
        test.expect(ftp_client.dstl_get_service().dstl_get_confirmed_read_length() == -2)

        test.log.step("6. Close defined profile")
        test.expect(ftp_client.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()