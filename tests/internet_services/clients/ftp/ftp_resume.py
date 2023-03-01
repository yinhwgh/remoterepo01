#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0088070.001, TC0088070.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """ TC intention: Resume broken data transfer in uplink and downlink direction.
    In uplink direction, send data and close the connection, then send data again  with offset size to the last file.
    In downlink direction, read data but not till the end, then close the connection. Then read the rest of data with offset size. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.info("Execution of script for TC0088070.001/002 - FtpResume")
        test.log.step("1. Define and activate PDP context or define connection profile - depending on product.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid())

        test.log.step("2.1. Configure FTP put service to upload datafile ftptest.txt to the directory on FTP server.")
        test.file_name = "ftptest.txt"
        test.ftp_put = test.define_ftp_client('0', 'put')

        test.log.step("2.2. Open connection.")
        test.expect(test.ftp_put.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_put.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("2.3. Send data 6000 bytes.")
        data_packet_size = 1000
        test.expect(test.ftp_put.dstl_get_service().dstl_send_sisw_command_and_data(data_packet_size, repetitions=6))

        test.log.step("2.4. Send end of data flag.")
        test.expect(test.ftp_put.dstl_get_service().dstl_send_sisw_command(0, eod_flag='1'))

        test.log.step("2.5. Close connection.")
        test.expect(test.ftp_put.dstl_get_service().dstl_close_service_profile())

        test.log.step("3.1. Define FTP service for requesting file size ftptest.txt from last upload session.")
        test.ftp_size = test.define_ftp_client('1', 'size')

        test.log.step("3.2. Open connection.")
        test.expect(test.ftp_size.dstl_get_service().dstl_open_service_profile())

        test.log.step("3.3. Check file size and wait for finish URC.")
        test.expect(test.ftp_size.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2100', '"ftptest.txt, bytes {}"'.format(6*data_packet_size)))
        test.expect(test.ftp_size.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("3.4. Close connection.")
        test.expect(test.ftp_size.dstl_get_service().dstl_close_service_profile())

        test.log.step("4.1. Define FTP service to upload data with offset size "
                      "to the last datafile 'ftptest.txt' with offset size = 5000.")
        test.ftp_put_with_offset = test.define_ftp_client('2', 'put 5000')

        test.log.step("4.2. Open FTP session.")
        test.expect(test.ftp_put_with_offset.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_put_with_offset.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4.3. Send data 4000 bytes.")
        test.expect(test.ftp_put_with_offset.dstl_get_service().dstl_send_sisw_command_and_data(data_packet_size, repetitions=4,
                                                                                                skip_data_check=True))

        test.log.step("4.4. Send end of data flag and close the connection.")
        test.expect(test.ftp_put_with_offset.dstl_get_service().dstl_send_sisw_command(0, eod_flag='1'))
        test.expect(test.ftp_put_with_offset.dstl_get_service().dstl_close_service_profile())

        test.log.step("5.1. Define FTP service for requesting file size ftptest.txt from last upload session.")
        test.ftp_size = test.define_ftp_client('1', 'size')

        test.log.step("5.2. Open connection.")
        test.expect(test.ftp_size.dstl_get_service().dstl_open_service_profile())

        test.log.step("5.3. Check file size and wait for finish URC.")
        test.expect(test.ftp_size.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2100', '"ftptest.txt, bytes {}"'.format(9*data_packet_size)))
        test.expect(test.ftp_size.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("5.4. Close connection.")
        test.expect(test.ftp_size.dstl_get_service().dstl_close_service_profile())

        test.log.step("6.1. Configure FTP get service to download datafile ftptest.txt.")
        test.ftp_get = test.define_ftp_client('3', 'get')

        test.log.step("6.2. Open connection.")
        test.expect(test.ftp_get.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_get.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("6.3. Read data 3000 bytes.")
        test.ftp_get.dstl_get_service().dstl_read_data(data_packet_size, repetitions=3)

        test.log.step("6.4. Check state and amount of data.")
        test.expect(test.ftp_get.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.ftp_get.dstl_get_parser().dstl_get_service_data_counter('rx') == 3*data_packet_size)

        test.log.step("6.5. Close connection.")
        test.expect(test.ftp_get.dstl_get_service().dstl_close_service_profile())

        test.log.step("7.1. Configure FTP get service to download datafile ftptest.txt with offset = 3000.")
        test.ftp_get_with_offset = test.define_ftp_client('4', 'get 3000')

        test.log.step("7.2. Open connection.")
        test.expect(test.ftp_get_with_offset.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_get_with_offset.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("7.3. Read data until finish URC.")
        test.expect(test.ftp_get_with_offset.dstl_get_service().dstl_read_all_data(data_packet_size))

        test.log.step("7.4. Check state and amount of data.")
        test.expect(test.ftp_get_with_offset.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_get_with_offset.dstl_get_parser().dstl_get_service_data_counter('rx') == 6*data_packet_size)

        test.log.step("7.5. Close connection.")
        test.expect(test.ftp_get_with_offset.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")
        try:
            test.ftp_put.dstl_get_service().dstl_close_service_profile()
            test.ftp_put.dstl_get_service().dstl_reset_service_profile()
            test.ftp_size.dstl_get_service().dstl_close_service_profile()
            test.ftp_size.dstl_get_service().dstl_reset_service_profile()
            test.ftp_put_with_offset.dstl_get_service().dstl_close_service_profile()
            test.ftp_put_with_offset.dstl_get_service().dstl_reset_service_profile()
            test.ftp_get.dstl_get_service().dstl_close_service_profile()
            test.ftp_get.dstl_get_service().dstl_reset_service_profile()
            test.ftp_get_with_offset.dstl_get_service().dstl_close_service_profile()
            test.ftp_get_with_offset.dstl_get_service().dstl_reset_service_profile()
        except AttributeError:
            test.log.error("Object was not created.")

    def define_ftp_client(test, profile_id, service_type):
        ftp_client = FtpProfile(test.dut, profile_id, test.connection_setup.dstl_get_used_cid(), alphabet="1",
                                command=service_type, files=test.file_name)
        ftp_client.dstl_set_parameters_from_ip_server(ip_server=test.ftp_server)
        ftp_client.dstl_generate_address()
        test.expect(ftp_client.dstl_get_service().dstl_load_profile())
        return ftp_client


if __name__ == "__main__":
    unicorn.main()
