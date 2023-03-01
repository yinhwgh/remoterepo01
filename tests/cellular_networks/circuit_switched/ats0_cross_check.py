#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095586.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.call import setup_voice_call
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.packet_domain.start_public_IPv4_data_connection import rasdial_connect


class Test(BaseTest):
    '''
    TC0095586.001 - Ats0_CrossCheck
    Intention: Cross check between ATS0 & SMS/GPRS
    Subscriber: 3
    need add dial_up_name parameter in local.cfg
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.r2.dstl_detect()
        test.expect(test.r2.dstl_register_to_network())

    def run(test):
        dut_phone_num = test.dut.sim.nat_voice_nr
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.log.step("1.Set ATS0=8")
        test.expect(test.dut.at1.send_and_verify("ATS0=8", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:008"))

        test.log.step("2.Make a voice call from Remote1 to DUT")
        test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")

        test.log.step("3.Remote2 send a SMS to DUT before auto answer")
        index = test.r2.dstl_write_sms_to_memory(sms_text="abcdefgh1234567890", sms_format='text', return_index=True)
        test.expect(
            test.r2.at1.send_and_verify('AT+CMSS={}, "{}"'.format(index[0], test.dut.sim.int_voice_nr), '.*OK.*'))
        test.expect(test.dut.at1.wait_for("(RING\s+){8}", timeout=120))
        test.expect(test.dut.at1.wait_for("\^SLCC: 1,1,0,0,0.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,0,0.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))
        test.expect(test.dut.dstl_release_call())

        test.log.step("4: Set FTP/Socket Parameters on DUT")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.echo_server = EchoServer("IPv4", "TCP")
        client_profile = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(), protocol="tcp")
        client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.dut.at1.wait_for('SISW: 1,1')
        test.sleep(2)

        test.log.step("5.Make a voice call from Remote1 to DUT when FTP/Socket download")
        test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")
        test.expect(test.dut.at1.wait_for("(RING\s+){8}", timeout=120))
        test.expect(test.dut.at1.wait_for("\^SLCC: 1,1,0,0,0.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,0,0.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))
        test.expect(test.dut.dstl_release_call())

        #need config dial up port first
        test.log.step("6. DUT Dial up")
        rasdial_connect('*99#', f'{test.dial_up_name}')
        test.log.step("7. Make a voice call from Remote1 to DUT")
        test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")
        test.expect(test.dut.at1.wait_for("(RING\s+){8}", timeout=120))
        test.expect(test.dut.at1.wait_for("\^SLCC: 1,1,0,0,0.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,0,0.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))
        test.expect(test.dut.dstl_release_call())

        #network not support, pending
        test.log.step("8. Make a conference call and check Automatic answer function")


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("ATS0=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:000"))


if "__main__" == __name__:
    unicorn.main()

