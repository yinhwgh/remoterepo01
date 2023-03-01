# responsible: haofeng.dding@thalesgroup.com
# location: Dalian
# TC0108046.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import ebs_alarmdevice_checknetwork_nf
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile

restart_cuunter = 1
re_init = False
run_all = False  # False for normal flow,which does not need retry.
senddata = "!@#$%^&*()1234567890abcdefghijklmnopqrstuvwxyz!@#$%^&*("


class Test(BaseTest):
    def setup(test):
        test.dut.devboard.send('mc:gpiocfg=3,outp')
        test.sleep(0.3)
        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(2)

    def run(test):
        main_process(test)

    def cleanup(test):
        pass


def ebs_sendheartbeat(test, start_step, alternative_step=0):
    if alternative_step == 1:
        toggle_off_rts(test)
    test.log.step('[SendAlarm][NF-01]Check service status')
    if start_step == 2:
        retry(test, NF_01_check_service_status, EF_C, 1)
    else:
        retry(test, NF_01_check_service_status, EF_B, 3)
    if alternative_step == 2:
        toggle_off_rts(test)
    test.log.step('[SendAlarm][NF-02]Send heart beat')
    retry(test, NF_02_send_heart_beat, EF_B, 3)
    if alternative_step == 3:
        toggle_off_rts(test)
    test.log.step('[SendAlarm][NF-03]Check if heartbeat was acknowledged')
    if start_step == 2:
        retry(test, NF_03_check_if_heartbeat_was_acknowledged, EF_D, 1)
    else:
        retry(test, NF_03_check_if_heartbeat_was_acknowledged, EF_B, 3)
    if alternative_step == 4:
        toggle_off_rts(test)
    test.log.step('[SendAlarm][NF-04]Go to Check network step 81Check service status')
    retry(test, NF_04_go_to_networkcheck, EF_B, 3)
    return True


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


