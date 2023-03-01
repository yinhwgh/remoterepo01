#responsible: feng.han@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0095168.001, TC0095168.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import check_urc
from dstl.sms import sms_functions
from dstl.sms import sms_center_address
from dstl.sms import select_sms_format
from dstl.network_service import network_monitor
from dstl.call import setup_voice_call
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.configuration import set_autoattach
from dstl.sms import delete_sms

import re

class Test(BaseTest):
    """
        TC0095168.001, TC0095168.002 - LTEvoiceCallCSFBfunction
        """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.log.info("For RMNET connection setup actsrvset to 11 and restart to make it take effect.")
        test.expect(test.dut.at1.send_and_verify('AT^SSRVSET=actsrvset,11', expect='OK'))
        test.expect(test.dut.dstl_enable_ps_autoattach())
        test.expect(test.dut.dstl_restart())
        test.echo_server = EchoServer(ip_version="IPv4", protocol="TCP")
        test.cid = "1"

    def run(test):
        test.log.info("Prepare network configurations before registering to LTE.")
        test.internet_connection_dut = dstl_get_connection_setup_object(test.dut, ip_version='IP', ip_public=False)
        test.internet_connection_dut.cgdcont_parameters['cid'] = test.cid
        test.internet_connection_dut.dstl_define_pdp_context()
        test.socket_client = SocketProfile(test.dut, "1", test.cid,
                                      protocol="tcp", etx_char=26)
        test.socket_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())
        test.internet_connection_dut.dstl_activate_internet_connection()

        test.log.step("1. Enable +CREG=2 to see if the CSFB is working")
        test.dut.dstl_register_to_network()
        test.log.info("Wait for some time for network stable.")
        test.sleep(20)
        registered_to_lte = test.dut.at1.send_and_verify("AT+COPS?", ",7\s+OK")
        test.expect(registered_to_lte, msg="Fail to register to LTE network, stop tests.", critical=True)

        test.log.info("VOLTE should be disabled.")
        test.dut.at1.send_and_verify("AT+CAVIMS?", "OK")
        if 'CAVIMS: 1' in test.dut.at1.last_response:
            test.log.info("VOLTE is enabled now but it should be disabled before tests.")
            test.log.info("Disable VOLTE by setting AT+CVMOD to CS only.")
            test.dut.at1.send_and_verify("AT+CVMOD=0", "OK")

        test.log.info("Clear SMS from memory.")
        test.dut.dstl_delete_all_sms_messages()

        for i in range(1, 3):
            if i == 1:
                test.log.step(f"2.{i}. Perform MO call.")
                test.log.step(f"2.{i}.1 Setup MO call from dut.")
                mo_port = test.dut.at1
                mt_port = test.r1.at1
                is_mo = True
                dial_number = test.r1.sim.nat_voice_nr
            else:
                test.log.step(f"2.{i}. Perform MT call.")
                test.log.step(f"2.{i}.1 Setup MO call from Remote.")
                mt_port = test.dut.at1
                mo_port = test.r1.at1
                is_mo = False
                dial_number = test.dut.sim.nat_voice_nr

            test.expect(test.dut.dstl_monitor_network_act() == '4G')
            test.expect(mo_port.send_and_verify(f"ATD{dial_number};", "OK"))
            test.expect(mt_port.wait_for("RING"))

            test.log.step(f"2.{i}.2. After ATD***; the module shall switch to 3G or 2G.")
            test.expect(test.dut.dstl_monitor_network_act() in ('2G','3G'))

            test.log.step(f"2.{i}.3. Answering the call module should keep in 3G or 2G.")
            test.expect(mt_port.send_and_verify("ATA", "OK"))
            test.sleep(2)
            test.expect(test.dut.dstl_check_voice_call_status_by_clcc(is_mo=is_mo))
            test.expect(test.dut.dstl_monitor_network_act() in ('2G','3G'))

            test.log.step(f"2.{i}.4. during the calling, activate one PDP context, open the IP service"
                          f" and establish the dial-up via PC or the ECM(at+swwan)")
            test.log.info(f"Opening IP Service for PDP context {test.cid}.")
            test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))
            test.expect(test.dut.dstl_check_voice_call_status_by_clcc(is_mo=is_mo))
            test.expect(test.dut.dstl_monitor_network_act() in ('2G','3G'))
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.internet_connection_dut.dstl_deactivate_internet_connection())
            test.sleep(5)

            test.log.info("Establish RMNET connection.")
            test.log.info("Activate the defined context,  but if it failed, any activated context "
                          "will be used for RMNET.")
            test.expect(test.internet_connection_dut.dstl_activate_pdp_context())
            test.dut.at1.send_and_verify("AT+CGPADDR", "OK")
            cids = re.findall('\+CGPADDR: (\d+),"\d.*', test.dut.at1.last_response)
            swan_id = ""
            if cids:
                test.log.info("Use the context which is not IMS for RMNET.")
                ims_cid = ""
                if len(cids) > 1:
                    test.dut.at1.send_and_verify('AT+CGDCONT?', 'OK')
                    ims_cid = re.findall('CGDCONT: (\d+),"IP.*?","IMS"', test.dut.at1.last_response)
                    if ims_cid:
                        ims_cid = ims_cid[0]
                for id in cids:
                    if id != ims_cid:
                        swan_id = id
                        break
            if swan_id:
                test.expect(test.dut.at1.send_and_verify(f'AT^SWWAN=1,{swan_id},1', expect='OK'))
                test.expect(test.dut.dstl_check_voice_call_status_by_clcc(is_mo=is_mo))
                test.expect(test.dut.dstl_monitor_network_act() in ('2G','3G'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SWWAN=0,{swan_id},1', expect='OK'))
            else:
                test.expect(cids, msg="No internet connection, cannot establish RMNET connection.")
            test.expect(test.internet_connection_dut.dstl_deactivate_pdp_context())

            test.log.step(f"2.{i}.5. during the calling, send and receive the SMS")
            test.expect(test.dut.dstl_enable_sms_urc())
            test.expect(test.dut.dstl_send_sms_message(destination_addr=test.dut.sim.nat_voice_nr,
                                                       sms_text="send SMS during call"))
            test.expect(test.dut.dstl_check_urc('.*CMTI.*'))
            test.expect(test.dut.dstl_monitor_network_act() in ('2G','3G'))

            test.log.step(f"2.{i}.6. after hanging up the call the module shall "
                          f"switch back to 4G on its own")
            test.expect(test.dut.dstl_release_call())
            test.log.info("Wait for some time for network being stable.")
            test.sleep(5)
            test.expect(test.dut.dstl_monitor_network_act() == '4G')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CVMOD=3", "OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SSRVSET=actsrvset,1', expect='OK'))
        test.expect(test.dut.dstl_restart())



if '__main__' == __name__:
    unicorn.main()
