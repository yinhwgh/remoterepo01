# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107853.001

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import NF_pre_config
from core import dstl
import random


class Test(BaseTest):
    """
     TC0107853.001-Resmed_eHealth_UpdateModule_Robustness_Test_EF_B1
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "GPIO/mode/FSR",std', 'OK'))
        uc_init_module(test, 1)

    def run(test):
        NF_pre_config(test)
        main_process(test)

        test.sleep(random.randint(15, 30))
        test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK', wait_after_send=3))
        test.log.info("fast shutdown pulled to GND for 20ms")
        test.dut.devboard.send('mc:gpio3cfg=1')
        test.dut.devboard.send('mc:gpio3cfg=0')
        test.sleep(2)  # can not ignition after 20ms
        test.dut.devboard.send_and_verify('mc:igt=1000', 'OK')
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        test.ssh_server.close()
        test.sleep(10)
        test.log.step("Initialize the module.")
        uc_init_module(test, 1)

        NF_pre_config(test)
        main_process(test)
        download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=100)
        if download_succeed:
            test.log.info("downlaod successfully")
        else:
            test.expect(False, critical=True)

        test.log.step("10. Trigger the firmware swap process.")
        test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        test.log.step("11. Check the module's SW version.")
        dstl_detect(test.dut)
        test.expect(test.dut.software_number == "100_028T")

    def cleanup(test):
        if test.dut.software_number == "100_028T":
            test.log.info("Start downgrade")
            test.expect(test.dut.at1.send_and_verify(
                'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.038T_arn01.000.00_lynx_100_028T_to_rev00.038_arn01.000.00_lynx_100_028_prod02sign.usf"'))
            test.expect(test.dut.at1.send_and_verify(
                'at^snfota="CRC","c4ec70b56e7393a13435730c18ad73edcacdfb716d3e72f0d6b6bfa94530fbf0"'))
            test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
            test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=100)
            test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
            test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
            dstl_detect(test.dut)
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


def main_process(test):
    test.log.step("1. Configures the IP service connection profile 0 "
                  "with an inactive timeout set to 90 seconds and a private APN using AT^SICS.")
    server_send_data = dstl_generate_data(1500)
    connection_setup = dstl_get_connection_setup_object(test.dut)
    test.expect(connection_setup.dstl_load_internet_connection_profile())
    test.expect(connection_setup.dstl_activate_internet_connection(),
                msg="Could not activate PDP context")
    socket_service = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                   host=test.ip_address,
                                   port=test.port_number,
                                   protocol="tcp", secure_connection=True, tcp_ot="90")
    socket_service.dstl_generate_address()
    test.expect(socket_service.dstl_get_service().dstl_load_profile())

    test.log.step("2.  configures this service profile as a secure TCP socket in non-transparent mode (server authentication only)")
    socket_service.dstl_set_secopt("1")
    test.expect(socket_service.dstl_get_service().dstl_write_secopt())

    test.log.step("3.  closes the internet service profile (ID 0)")
    test.dut.at1.send_and_verify('AT^SISC=0', 'OK', handle_errors=True)
    test.sleep(5)

    test.log.step("4. Open socket profile.")
    test.expect(socket_service.dstl_get_service().dstl_open_service_profile(), critical=True)
    test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

    test.log.step('5. Server send 1500 data ')
    test.log.info('Server send 1500 data*10 ')
    for i in range(10):
        test.ssl_server.dstl_send_data_from_ssh_server(data=server_send_data, ssh_server_property='ssh_server')
        test.sleep(1)

    test.log.step("6. Reads the file which is about the size of 100k-2Mbyte in 1500 Byte chunks.")
    for i in range(10):
        test.expect(socket_service.dstl_get_service().dstl_read_data
                    (req_read_length=1500, repetitions=1))
        test.sleep(1)
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.UP.value)

    test.log.step("7. Closes internet service profile after the successful download of the file.")
    test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)

    test.log.step("8. Configure SNFOTA feature (URL, CID, hash).")
    test.expect(test.dut.at1.send_and_verify('at^snfota="urc",1'))
    test.expect(test.dut.at1.send_and_verify('at^snfota="conid",{}'.format(connection_setup.dstl_get_used_cid())))
    test.expect(test.dut.at1.send_and_verify(
        'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.038_arn01.000.00_lynx_100_028_to_rev00.038T_arn01.000.00_lynx_100_028T_prod02sign.usf"'))
    test.expect(test.dut.at1.send_and_verify(
        'at^snfota="CRC","19de9dd031fb028f192f5358afc53461104a51a413132b9c6582dbcf6f950ecb"'))

    test.log.step("9. Trigger the download.")
    test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))


if __name__ == "__main__":
    unicorn.main()
