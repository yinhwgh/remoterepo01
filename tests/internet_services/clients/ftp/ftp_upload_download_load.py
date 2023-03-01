#responsible: michal.habrych@globallogic.com
#location: Wroclaw
#TC0107272.001

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
    To verify Module behavior during FTP load DL/UL scenario

    Description:
    1) Depends on Module:
    - Define PDP context / NV bearer and activate it using SICA command.
    - Define Connection profile using SICS command.
    2) Define FTP put client profile on Module.
    3) Open defined FTP profile and wait for proper URC.
    4) Upload a 4,5Mb file (3000 x 1500 bytes) to server (last packet with EOD flag).
    5) Check service state and Tx/Rx counters.
    6) Close FTP client profile.
    7) Define FTP get client profile on Module (use file uploaded in previous steps).
    8) Open defined FTP profile and wait for proper URC.
    9) Download file from FTP server (3000 x 1500 bytes).
    10) Check service state and Tx/Rx counters.
    11) Close FTP client profile.
    12) Define FTP del client profile on Module (use file from previous steps).
    13) Open defined FTP profile and wait for proper URC.
    14) Check service state and Tx/Rx counters.
    15) Close FTP client profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.file_name = "FTP4_5M.txt"
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        send_loops = 2999
        receive_loops = send_loops + 1
        data_length = 1500
        file_length = 4500000

        test.log.info("TC0107272.001 FtpUploadDownloadLoad")
        test.log.step("1) Depends on Module:"
                      "- Define PDP context / NV bearer and activate it using SICA command."
                      "- Define Connection profile using SICS command.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid(), test_duration=8)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("2) Define FTP put client profile on Module.")
        test.define_and_print_ftp_profile("put")

        test.log.step("3) Open defined FTP profile and wait for proper URC.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4) Upload a 4,5Mb file (3000 x 1500 bytes) to server (last packet with EOD flag).")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length,
                                                                    repetitions=send_loops, expected="OK"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, eod_flag="1"))

        test.log.step("5) Check service state and Tx/Rx counters.")
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("tx") == file_length)

        test.log.step("6) Close FTP client profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("7) Define FTP get client profile on Module (use file uploaded in previous steps).")
        test.define_and_print_ftp_profile("get")

        test.log.step("8) Open defined FTP profile and wait for proper URC.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("9) Download file from FTP server (3000 x 1500 bytes).")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_length, repetitions=receive_loops))

        test.log.step("10) Check service state and Tx/Rx counters.")
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("rx") == file_length)

        test.log.step("11) Close FTP client profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("12) Define FTP del client profile on Module (use file from previous steps)")
        test.define_and_print_ftp_profile("del")

        test.log.step("13) Open defined FTP profile and wait for proper URC.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0","2100",'"250 DELE command successful"'))

        test.log.step("14) Check service state and Tx/Rx counters.")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

    def cleanup(test):
        test.log.step("15) Close FTP client profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file_name):
                test.log.warn("Problem with deleting file from server")
        except AttributeError:
            test.log.error("Object was not created.")

    def define_and_print_ftp_profile(test, cmd):
        test.ftp_client = FtpProfile(test.dut, 0, test.cid, command=cmd, alphabet="1", files=test.file_name)
        test.ftp_client.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))

if __name__ == "__main__":
    unicorn.main()