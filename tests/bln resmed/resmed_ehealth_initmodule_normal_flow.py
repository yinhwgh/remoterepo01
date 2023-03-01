# responsible: haofeng.ding@thalesgroup.com
# location: Dalian
# TC0107803.001
# Hints:
# ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
# The SIM card should not with PIN
import unicorn
import time
import re
from core.basetest import BaseTest
import dstl.auxiliary.devboard.devboard
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from dstl.serial_interface.serial_interface_flow_control import dstl_check_flow_control_number_after_set
from dstl.serial_interface.config_baudrate import dstl_get_supported_max_baudrate, dstl_set_baudrate, \
    dstl_get_supported_baudrate_list

restart_cuunter = 1  # Restart counter to make the script stop
run_all = False  # False for normal flow,which does not need retry.
re_init = False  # if re_init is Ture,do not continue with normal flow after re-init


class Test(BaseTest):
    """
       TC0107803.001 - Resmed_eHealth_InitModule_NF
    """

    def setup(test):
        pass

    def run(test):
        uc_init_module(test, 1)

    def cleanup(test):
        pass


def uc_init_module(test, start_step, alternative_step=0):
    if start_step == 1:
        test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
        time.sleep(2)
        test.log.step('[Init][NF-01].Power on the module with a valid SIM')
        test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK')
    if start_step <= 2:
        if get_reinit_flag() is True:
            return True
        if start_step == 2:
            test.log.step('***** uc_init_module re-init flow start *****')
        if alternative_step == 2:
            test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
        test.log.step('[Init][NF-02].Power on the module via the ignition line')
        retry(test, NF_02_power_on, AF_A_HW_restart, 1)
        # time.sleep(2)
        test.log.step('[Init][NF-03].Waits for V180==1 up to 14s')
    if start_step <= 4:
        if get_reinit_flag() is True:
            return True
        if alternative_step == 4:
            test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
        test.log.step('[Init][NF-04].Waits for ^SYSSTART up to 14s')
        retry(test, NF_04_wait_for_sysstart, AF_A_HW_restart, 1)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 5:
            toggle_off_rts(test)
        time.sleep(10)
        test.log.step('[Init][NF-05].Check the AT command communication with the module')
        retry(test, NF_05_check_at_command, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 6:
            toggle_off_rts(test)
        test.log.step('[Init][NF-06].Disable AT command echo mode (ATE0)')
        retry(test, NF_06_disable_at_echo_mode, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 7:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-07]: request module version (AT+CMI, AT+GMM, AT+CMR, ATI1)')
        retry(test, NF_07_request_module_version, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 8:
            toggle_off_rts(test)
        test.log.step(
            '[Init]:[NF-08]: Enables HW flow control (AT\Q3) Error result code (numeric) Automatic response to Network requests (ATS0)')
        retry(test, NF_08_enable_flowcontrol_errorcode, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 9:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-09]: Requests IMEI (AT+CGSN)')
        retry(test, NF_09_request_imei, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 10:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-10]: Requests IMEI (AT+CGSN)')
        retry(test, NF_10_enable_full_function, AF_B_SW_restart, 3)
    if start_step <= 11:
        if get_reinit_flag() is True:
            return True
        if alternative_step == 11:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-11]: Requests USIM ID (AT+CCID)')
        retry(test, NF_11_request_usim_id, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 12:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-12]: Forbids cell broadcast messages (AT+CSCB=1,"","")')
        retry(test, NF_12_forbids_cell_broadcast_message, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 13:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-13]: Requests Model identification (AT+CGMM) SIM PIN status (AT+CPIN?)IMSI (AT+CIMI)')
        retry(test, NF_13_request_id_sim_status, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 14:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-14]: Enable URC and auto attach')
        retry(test, NF_14_enable_urc, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 15:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-15]: Setup the network')
        retry(test, NF_15_setup_network, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 16:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-16]: Configure SMS format, enable URC and detailed header information')
        retry(test, NF_16_setup_short_message, AF_B_SW_restart, 3)
        if get_reinit_flag() is True:
            return True
        if alternative_step == 17:
            toggle_off_rts(test)
        test.log.step('[Init]:[NF-17]: check the network registration')
        retry(test, NF_17_check_network_registration, AF_B_SW_restart, 3)
        test.log.step('[Init]:Init or re-init end')
        if run_all is True:
            set_reinit_flag(True)
    return True


def set_run_all(value):
    global run_all
    run_all = value
    return True


def get_run_all():
    return run_all


def set_reinit_flag(value):
    global re_init
    re_init = value
    return


def get_reinit_flag():
    return re_init


def retry(test, fun_name, error_handling, retry_counter):
    if run_all is False:
        return fun_name(test)
    while (retry_counter > 0):
        if fun_name(test) is True:
            return True
        else:
            retry_counter = retry_counter - 1
    test.log.step('Retry failed,start to re-init')
    toggle_on_rts(test)
    test.expect(error_handling(test))
    return False


def NF_02_power_on(test):
    return test.expect(test.dut.devboard.send_and_verify('MC:igt=1100', 'OK'))


def NF_04_wait_for_sysstart(test):
    return test.expect(test.dut.at1.wait_for('^SYSSTART', 64))


def NF_05_check_at_command(test):
    return test.expect(test.dut.at1.send_and_verify("AT", 'OK\r\n', timeout=5, handle_errors=True))


def NF_06_disable_at_echo_mode(test):
    return test.expect(test.dut.at1.send_and_verify("ATE0", 'OK\r\n', timeout=5, handle_errors=True))


def NF_07_request_module_version(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CGMI", 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+GMM", 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify("ATI1", 'OK\r\n', timeout=5, handle_errors=True))
    return result


def NF_08_enable_flowcontrol_errorcode(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT\Q3", 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", 'OK\r\n', timeout=5, handle_errors=True))
    time.sleep(2)
    result = result & test.expect(test.dut.at1.send_and_verify("ATS0=0", 'OK\r\n', timeout=5, handle_errors=True))
    return result