def NF_01_check_service_status(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SISI=1', 'OK', timeout=5, handle_errors=True))


def NF_02_send_heart_beat(test):
    result = True
    result = result & test.expect(
        test.dut.at1.send_and_verify('AT^SISW=1,55', '^SISW: 1,55,0\r\n', timeout=5, handle_errors=True))
    result = result & test.expect(test.dut.at1.send_and_verify(senddata, 'OK', timeout=5, handle_errors=True))
    return result


def NF_03_check_if_heartbeat_was_acknowledged(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SISW=1,0', 'OK', timeout=5, handle_errors=True))


def NF_04_go_to_networkcheck(test):
    return test.expect(ebs_check_network(test, 81))


def EF_A(test):
    toggle_on_rts(test)
    global restart_cuunter
    test.log.info('restart_counter is {}'.format(str(restart_cuunter)))
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.log.step("*****Shut down module *****")
    test.dut.devboard.send('mc:gpio3=0')
    test.expect(ebs_check_network(test, 2))
    return True


def EF_B(test):
    toggle_on_rts(test)
    global restart_cuunter
    test.log.info('restart_counter is {}'.format(str(restart_cuunter)))
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.log.step("*****Shut down module *****")
    test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK')
    test.expect(ebs_check_network(test, 2))
    return True


def EF_C(test):
    toggle_on_rts(test)
    global restart_cuunter
    test.log.info('restart_counter is {}'.format(str(restart_cuunter)))
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.log.step("*****De-register *****")
    test.dut.at1.send_and_verify('AT^SISC=1', 'OK')
    test.dut.at1.send_and_verify('AT^SISC=9', 'OK')
    test.dut.at1.send_and_verify('AT+COPS=2', 'OK')
    test.log.step("*****Register *****")
    test.sleep(2)
    test.dut.at1.send_and_verify('AT+COPS=0', 'OK')
    test.expect(ebs_check_network(test, 2))
    return True


def EF_D(test):
    toggle_on_rts(test)
    global restart_cuunter
    test.log.info('restart_counter is {}'.format(str(restart_cuunter)))
    if restart_cuunter == 10:
        test.log.error('restart 10 times,please check.')
        set_reinit_flag(True)
        return True
    restart_cuunter = restart_cuunter + 1
    test.log.step("*****De-register *****")
    test.dut.at1.send_and_verify('AT^SISC=1', 'OK')
    test.dut.at1.send_and_verify('AT^SISC=9', 'OK')
    test.dut.at1.send_and_verify('AT+COPS=2', 'OK')
    test.log.step("*****Register *****")
    test.sleep(2)
    test.dut.at1.send_and_verify('AT+COPS=0', 'OK')
    test.expect(ebs_check_network(test, 57))
    return True


def toggle_off_rts(test):
    test.dut.at1.connection.setRTS(False)
    test.sleep(1)
    test.log.h3(f"RTS line state: {test.dut.at1.connection.rts}")


def toggle_on_rts(test):
    test.dut.at1.connection.setRTS(True)
    test.sleep(1)
    test.log.h3(f"RTS line state: {test.dut.at1.connection.rts}")


def set_reinit_flag(value):
    global re_init
    re_init = value
    return


def get_reinit_flag():
    return re_init


def set_run_all(value):
    global run_all
    run_all = value
    return True


def get_run_all():
    return run_all


def ebs_check_network(test, start_step, alternative_step=0):
    if start_step == 1:
        test.log.step("1. Application and the module power up & 2. Power on the module via the ignition line.")
        test.dut.at1.send_and_verify("AT^SMSO", ".*OK.*")
        test.dut.devboard.send_and_verify("mc:vbatt=off", ".*OK.*")
        test.sleep(2)
        test.dut.devboard.send_and_verify("mc:vbatt=on", ".*OK.*")
        test.sleep(2)
    if start_step <= 2:
        if start_step == 2:
            test.log.step('***** ebs check network re-init flow start *****')
        if alternative_step == 2:
            test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
        test.dut.devboard.send_and_verify("mc:igt=1000", ".*OK.*")
        test.log.step("3. Waits for ^SYSSTART about 30s.")
        test.dut.at1.wait_for('SYSSTART', 30)
    if start_step <= 4:
        if start_step == 4:
            test.log.step('***** ebs check network re-init flow start *****')
        if alternative_step == 4:
            test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
        test.log.step("4. Check the AT command communication with the module. Send AT and expect return OK.")
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
        test.log.step("5. Set baudrate, IPR is 230400.")
        test.dut.at1.send_and_verify("at+ipr={}".format(230400), "OK", timeout=10)
        test.dut.at1.reconfigure({"baudrate": 230400})
        test.sleep(5)
        test.log.step("6. Set echo, ATE0 and expect return OK.")
        test.expect(test.dut.at1.send_and_verify("ATE0", ".*OK.*"))
        test.log.step("7. Set error messages format with AT+CMEE=1.")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
        test.log.step("8. Activate registration URCs with AT+CREG=2.")
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2", ".*OK.*"))
        test.log.step("9. Check module model with AT+CGMM.")
        test.expect(test.dut.at1.send_and_verify("AT+CGMM", ".*OK.*"))
        test.log.step("10. Disable AutoAttach")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=GPRS/AutoAttach,disabled", ".*OK.*"))
        test.log.step("11. Set serial port hardware flow control with AT\Q3.")
        test.expect(test.dut.at1.send_and_verify("AT\Q3", ".*OK.*"))
        test.log.step("12. Activate radio state URC, AT^SIND=lsta,1,0.")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=lsta,1,0", ".*OK.*"))
        test.log.step("13. Activate service state URC.")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=service,1", ".*OK.*"))
        test.log.step("15. Activate SMS full storage URC")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=smsfull,1", ".*OK.*"))
        test.log.step("16. Activate SIM data activity URC.")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=simdata,1", ".*OK.*"))
        test.log.step("17. Activate extended incoming call indication format.")
        test.expect(test.dut.at1.send_and_verify("AT+CRC=1", ".*OK.*"))
        test.log.step("18. Activate CLIP.")
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1", ".*OK.*"))
        test.log.step("19. Set RING functionality.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RingOnData","on"', ".*OK.*"))
        test.log.step("20. Set ports (other module option).")
        test.expect(test.dut.at1.send_and_verify("AT^SSET=1", ".*OK.*"))
        test.log.step("21. Disable power save on serial.")
        test.expect(test.dut.at1.send_and_verify("AT^SPOW=1,0,0", ".*OK.*"))
        test.log.step("22. Check module connection.")
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
        test.log.step("23. Set clock initial time..")
        test.expect(test.dut.at1.send_and_verify('AT+CCLK="00/01/01,00:00:57+32"', ".*OK.*"))
        test.log.step("24. Check technology setting..")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*OK.*"))
        test.log.step("25. Set technology according to application setup.")
        # test.expect(test.dut.at1.send_and_verify("AT^SXRAT=1,2", ".*OK.*"))
        test.log.step("26. Set GPIO8 to FNS to control selected SIM interface.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","std"', ".*OK.*"))
        test.log.step("27. Activate second SIM interface.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode","1"', ".*OK.*"))
        test.log.step("28. Set dual SIM option.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode/Dreg","on"', ".*OK.*"))
        test.log.step("29. Check enabled SIM.")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1,0,0,1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="SM","ME","SM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AAT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=3,0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CLIP=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGMM', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCLK?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGATT=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
        # 小机站增加 by yinhw
        test.dut.at1.wait_for('CREG: 5', timeout=150)
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","on"', ".*OK.*"))
        # test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","3"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,IPV6', ".*OK.*"))
        # test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,IPV6,"internetipv6"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,IPV4V6,"radius"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=2,1,"gemalto","gemalto"', ".*OK.*"))
    if start_step <= 57:
        if start_step == 57:
            test.log.step('***** ebs check network re-init flow start *****')
        if alternative_step == 57:
            test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=9,srvType,"Socket"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=9,alphabet,1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=9,conId,2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=9,address,"socktcp://listener:54321"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISO=9', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
        # test.expect(test.dut.at1.send_and_verify('AT^SICI=0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISC=9', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=242', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGL=4', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGL=1', ".*OK.*"))
        test.sleep(10)
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.socket = SocketProfile(test.dut, "1", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                    host="client", localport=65100)
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,srvType,Socket', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,conId,2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,tcpMR,10', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,tcpOT,6000', ".*OK.*"))
        # test.expect(test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://dev10.aplnet.dynv6.net:6650"', ".*OK.*"))
        # test.expect(test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://[2001:470:18:36b::2]:50025"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,alphabet,1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://114.55.6.216:50000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISO=1', ".*OK.*"))
        test.sleep(20)
        test.expect(test.dut.at1.send_and_verify('AT^SISI=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISE=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISI=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,0', ".*OK.*"))
        test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(511))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT^SISR=1,511', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
    if start_step <= 81:
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=242', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGL=4', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SMONI', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISR=1,511', ".*OK.*"))
    return True


def main_process(test):
    ebs_check_network(test, 1)
    ebs_sendheartbeat(test, 1)
    test.expect(test.dut.at1.send_and_verify('AT^SISC=1', ".*OK.*"))
    test.dut.at1.send_and_verify("at+ipr={}".format(115200), "OK", timeout=10)
    test.dut.at1.reconfigure({"baudrate": 115200})
    test.dut.at1.send_and_verify('at^scfg="GPRS/AutoAttach","enabled"', ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
