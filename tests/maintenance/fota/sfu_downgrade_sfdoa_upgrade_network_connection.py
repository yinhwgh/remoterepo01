# responsible: kamil.kedron@globallogic.com
# location: Wroclaw

import os
import unicorn
from threading import Thread

from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_functions import dstl_enable_sms_urc
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs


class Test(BaseTest):
    """
    INTENTION
    """

    def setup(test):
        test.time_value = 25
        test.wait_time_value = 300
        test.elf = "ELS31-V_M2M-GEMALTO-VERIZON_LR4.3.3.0-35577-UE4.3.3.0.squashfs"
        test.rast = "ELS31-V_M2M-GEMALTO-VERIZON_LR4.3.3.0-35577-UE4.3.3.0.kernel.rast"
        test.sfu_sw_bootloader = "35577.*35577"
        test.sfu_path = "C:/Program Files (x86)/Sequans Communications/SFU"
        test.check_dir = "cd"
        test.sms_message = "The quick brown fox jumps over the lazy dog"
        test.ftp_server="ftp://kamilkedron:kamilkedron1qaz@147.135.208.186:50102/DAHLIA/"
        test.fota_file_1 = "ELS31-V_M2M-GEMALTO-VERIZON_LR4.3.3.0-36343-UE4.3.3.0c.sfp"
        test.fota_file_1_sw_bootloader = "36343.*36343"
        test.fota_file_2 = "ELS31-V_UE4.3.3.0fc_arn40897.sfp"
        test.fota_file_2_sw_bootloader ="36343.*40897"
        test.ffh_reset_regex= ".*Run\-only\\sDM\\ssection\\sloaded.*"


        test.set_precondition(test.dut)
        test.set_precondition(test.r1)

        test.expect(test.r1.at1.send_and_verify('AT^SCFG="URC/DstIfc","mdm"', ".*OK.*", timeout=test.time_value))

    def run(test):
        iterations=100

        test.log.step('Execute 100 iterations')
        test.dut.at2.open()

        for iteration in range(iterations+1):

            test.log.step('Loop {} START'.format(iteration+1))

            test.log.step('1. Downgrade module with sfu to 35577 DAHLIA_101-ODM_204.8C')
            test.log.info('Switch to FFH mode using AT command channel')
            test.expect(test.dut.devboard.send_and_verify("AT^MCGPIO=2,1,1", ".*OK.*", timeout=test.time_value))
            test.expect(test.dut.devboard.send_and_verify("AT^MCGPIO=2,3,1", ".*OK.*", timeout=test.time_value))
            test.expect(test.dut.at1.send_and_verify("AT+CFUN=1,1", ".*OK.*", timeout=test.time_value))
            test.sleep(60)
            test.expect(test.dut.at2.wait_for_strict(test.ffh_reset_regex), msg="Failed not occurred")
            test.run_sfu_thread()
            test.expect(test.dut.devboard.send_and_verify("AT^MCGPIO=2,1,0", ".*OK.*", timeout=test.time_value))
            test.dut.at3.send("AT^RESET", wait_after_send=40)
            test.expect(test.dut.at1.wait_for_strict("SYSSTART"), msg="Failed not occurred")
            test.expect(test.dut.at1.send_and_verify('at!="showver"', f".*{test.sfu_sw_bootloader }.*OK.*", timeout=test.time_value))

            test.log.step('2. Update with SFDOA to 36343 DAHLIA_101C-ODM_204.11B.')
            test.execute_fota(test.fota_file_1, test.fota_file_1_sw_bootloader)

            test.log.step('3. Check IMEI')
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*356278076507070.*OK.*", timeout=test.time_value))

            test.log.step('4. Update with SFDOA to 40897 DAHLIA_V_500_020j.')
            test.execute_fota(test.fota_file_2, test.fota_file_2_sw_bootloader)

            test.log.step('5. Check IMEI')
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*356278076507070.*OK.*", timeout=test.time_value))

            test.log.step('6. Log to the network')
            test.register_to_network()
            test.expect(dstl_register_to_network(test.r1))
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*356278076507070.*OK.*", timeout=test.time_value))

            test.log.step('7. Receive sms from Remote on DUT')
            test.send_sms(test.r1, test.dut)
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*356278076507070.*OK.*", timeout=test.time_value))

            test.log.step('8. Send sms from DUT to Remote')
            test.send_sms(test.dut, test.r1)
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*356278076507070.*OK.*", timeout=test.time_value))

            test.log.step('9. Execute Tcp Socket connection')
            test.tcp_socket_transparent()
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', ".*356278076507070.*OK.*", timeout=test.time_value))

            test.log.step('Loop {} END'.format(iteration + 1))

            iteration+=1

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))

    def set_precondition(test, interface):
        dstl_detect(interface)
        dstl_get_imei(interface)

    def register_to_network(test):
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=1", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*", timeout=test.time_value))
        if test.dut.at1.send_and_verify('AT+CPIN?', ".*READY.*OK.*", timeout=test.time_value):
            test.log.info("PIN entered")
        else:
            test.expect(test.dut.at1.send_and_verify('AT+CPIN="9999"', ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=,,,9", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3,"IPV4V6","we01.VZWSTATIC"', ".*OK.*", timeout=test.time_value))
        test.sleep(test.time_value)

    def tcp_socket_transparent(test):
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.ip_version = "IPv4"
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())
        test.log.step("2. Define and open TCP non-transparent server (listener) on remote.")
        socket_listener = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100)
        socket_listener.dstl_generate_address()
        test.expect(socket_listener.dstl_get_service().dstl_load_profile())
        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        r1_ip_address = socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        test.log.step("3. Define TCP non-transparent client services on DUT.")
        socket_client = SocketProfile(test.dut, "0", 3,
                                      protocol="tcp", host=r1_ip_address, port=65100)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_load_profile())
        test.log.step("Open internet connection")
        test.expect(test.dut.at1.send_and_verify("AT^SICA=1,3", ".*OK.*", timeout=test.time_value))

        test.log.step("4. Client: Open service and send data 1500x1.")
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1500))

        test.log.step("5. Close connection and delete used profiles.")
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client.dstl_get_service().dstl_reset_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.r1.at1.send_and_verify("AT+CFUN=1,1", ".*OK.*", timeout=test.time_value))
        test.expect(test.r1.at1.wait_for_strict("SYSSTART", timeout=120), msg="Failed not occurred")

    def send_sms(test, sender, receiver):
        test.expect(dstl_enable_sms_urc(receiver))
        test.log.step('Set SMS Text Mode.')
        test.expect(dstl_select_sms_message_format(receiver))
        test.expect(dstl_select_sms_message_format(sender))
        test.expect(dstl_set_preferred_sms_memory(receiver, "ME"))
        test.expect(receiver.at1.send_and_verify("AT+CMGD=1,4", ".*OK.*", timeout=test.time_value))
        test.log.step('Set Service Center Adress.')
        test.expect(dstl_set_sms_center_address(receiver))
        test.expect(dstl_set_sms_center_address(sender))
        test.log.step('Send SMS.')
        test.expect(dstl_send_sms_message(sender, receiver.sim.nat_voice_nr, test.sms_message))
        test.expect(dstl_check_urc(receiver, "CMTI", timeout=test.wait_time_value))

    def execute_sfu(test,stop):
        try:
            while True:
                os.chdir(test.sfu_path)
                test.os.execute("cd", shell=True)
                test.os.execute(f"sfu.exe {test.rast} {test.elf} 192.168.15.1 !6#473MwC --log downgradelog.txt --usb-id 1E2D 00A0 --ffh", shell=True)
                if stop():
                    break
        except BaseException as error:
            print('SFU  FAILED')

    def run_sfu_thread(test):
        stop_thread = False
        th = Thread(target=test.execute_sfu, name="SFU", args=(lambda: stop_thread, ))
        th.start()
        test.sleep(test.wait_time_value)
        stop_thread = True
        test.log.info(f'Stop Thread is: {stop_thread}')
        test.log.info(f'Thread is: {th.is_alive()}')
        test.sleep(test.time_value)
        test.os.execute("taskkill /im sfu.exe /t /f", shell=True)
        th.join()
        test.log.info(f'Thread is: {th.is_alive()}')

    def execute_fota(test, fota_file, sw_bootloader):
        test.log.step('Perform factory reset AT^SCFG="MeOpMode/Factory","all"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MeOpMode/Factory","all"', ".*OK.*", timeout=test.time_value))
        test.log.step('Update with SFDOA.')
        test.register_to_network()
        test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,3', ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify('AT+CGACT?', ".*CGACT: 3,1.*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify(f'AT^SFDOA="{test.ftp_server}{fota_file}",1,1,0', ".*SFDOA.*",
                                              timeout=test.time_value))
        test.expect(test.dut.at1.wait_for_strict('"downloading",25', timeout=900), msg="Failed not occurred")
        test.expect(test.dut.at1.wait_for_strict('"downloading",50', timeout=900), msg="Failed not occurred")
        test.expect(test.dut.at1.wait_for_strict('"downloading",75', timeout=900), msg="Failed not occurred")
        test.expect(test.dut.at1.wait_for_strict('"downloading",100', timeout=900), msg="Failed not occurred")
        if "36343.*36343" in sw_bootloader:
            test.expect(test.dut.at1.wait_for_strict("SYSSTART", timeout=900), msg="Failed not occurred")
        else:
            test.expect(test.dut.at1.wait_for_strict("FW_READY", timeout=900), msg="Failed not occurred")
            test.expect(test.dut.at1.wait_for_strict("SHUTDOWN"), msg="Failed not occurred")
            test.expect(test.dut.at1.wait_for_strict("SYSSTART"), msg="Failed not occurred")
        test.sleep(test.time_value)
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=1,1", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.wait_for_strict("SYSSTART"), msg="Failed not occurred")
        test.expect(test.dut.at1.send_and_verify('at!="showver"', f".*{sw_bootloader}.*OK.*", timeout=test.time_value))


if "__main__" == __name__:
    unicorn.main()