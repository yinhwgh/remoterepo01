# responsible: dominik.tanderys@globallogic.com
# Wroclaw
# TC0093977.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr, dstl_switch_to_command_mode_by_pluses
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
       TC intention: 	Check if RING line works properly when SMS is received during data mode.

       Description:
       1) Enter PIN and attach module to the network.
       2) Set SMS Event Reporting Configuration (AT+CNMI=2,1).
       3) Define PDP context and activate it.
       4) Define service profiles:
            - on DUT: TCP Transparent Client
            - on Remote: TCP Transparent Listener
        5) Open connection on Remote than on DUT.
        6) Enter data mode.
        7) Send sms from Remote to DUT.
        8) Check whether the RING line has changed its state.
        9) Leave transparent mode.
        10) Check if URC which informs about new SMS is received.
        11) Read SMS on DUT.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

        dstl_detect(test.r1)

        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1, "on"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut, "on"))

        test.expect(test.dut.at1.send_and_verify("at^scfg=\"URC/Ringline\", \"asc0\""))
        test.expect(test.dut.at1.send_and_verify("at^scfg=\"URC/Ringline/ActiveTime\", \"2\""))

        dstl_delete_all_sms_messages(test.dut)

    def run(test):
        test.log.step("1) Enter PIN and attach module to the network.")
        dstl_register_to_network(test.dut)
        dstl_register_to_network(test.r1)
        test.expect(test.dut.at1.send_and_verify("AT&D2"))

        test.log.step("2) Set SMS Event Reporting Configuration (AT+CNMI=2,1).")
        test.expect(test.dut.at1.send_and_verify("at+cnmi=2,1"))

        test.log.info("Changing sms mode to text, to make sending adn reading SMS easier")
        dstl_select_sms_message_format(test.dut)
        dstl_select_sms_message_format(test.r1)

        test.log.step("3) Define PDP context and activate it.")
        connection = dstl_get_connection_setup_object(test.dut)
        test.expect(connection.dstl_load_internet_connection_profile())
        test.expect(connection.dstl_activate_internet_connection(), msg="Could not activate PDP context")

        connection_rem = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_rem.dstl_load_internet_connection_profile())
        test.expect(connection_rem.dstl_activate_internet_connection(), msg="Could not activate PDP context")

        test.log.step("4) Define service profiles:"
                      "- on DUT: TCP Transparent Client"
                      "- on Remote: TCP Transparent Listener")
        rem_port = "8888"
        test.profile_rem = SocketProfile(test.r1, "0", connection_rem.dstl_get_used_cid(), host="listener",
                                         port=rem_port, protocol="tcp", empty_etx=True)
        test.profile_rem.dstl_generate_address()
        test.expect(test.profile_rem.dstl_get_service().dstl_load_profile())
        test.expect(test.profile_rem.dstl_get_service().dstl_open_service_profile())
        rem_address_and_port = test.profile_rem.dstl_get_parser().dstl_get_service_local_address_and_port("IPv4")
        rem_address = rem_address_and_port.split(":")

        test.profile_dut = SocketProfile(test.dut, "0", connection_rem.dstl_get_used_cid(), host=rem_address[0],
                                         port=rem_port, protocol="tcp", empty_etx=True)
        test.profile_dut.dstl_generate_address()
        test.expect(test.profile_dut.dstl_get_service().dstl_load_profile())

        test.log.step("5) Open connection on Remote than on DUT.")
        test.expect(test.profile_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile_rem.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(test.profile_rem.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile_rem.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6) Enter data mode.")
        test.expect(test.profile_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("7) Send sms from Remote to DUT.")
        test.dut.at1.append(True)
        test.expect(test.dut.devboard.send_and_verify("MC:URC = on, RING"))
        dstl_set_sms_center_address(test.r1, test.r1.sim.sca)
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.nat_voice_nr))

        test.log.step("8) Check whether the RING line has changed its state.")
        sms_timeout = 60
        test.expect(test.dut.devboard.wait_for(".*RINGline: 1.*", sms_timeout))

        test.log.step("9) Leave transparent mode.")
        if not dstl_switch_to_command_mode_by_dtr(test.dut):
            dstl_switch_to_command_mode_by_pluses(test.dut)
            test.expect(False, "Did not leave command mode")

        else:
            test.expect(True)

        test.log.step("10) Check if URC which informs about new SMS is received.")
        if "CMTI" not in test.dut.at1.last_response:
            test.expect(test.dut.at1.wait_for(".*\+CMTI.*"))

        else:
            test.expect(True)

        test.dut.at1.append(False)

        test.log.step("11) Read SMS on DUT.")

        sms_index = 0
        test.expect("This is SMS Message with default content in Text mode" in
                    dstl_read_sms_message(test.dut, sms_index))

    def cleanup(test):
        test.profile_dut.dstl_get_service().dstl_close_service_profile()
        test.profile_rem.dstl_get_service().dstl_close_service_profile()
        dstl_delete_all_sms_messages(test.dut)



if "__main__" == __name__:
    unicorn.main()