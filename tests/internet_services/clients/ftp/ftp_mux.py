# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0010958.001, TC0010958.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_get_siss_read_response \
    import dstl_get_siss_read_response


class Test(BaseTest):
    """
    Verify correct behaviour of FTP via Multiplexer (MUX)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.file_name = "test_file.txt"
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.data_length = 1000
        test.file_length = 2000
        test.dut.at1.close()
        test.set_mux_interface("1")
        test.log.step("1. Configure a GPRS connection profile.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid(),
                                    test_duration=1)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("2. Perform a FTP up and download on each MUX channel.")
        test.log.info("Define FTP put client profile on Module.")
        test.log.info("Execute Step 2 - Mux1")
        test.step2()

        test.log.info("Execute Step 2 - Mux2")
        test.set_mux_interface("2")
        test.step2()

        test.log.info("Execute Step 2 - Mux3")
        test.set_mux_interface("3")
        test.step2()

    def cleanup(test):
        test.log.info("Close FTP client profile.")
        test.ftp_client.dstl_get_service().dstl_close_service_profile()
        test.ftp_client.dstl_get_service().dstl_reset_service_profile()
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file_name):
                test.log.warn("Problem with deleting file from server")
        except AttributeError:
            test.log.error("Object was not created.")
        test.dut.mux_1.close()
        test.dut.mux_2.close()
        test.dut.mux_3.close()

    def define_and_print_ftp_profile(test, cmd):
        test.ftp_client = FtpProfile(test.dut, 0, test.cid, command=cmd, alphabet="1",
                                     files=test.file_name)
        test.ftp_client.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        dstl_get_siss_read_response(test.dut)

    def set_mux_interface(test, mux_interface):
        mux_interface = 'dut_mux_{}'.format(mux_interface)
        test.remap({'dut_at1': mux_interface})

    def step2(test):
        test.log.info("Define FTP put client profile on Module.")
        test.define_and_print_ftp_profile("put")

        test.log.info("Open defined FTP profile and wait for proper URC.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.info("Upload file to server (last packet with EOD flag).")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(
            test.data_length, expected="OK"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(
            test.data_length, eod_flag="1"))

        test.log.info("Check service state and Tx/Rx counters.")
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("tx") ==
            test.file_length)

        test.log.info("Close FTP client profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.info(
            "Define FTP get client profile on Module (use file uploaded in previous steps).")
        test.ftp_client.dstl_set_ftp_command("get")
        test.expect(test.ftp_client.dstl_get_service().dstl_write_cmd())
        dstl_get_siss_read_response(test.dut)

        test.log.info("Open defined FTP profile and wait for proper URC.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.info("Download file from FTP server.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_all_data(1500))

        test.log.info("Check service state and Tx/Rx counters.")
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("rx") ==
            test.file_length)

        test.log.info("Close FTP client profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())


if __name__ == "__main__":
    unicorn.main()
