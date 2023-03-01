# responsible: haofeng.ding@thalesgroup.com
# location: Dalian
# TC0107805.001
# Hints:
# ntp_address should be defined in local.cfg currently,such as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
# The SIM card should not with PIN
import unicorn
import time
import re
from core.basetest import BaseTest
import dstl.auxiliary.devboard.devboard
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from dstl.serial_interface.serial_interface_flow_control import dstl_check_flow_control_number_after_set
from dstl.serial_interface.config_baudrate import dstl_get_supported_max_baudrate, dstl_set_baudrate, dstl_get_supported_baudrate_list
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from tests.rq6 import resmed_ehealth_initmodule_normal_flow

send_data = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()abcdefghijklmnopqrstuvwxyz1"
restart_cuunter = 1 #Restart counter to make the script stop
run_all = False #False for normal flow,which does not need retry.
re_init = False #if re_init is Ture,do not continue with normal flow after re-init


class Test(BaseTest):
    def setup(test):
        test.log.step('Init the module first')
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def run(test):
        NF_pre_config(test)
        uc_send_healthdata(test, 1)

    def cleanup(test):
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


def uc_send_healthdata(test, start_step, alternative_step=0):
    # NF_pre_config(test)
    if start_step == 1:
        if get_reinit_flag() is True:
            return True
        # if alternative_step == 1:
        #      toggle_off_rts(test)
        test.log.step('[SendHealthData][NF-01]Configures the IP service connection profile 0 with an inactive timeout set to 90 seconds and a private APN using AT^SICS.')
        retry(test, NF_01_config_ip_servive_connection_sics, EF_A_reboot_module, 3, alternative_step)
    if start_step <= 2:
        if get_reinit_flag() is True:
            return True
        # if alternative_step == 2:
        #     toggle_off_rts(test)
        test.log.step('[SendHealthData][NF-02]closes the internet service profile (ID 0) and configures this service profile as a secure TCP socket in non-transparent mode (server authentication only).')
        retry(test, NF_02_config_ip_servive_connection_siss, EF_A_reboot_module, 3, alternative_step)
    if start_step <= 3:
        if get_reinit_flag() is True:
            return True
        # if alternative_step == 3:
        #     toggle_off_rts(test)
        test.log.step('[SendHealthData][NF-03]opens the internet service and waits for SISW URC.')
        retry(test, NF_03_open_internet_service, EF_A_reboot_module, 3, alternative_step)
        if get_reinit_flag() is True:
            return True
        # if alternative_step == 4:
        #     toggle_off_rts(test)
        test.log.step('[SendHealthData][NF-04]sends health data (~100k-1MByte) to the receiving server in 1500Bytes chunks and checks the connection status with AT^SISI=0 in between.')
        retry(test, NF_04_send_health_data, EF_A_reboot_module, 3, alternative_step)
        if get_reinit_flag() is True:
            return True
        # if alternative_step == 5:
        #     toggle_off_rts(test)
        test.log.step('[SendHealthData][NF-05]closes the internet service profile.')
        retry(test, NF_05_close_internet_service, EF_A_reboot_module, 3, alternative_step)
        if run_all is True:
            set_reinit_flag(True)
    return True

def NF_pre_config(test):
    result = True
    test.cipher = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    # test.cipher = "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384"
    test.log.step("1. Run OpenSSL server with one cipher suite supported by module: {}.".
                  format(test.cipher))

    test.ssl_server = SslServer("IPv4", "socket_tls", test.cipher)
    test.ip_address = test.ssl_server.dstl_get_server_ip_address()
    test.port_number = test.ssl_server.port_number
    ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
    test.sleep(5)

    test.log.step("2. Load client certificate and server public certificate "
                  "(micCert.der) on module.")
    test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                            dstl_get_openssl_configuration_number())
    if test.certificates.dstl_count_uploaded_certificates() > 0:
        test.certificates.dstl_delete_all_uploaded_certificates()
    test.certificates.dstl_upload_openssl_certificates()

    test.log.step("3. Check if certificates are installed.")
    test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                msg="Wrong amount of certificates installed")

    test.log.step("4. Set Real Time Clock to current time.")
    test.expect(dstl_set_real_time_clock(test.dut))
    return result

def NF_01_config_ip_servive_connection_sics(test, alternative_step):
    if alternative_step == 1:
        return False
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","internet4g.gdsp"', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK\r\n', timeout=5, handle_errors=True))
    #result = result & test.expect(test.dut.at1.send_and_verify('AT^SICS=0,"inactTO","90"', 'OK\r\n', timeout=5, handle_errors=True))
    return result

