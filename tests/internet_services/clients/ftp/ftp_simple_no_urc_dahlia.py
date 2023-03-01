#responsible: michal.habrych@globallogic.com
#location: Wroclaw
#TC0012075.002, TC0012075.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Intention:
    Perfom a simple FTP put and get session with URCs disabled.

    Description:
    1) Disable internet URCs mode by calling AT^SCFG.
    2) Configure FTP session and set "cmd" parameter to "put"
    3) Open defined service.
    4) Check service state.
    5) Send one 1500 byte block.
    6) Close the service, change file name and open it again.
    7) Check service state.
    8) Send three 1500 byte blocks. Remember that to send only the last block with EOD (end of data flag).
    9) Close the service
    10) Change "cmd" parameter to "get"
    11) Open the service.
    12) Check service state.
    13) Download the file sent in step 6.
    14) Close the service, change file name and open it again.
    15) Check service state.
    16) Download the file sent in step 9.
    17) Close and delete service.
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, test.cid)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.file1_name = "test_1500.txt"
        test.file2_name = "test_4500.txt"

    def run(test):
        data_length = 1500
        file1_length = 1500
        file2_length = 4500

        test.log.info("TC0012075.003 - FtpSimpleNoUrc_Dahlia")
        test.log.step("1) Disable internet URCs mode by calling AT^SCFG.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))

        test.log.step("2) Configure FTP session and set 'cmd' parameter to 'put' ")
        test.define_and_print_ftp_profile("put", test.file1_name)

        test.log.step("3) Open defined service. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4) Check service state. ")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("5) Send one 1500 byte block. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("tx") == file1_length)

        test.log.step("6) Close the service, change file name and open it again. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.ftp_client.dstl_set_files(test.file2_name)
        test.expect(test.ftp_client.dstl_get_service().dstl_write_files())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("7) Check service state. ")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("8) Send three 1500 byte blocks. Remember that to send only the last block with EOD "
                      "(end of data flag). ")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, repetitions=2
                                                                                       , expected="OK"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("tx") == file2_length)

        test.log.step("9) Close the service. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("10) Change 'cmd' parameter to 'get'.")
        test.ftp_client.dstl_set_ftp_command("get")
        test.expect(test.ftp_client.dstl_get_service().dstl_write_cmd())
        test.ftp_client.dstl_set_files(test.file1_name)
        test.expect(test.ftp_client.dstl_get_service().dstl_write_files())

        test.log.step("11) Open the service. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("12) Check service state. ")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("13) Download the file sent in step 6. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_length))
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("rx") == file1_length)

        test.log.step("14) Close the service, change file name and open it again. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.ftp_client.dstl_set_files(test.file2_name)
        test.expect(test.ftp_client.dstl_get_service().dstl_write_files())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("15) Check service state. ")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("16) Download the file sent in step 9. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_length, repetitions=3))
        test.expect(not test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("rx") == file2_length)

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file1_name):
                test.log.warn("Problem with deleting created test file.")
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file2_name):
                test.log.warn("Problem with deleting created test file.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.log.step("17) Close and delete service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def define_and_print_ftp_profile(test, cmd, file_name):
        test.ftp_client = FtpProfile(test.dut, 0, test.cid, command=cmd, alphabet="1", host=test.ftp_ip_address,
                                     port=test.ftp_port, files=file_name,
                                     user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))

if __name__ == "__main__":
    unicorn.main()