def NF_09_request_imei(test):
    return test.expect(test.dut.at1.send_and_verify('AT+CGSN', 'OK\r\n', timeout=5, handle_errors=True))


def NF_10_enable_full_function(test):
    return test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', 'OK\r\n', timeout=5, handle_errors=True))


def NF_11_request_usim_id(test):
    return test.expect(test.dut.at1.send_and_verify('AT+CCID', 'OK\r\n', timeout=5, handle_errors=True))


def NF_12_forbids_cell_broadcast_message(test):
    return test.expect(test.dut.at1.send_and_verify('AT+CSCB=1,"",""', 'OK\r\n', timeout=5, handle_errors=True))


def NF_13_request_id_sim_status(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CGMM', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CIMI', 'OK\r\n', timeout=5, handle_errors=True))
    return result


def NF_14_enable_urc(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CREG=2', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CGEREP=2', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR","std"', 'OK\r\n', timeout=5, handle_errors=True))
    # result = result & test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/Fso","1"', 'OK\r\n'))
    return result


def NF_15_setup_network(test):
    result = True
    # result = result & test.expect(test.dut.at1.send_and_verify('AT^SXRAT=4,3', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","","",0,0', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+COPS?', 'OK\r\n', timeout=5, handle_errors=True))
    # AT+COPS=3,2
    return result


def NF_16_setup_short_message(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CSDH=1', 'OK\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT+CMGL="ALL"', 'OK\r\n', timeout=5, handle_errors=True))
    return result


def NF_17_check_network_registration(test):
    # return test.expect(test.dut.at1.send_and_verify('AT+COPS?', 'OK\r\n', timeout=5, handle_errors=True))

    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT+COPS?', 'OK\r\n', timeout = 5, handle_errors = True))
    result = result & test.expect(test.dut.at1.send_and_verify('AT+CCLK?', 'OK\r\n', timeout = 5, handle_errors = True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SIND="is_cert",1', 'OK\r\n', timeout = 5, handle_errors = True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SSECUA="CertStore/TLS/PreconfigureCert",,1', 'OK\r\n', timeout = 5,
                                     handle_errors = True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SSECUA="CertStore/TLS/PreconfigureCert",,2', 'OK\r\n', timeout = 5,
                                     handle_errors = True))
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SSECUA="CertStore/TLS/PreconfigureCert",,3', 'OK\r\n', timeout = 5,
                                     handle_errors = True))
    return result


def AF_Soft_reset(test):
    return test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK\r\n'))


def AF_enter_flight_mode(test):
    return test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', 'OK\r\n'))


def AF_A_HW_restart(test):
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
    test.log.step("*****Re-init module *****")
    test.expect(uc_init_module(test, 2))
    return True


def AF_B_SW_restart(test):
    global restart_cuunter
    if restart_cuunter >= 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK')
    test.dut.devboard.send_and_verify('MC:igt=1100', 'OK')
    time.sleep(14)
    test.log.step("*****Soft reset the module *****")
    retry(test, AF_Soft_reset, AF_A_HW_restart, 1)
    test.log.step("*****Re-init module *****")
    test.expect(uc_init_module(test, 4))
    return True


def AF_C_Flight_Mode_reset(test):
    test.log.step("*****set to flight mode *****")
    retry(test, AF_enter_flight_mode, AF_B_SW_restart, 1)
    time.sleep(5)
    test.log.step("*****Re-init module *****")
    test.expect(uc_init_module(test, 11))
    return True


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
