#responsible: lei.chen@thalesgroup.com
#location: Dalian
# TC0103774.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.configuration import character_set

from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser

class Test(BaseTest):
    """
       TC0103774.001 - Character_GSM_UCS2_ServiceProfile
       Check if GSM characters can transform to UCS2 character correctly in AT command AT^SISS.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(3)
        test.expect(test.dut.dstl_enter_pin())
    
    def run(test):
        # Socket server setup
        socket_profile_id = 3
        test.log.step('Socket Step 1. Set character set to GSM.')
        test.expect(test.dut.dstl_set_character_set("GSM"))

        test.log.step('Socket Step 2. Configure socket client service profile.')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        used_cid = connection_setup_dut.dstl_get_used_cid()

        test.echo_server = EchoServer("IPv4", "TCP")
        socket_profile = SocketProfile(test.dut, socket_profile_id, used_cid, protocol="TCP")
        socket_profile.dstl_set_parameters_from_ip_server(test.echo_server)

        socket_profile.dstl_generate_address()
        socket_address = socket_profile._model.address
        test.expect(socket_profile.dstl_get_service().dstl_load_profile())

        test.log.step('Socket Step 3. Read profile and connect the service.')
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
        profile_info = test.dut.at1.last_response
        test.expect(f'^SISS: {socket_profile_id},"srvType","Socket"' in profile_info, msg="srvType \"Socket\" is not in response")
        test.expect(f'^SISS: {socket_profile_id},"conId","{used_cid}"' in profile_info, msg=f"conid \"{used_cid}\" is not in response")
        test.expect(f'^SISS: {socket_profile_id},"address","{socket_address}"' in profile_info, msg=f"address \"{used_cid}\" is not in response")
        test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {socket_profile_id},\"Socket\",2,1"))
        test.expect(socket_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {socket_profile_id},\"Socket\",4,2"))
        test.expect(socket_profile.dstl_get_service().dstl_close_service_profile())

        test.log.step('Socket Step 4. Change the character set to UCS2')
        test.expect(test.dut.dstl_set_character_set("UCS2"))

        test.log.step('Socket Step 5. Read profile and connect the service again')
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
        profile_info = test.dut.at1.last_response
        srv_type_ucs2 = test.dut.dstl_convert_to_ucs2("Socket")
        used_cid_ucs2 = test.dut.dstl_convert_to_ucs2(used_cid)
        socket_address_ucs2 = test.dut.dstl_convert_to_ucs2(socket_address)
        test.expect(f'^SISS: {socket_profile_id},"srvType","{srv_type_ucs2}"' in profile_info, msg=f"srvType ucs2 code \"{srv_type_ucs2}\" is not in reponse")
        test.expect(f'^SISS: {socket_profile_id},"conId","{used_cid_ucs2}"' in profile_info, msg=f"conid ucs2 code \"{used_cid_ucs2}\" is not in reponse")
        test.expect(f'^SISS: {socket_profile_id},"address","{socket_address_ucs2}"' in profile_info, msg=f"address ucs2 code \"{socket_address_ucs2}\" is not in reponse")
        test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {socket_profile_id},\"Socket\",2,1"))
        test.expect(socket_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {socket_profile_id},\"Socket\",4,2"))

        test.log.step('Socket Step 6. Change character set back to "GSM", check if all the characters are still keep the original value')
        test.expect(test.dut.dstl_set_character_set("GSM"))
        test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {socket_profile_id},\"Socket\",4,2"))
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
        profile_info = test.dut.at1.last_response
        test.expect(f'^SISS: {socket_profile_id},"srvType","Socket"' in profile_info, msg="srvType in response is incorrect")
        test.expect(f'^SISS: {socket_profile_id},"conId","{used_cid}"' in profile_info, msg="conid in response is incorrect")
        test.expect(f'^SISS: {socket_profile_id},"address","{socket_address}"' in profile_info, msg="address in response is incorrect")
        test.expect(socket_profile.dstl_get_service().dstl_close_service_profile())

        # Setup FTP server
        ftp_profile_id = 2
        if test.dut.at1.send_and_verify(f"AT^SISS={ftp_profile_id},srvType,Ftp", "OK"):
            test.log.step('FTP Step 1. Set character set to GSM.')
            test.expect(test.dut.dstl_set_character_set("GSM"))

            test.log.step('FTP Step 2. Configure socket client service profile.')
            connection_setup_dut = dstl_get_connection_setup_object(test.dut)
            test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
            used_cid = connection_setup_dut.dstl_get_used_cid()

            test.ftp_server = FtpServer("IPv4", test, used_cid)
            test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
            test.ftp_port = test.ftp_server.dstl_get_server_port()
            ftp_profile = FtpProfile(test.dut, ftp_profile_id, used_cid,
                                        host=test.ftp_ip_address, port=test.ftp_port,
                                        user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd(), command="dir")
            ftp_profile.dstl_generate_address()
            ftp_address = ftp_profile._model.address
            test.log.info("Generated address is {}".format(ftp_address))
            test.expect(ftp_profile.dstl_get_service().dstl_load_profile())

            test.log.step('FTP Step 3. Read profile and connect the service.')
            test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
            profile_info = test.dut.at1.last_response
            test.expect(f'^SISS: {ftp_profile_id},"srvType","Ftp"' in profile_info, msg="srvType \"Ftp\" is not in response")
            test.expect(f'^SISS: {ftp_profile_id},"conId","{used_cid}"' in profile_info, msg=f"conid \"{used_cid}\" is not in response")
            test.expect(f'^SISS: {ftp_profile_id},"address","{ftp_address}"' in profile_info, msg=f"address \"{used_cid}\" is not in response")
            test.expect(f'^SISS: {ftp_profile_id},"cmd","dir"' in profile_info, msg=f"cmd \"dir\" is not in response")
            test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {ftp_profile_id},\"Ftp\",2,1", wait_after_send=2))
            test.expect(ftp_profile.dstl_get_service().dstl_close_service_profile())
            test.expect(ftp_profile.dstl_get_service().dstl_open_service_profile())
            test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {ftp_profile_id},\"Ftp\",4,2"))
            test.expect(ftp_profile.dstl_get_service().dstl_close_service_profile())

            test.log.step('FTP Step 4. Change the character set to UCS2')
            test.expect(test.dut.dstl_set_character_set("UCS2"))

            test.log.step('FTP Step 5. Read profile and connect the service again')
            test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
            profile_info = test.dut.at1.last_response
            srv_type_ucs2 = test.dut.dstl_convert_to_ucs2("Ftp")
            used_cid_ucs2 = test.dut.dstl_convert_to_ucs2(used_cid)
            ftp_address_ucs2 = test.dut.dstl_convert_to_ucs2(ftp_address)
            test.log.info(f'Verify <^SISS: {ftp_profile_id},"srvType","{srv_type_ucs2}"> in response')
            test.expect(f'^SISS: {ftp_profile_id},"srvType","{srv_type_ucs2}"' in profile_info, msg=f"srvType ucs2 code \"{srv_type_ucs2}\" is not in reponse")
            test.log.info(f'Verify <^SISS: {ftp_profile_id},"conId","{used_cid_ucs2}"> in response')
            test.expect(f'^SISS: {ftp_profile_id},"conId","{used_cid_ucs2}"' in profile_info, msg=f"conid ucs2 code \"{used_cid_ucs2}\" is not in reponse")
            test.log.info(f'Verify <^SISS: {ftp_profile_id},"address","{ftp_address_ucs2}"> in response')
            test.expect(f'^SISS: {ftp_profile_id},"address","{ftp_address_ucs2}"' in profile_info, msg=f"address ucs2 code \"{ftp_address_ucs2}\" is not in reponse")
            test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {ftp_profile_id},\"Ftp\",2,1"))
            test.expect(ftp_profile.dstl_get_service().dstl_open_service_profile())
            test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {ftp_profile_id},\"Ftp\",4,2"))

            test.log.step('FTP Step 6. Change character set back to "GSM", check if all the characters are still keep the original value')
            test.expect(test.dut.dstl_set_character_set("GSM"))
            test.expect(test.dut.at1.send_and_verify("AT^SISO?", f"\^SISO: {ftp_profile_id},\"Ftp\",4,2"))
            test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
            profile_info = test.dut.at1.last_response
            test.expect(f'^SISS: {ftp_profile_id},"srvType","Ftp"' in profile_info, msg="srvType in response is incorrect")
            test.expect(f'^SISS: {ftp_profile_id},"conId","{used_cid}"' in profile_info, msg="conid in response is incorrect")
            test.expect(f'^SISS: {ftp_profile_id},"address","{ftp_address}"' in profile_info, msg="address in response is incorrect")
            test.expect(ftp_profile.dstl_get_service().dstl_close_service_profile())

    
    def cleanup(test):
        test.expect(test.dut.dstl_set_character_set("GSM"))
        
if "__main__" == __name__:
    unicorn.main()