def NF_02_config_ip_servive_connection_siss(test, alternative_step):
    if alternative_step == 2:
        return False
    result = True
    if test.dut.at1.send_and_verify('AT^SISI=0', 'OK\r\n', timeout=5, handle_errors=True):
        result = result & test.expect(test.dut.at1.send_and_verify('AT^SISC=0', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"srvType","socket"', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"conId","1"', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SISS=0,"tcpOT",90', 'OK\r\n', timeout=5, handle_errors=True))
    # global ip_address, port_number
    result = result & test.expect(test.dut.at1.send_and_verify(f'AT^SISS=0,"address","socktcps://{test.ip_address}:{test.port_number}"', 'OK\r\n', timeout=5, handle_errors=True))
    return result

def NF_03_open_internet_service(test, alternative_step):
    if alternative_step == 3:
        return False
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SISO=0', 'SISW', wait_for='SISW', handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SMONI', 'OK\r\n', timeout=5, handle_errors=True))
    return result

def NF_04_send_health_data(test, alternative_step):
    if alternative_step == 4:
        if test.dut.at1.send_and_verify('AT^SISI=0', 'SISI: 0,4', timeout=5, handle_errors=True):
            test.dut.at1.send_and_verify('AT^SISC=0', 'OK\r\n', timeout=5, handle_errors=True)
            test.ssh_server.close()
            test.sleep(10)
            NF_pre_config(test)
        return False
    result = True
    for i in range(10):
        result = result & test.expect(test.dut.at1.send_and_verify('AT^SISW=0,1500', '^SISW: 0,1500,0\r\n', timeout=5, handle_errors=True))
        result = result & test.expect(test.dut.at1.send_and_verify(send_data, 'OK\r\n', timeout=5, handle_errors=True))
        test.sleep(1)
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SISI=0', 'OK\r\n', timeout=5, handle_errors=True))
    return result

def NF_05_close_internet_service(test, alternative_step):
    if alternative_step == 5:
        if test.dut.at1.send_and_verify('AT^SISI=0', 'SISI: 0,4', timeout=5, handle_errors=True):
            test.dut.at1.send_and_verify('AT^SISC=0', 'OK\r\n', timeout=5, handle_errors=True)
            test.ssh_server.close()
            test.sleep(10)
            NF_pre_config(test)
        return False
    return test.expect(test.dut.at1.send_and_verify('AT^SISC=0', 'OK\r\n', timeout=5, handle_errors=True))

def EF_Soft_reset(test, alternative_step):
    return test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK\r\n'))

def EF_B_HW_restart(test):
    global restart_cuunter
    test.log.info('restart_counter is {}'.format(str(restart_cuunter)))
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.log.step("[precondition] restore")
    test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK')
    test.dut.devboard.send_and_verify('MC:igt=1100', 'OK')
    time.sleep(14)
    test.log.step("*****Shut down module *****")
    test.dut.at1.send("AT^SMSO=fast")
    test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
    time.sleep(5)
    test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK')
    # added by yhw --start--
    test.dut.devboard.send_and_verify('MC:igt=1100', 'OK')
    time.sleep(30)
    # --end--
    test.log.step("*****Re-init module *****")
    #test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 2))
    test.expect(uc_send_healthdata(test, 1))
    return True

def EF_A_reboot_module(test):
    global restart_cuunter
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK')
    test.dut.devboard.send_and_verify('MC:igt=1100', 'OK')
    time.sleep(14)
    test.log.step("*****Soft reset the module *****")
    retry(test, EF_Soft_reset, EF_B_HW_restart, 3)
    time.sleep(34)
    test.log.step("*****Re-init module *****")
    #test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 4))
    test.expect(uc_send_healthdata(test, 1))
    return True


def retry(test, fun_name, error_handling, retry_counter, alternative_step=0):
    print('-----------------', alternative_step, '--------------------')
    if run_all is False:
        return fun_name(test, alternative_step)
    while (retry_counter > 0):
        if fun_name(test, alternative_step) is True:
            return True
        else:
            retry_counter = retry_counter - 1
    test.log.step('Retry failed,start to re-init')
    toggle_on_rts(test)
    test.expect(error_handling(test))
    return False

def set_run_all(value):
    global run_all
    run_all = value
    return

def get_run_all():
    return run_all

def set_reinit_flag(value):
    global re_init
    re_init = value
    return

def get_reinit_flag():
    return re_init

def toggle_off_rts(test):
    test.dut.at1.connection.setRTS(False)
    test.sleep(1)
    test.log.h3(f"RTS line state: {test.dut.at1.connection.rts}")

def toggle_on_rts(test):
    test.dut.at1.connection.setRTS(True)
    test.sleep(1)
    test.log.h3(f"RTS line state: {test.dut.at1.connection.rts}")

if "__main__" == __name__:
    unicorn.main()