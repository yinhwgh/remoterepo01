#responsible dominik.tanderys@globallogic.com
#Wroclaw
#TC0095697.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command

class Test(BaseTest):
    """Intention:
    Check basic AT^SISI functionality

    Description:
    1. Define PDP context and activate internet connection if required
    2. Define FTP profile with GET method
    3. Check ^SISI
    4. Open FTP profile
    5. Check ^SISI
    6. Read all data
    7. Check ^SISI
    8. Close FTP Connection"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.step("1. Define PDP context and activate internet connection if required")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftp_server = FtpServer("IPv4", test, connection_setup.dstl_get_used_cid())
        data_length = 100
        test.ftp_server.dstl_ftp_server_create_file("test.txt", data_length)

        test.log.step("2. Define FTP profile with GET method")
        ftp_client = FtpProfile(test.dut, "0", connection_setup.dstl_get_used_cid(), command="get",
                                ip_server=test.ftp_server, alphabet="1", files="test.txt")
        ftp_client.dstl_set_parameters_from_ip_server()
        ftp_client.dstl_generate_address()
        test.expect(ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Check ^SISI")
        test.expect(ftp_client.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE) ==
                    ServiceState.ALLOCATED.value, msg="Wrong service state")

        test.log.step("4. Open FTP profile")
        test.expect(ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("5. Check ^SISI")
        test.expect(ftp_client.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE) ==
                    ServiceState.UP.value, msg="Wrong service state")

        test.log.step("6. Read all data")
        test.expect(ftp_client.dstl_get_service().dstl_read_data(data_length))
        test.expect(ftp_client.dstl_get_service().dstl_get_confirmed_read_length() == data_length)

        test.log.step("7. Check ^SISI")
        test.expect(ftp_client.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE) ==
                    ServiceState.DOWN.value, msg="Wrong service state")

        test.log.step("8. Close FTP Connection")
        test.expect(ftp_client.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file("test.txt"):
                test.log.warn("Problem with deleting file.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")

        except AttributeError:
            test.log.error("Object was not created.")


if (__name__ == "__main__"):
    unicorn.main()