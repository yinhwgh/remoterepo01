# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107808.001

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
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import uc_send_healthdata
from core import dstl
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
import re

rethread = False


class Test(BaseTest):
    """
     TC0107808.001-Resmed_eHealth_UpdateApplication_NormalFlow
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        uc_init_module(test, 1)
        trigger_sms(test)

    def run(test):
        NF_pre_config(test)
        test.log.step("Resmed_eHealth_UpdateApplication_NormalFlow.")
        main_process(test)

    def cleanup(test):
        # if test.dut.software_number == "100_032":
        #     test.log.info("Start downgrade")
        #     test.expect(test.dut.at1.send_and_verify(
        #         'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.802_arn01.000.00_lynx_100_032_to_rev00.800_arn01.000.00_lynx_100_030_prod02sign.usf"'))
        #     test.expect(test.dut.at1.send_and_verify(
        #         'at^snfota="CRC","4ee9a59764736e05efa14ef24eec8573a3e126a6a46e4fac41bc83cb617ac0d4"'))
        #     test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
        #     test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
        #     test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        #     test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        #     test.sleep(5)
        #     dstl_detect(test.dut)
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

def EF_Soft_reset(test, checkstep, restart):
    if checkstep == restart:
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        main_process(test)
        return True
    else:
        return False

def trigger_sms(test):
    test.log.info('set message mode to text')
    test.expect(test.dut.dstl_select_sms_message_format(sms_format='Text'))
    test.log.info('set sms storage to ME')
    test.expect(test.dut.dstl_set_preferred_sms_memory('ME'))
    # test.log.info('get ME capacity')
    # test.capacity_sms = test.dut.dstl_get_sms_memory_capacity(1)
    test.log.info('clean up ME before test')
    test.expect(dstl_delete_all_sms_messages(test.dut))
    test.log.info('write a sms')
    test.dut.at1.send(f'AT+CMGW="{test.dut.sim.int_voice_nr}"')
    test.expect(test.dut.at1.wait_for('>'))
    test.dut.at1.send('aaaaaaaaaa\x1A')
    test.expect(test.dut.at1.wait_for('OK'))
    test.log.info('read a sms')
    test.dut.at1.send("AT+CMGR=1")
    test.expect(test.dut.at1.wait_for('OK'))
    test.log.info('delete a sms')
    test.dut.at1.send("AT+CMGD=1")
    test.expect(test.dut.at1.wait_for('OK'))
    test.log.info('send a sms')
    test.dut.at1.send(f'AT+CMGS="{test.dut.sim.int_voice_nr}"')
    test.expect(test.dut.at1.wait_for('>'))
    test.dut.at1.send('START FOTA\x1A')
    test.expect(test.dut.at1.wait_for('OK'))
    test.expect(test.dut.devboard.wait_for('>ASC0: +CMTI:'))


def dstl_delete_all_sms_messages(device):
    device.at1.send_and_verify('AT+CMGL="ALL"', '.*OK.*', timeout=120)
    smgl_index = re.findall(r"\+CMGL: (\d+),.*", device.at1.last_response)
    sms_indexes=[int(val) for val in smgl_index]
    delete_flag = True
    for sms_index in sms_indexes:
        delete_flag &= device.at1.send_and_verify('AT+CMGD={}'.format(int(sms_index)), '.*OK.*')
    if delete_flag:
        dstl.log.info('All SMS messages have been deleted from the device\'s memory - PASSED')
        return True
    else:
        dstl.log.info('All SMS messages have not been deleted from the device\'s memory - FAILED')
        return False

def main_process(test, restart=0):
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
    if EF_Soft_reset(test, 1, restart):
        return True

    test.log.step("2.  Closes the internet service profile (ID 0) and configures this service profile "
                  "as a secure TCP socket in non-transparent mode (server authentication only)")
    socket_service.dstl_set_secopt("1")
    test.expect(socket_service.dstl_get_service().dstl_write_secopt())
    if EF_Soft_reset(test, 2, restart):
        return True

    test.log.step("3. Open socket profile.")
    test.dut.at1.send_and_verify('AT^SISC=0', 'OK', handle_errors=True)
    test.sleep(5)
    if rethread and restart == 0:
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(20)
    test.expect(socket_service.dstl_get_service().dstl_open_service_profile(), critical=True)
    test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
    if EF_Soft_reset(test, 3, restart):
        return True

    test.log.step('4. Server send 1500 data ')
    test.log.info('Server send 1500 data*10 ')
    for i in range(10):
        test.ssl_server.dstl_send_data_from_ssh_server(data=server_send_data, ssh_server_property='ssh_server')
        test.sleep(1)
    if EF_Soft_reset(test, 4, restart):
        return True

    test.log.step("5. Reads the file which is about the size of 100k-2Mbyte in 1500 Byte chunks.")
    for i in range(10):
        test.expect(socket_service.dstl_get_service().dstl_read_data
                    (req_read_length=1500, repetitions=1))
        test.sleep(1)
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.UP.value)
    if EF_Soft_reset(test, 5, restart):
        return True

    test.log.step("6. Closes internet service profile after the successful download of the file.")
    test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)
    if EF_Soft_reset(test, 6, restart):
        return True

    # test.log.step("7. Configure SNFOTA feature (URL, CID, hash).")
    # test.expect(test.dut.at1.send_and_verify('at^snfota="urc",1'))
    # test.expect(test.dut.at1.send_and_verify('at^snfota="conid",{}'.format(connection_setup.dstl_get_used_cid())))
    # test.expect(test.dut.at1.send_and_verify(
    #     'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.800_arn01.000.00_lynx_100_030_to_rev00.802_arn01.000.00_lynx_100_032_prod02sign.usf"'))
    # test.expect(test.dut.at1.send_and_verify(
    #     'at^snfota="CRC","a2b1509f73318f5cb368c0555febae687c758552989d568ed54b72a78b30ff59"'))
    # if EF_Soft_reset(test, 7, restart):
    #     return True
    #
    # test.log.step("8. Trigger the download.")
    # test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
    # download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
    # if download_succeed:
    #     test.log.info("downlaod successfully")
    # else:
    #     test.expect(False, critical=True)
    # if EF_Soft_reset(test, 8, restart):
    #     return True
    #
    # test.log.step("9. Trigger the firmware swap process.")
    # test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
    # test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
    # if EF_Soft_reset(test, 9, restart):
    #     return True
    #
    # test.log.step("10. Check the module's SW version.")
    # test.sleep(5)
    # dstl_detect(test.dut)
    # test.expect(test.dut.software_number == "100_032")
    # if EF_Soft_reset(test, 10, restart):
    #     return True

    test.log.step("11. Softreset the module (AT+CFUN=1,1).")
    test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
    test.expect(test.dut.at1.wait_for('^SYSSTART'))

    test.log.step("12. Initialize the module.")
    uc_init_module(test, 1)

    test.log.step("13.  Send report to task server via IP services.")
    test.ssh_server.close()
    test.sleep(10)
    NF_pre_config(test)
    uc_send_healthdata(test, 1)


if __name__ == "__main__":
    unicorn.main()
