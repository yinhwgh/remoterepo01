#responsible: kamil.kedron@globallogic.com
#location: Wroclaw
#TC0000325.002

import unicorn
import re

from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.status_control.sind_parameters import dstl_get_sind_read_response_dict
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.sms_functions import dstl_enable_sms_urc
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.sms_functions import dstl_list_occupied_sms_indexes
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message


class Test(BaseTest):
    """
    INTENTION
    Check with SIND command the indicator "message" output while sending SMS.

    PRECONDITION
    2 Modules must be on and pin must be added.
    All other indicators not used in this test are deactivated.
    Module is in it factory defaults.

    EXPECTED RESULTS
    5. Output of indicator. "message" unread message (0-1).
    12. If message is received, the status of indicator "message" has to change to 1.("+CIEV: message,1")
    14. If message is read, the status of indicator "message" has to change to 0. ("+CIEV: message,0")
    17. Should be deactivated.
    19. There should not be any "+CIEV. message"
    """
    def setup(test):
        test.time_value = 5
        test.wait_time_value = 90
        test.enable_state = 1
        test.disable_state = 0
        test.test_sind = "message"
        test.sms_message = "The quick brown fox jumps over the lazy dog"

        test.set_precondition(test.dut)
        test.set_precondition(test.r1)

        if not test.dut.at1.send_and_verify("AT^SIND?", "^SIND: message"):
            test.expect(False, critical=True,
                        msg=f"Product {test.dut.product} does not support AT^SIND= 'message', scripts exit")

        test.log.info('Precondition: Delete all SMS from ME and SM storage.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
        test.log.step('1. Set modules to factory defaults.')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))

        test.log.step('2. Deactivate all other indicators not used in this test.')
        sind_dict = dstl_get_sind_read_response_dict(test.dut)
        for sind_key, sind_value in sind_dict.items():
            test.expect(test.dut.at1.send_and_verify(f'AT^SIND="{sind_key}",0', ".*OK.*"),
                        msg=f'Failed: AT^SIND="{sind_key}" is not deactivated')

        test.log.step('3. Check "message" indicator. Should be deactivated.')
        test.expect(test.get_status_sind(test.test_sind, test.disable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'message' is not deactivated")

        test.log.step('4. Enable the "message" indicator with SIND command for the test.')
        test.expect(test.set_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'message' is not enabled")

        test.log.step('5. Check "message" indicator. Should be activated.')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'message' is not activated")

        test.log.step('6. Set SMS Text Mode.')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step('7. Set SMS storage to ME and write SMS until storage is full.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        for mem_num in range(dstl_get_sms_count_from_memory(test.dut)[2],
                              int(dstl_get_sms_memory_capacity(test.dut, 3))):
            dstl_write_sms_to_memory(test.dut)
            test.expect(test.check_no_urc(test.dut.at1, "CIEV: message", test.time_value))

        test.log.step('8. Change storage to SM.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(test.check_no_urc(test.dut.at1, "CIEV: message", test.time_value))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "SM"))

        test.log.step('9. Delete all SMS from SM storage.')
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('10. Set Service Center Adress.')
        test.expect(dstl_set_sms_center_address(test.dut))
        test.expect(dstl_set_sms_center_address(test.r1))

        test.log.step('11. Send SMS.')
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.nat_voice_nr, test.sms_message))

        test.log.step('12. Check with SIND command the indicator "message" output while sending SMS.')
        if test.get_status_sind(test.test_sind, test.enable_state, test.disable_state):
            test.log.info(" AT^SIND= 'message' status does not changed before sms received")
        else:
            test.log.info(" AT^SIND= 'message' status changed sms received")
        test.expect(test.dut.at1.wait_for("CIEV: message,1", append=True), msg="Failed: CIEV: message,1 not occurred")
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.enable_state),
                    msg="Failed: AT^SIND= 'message' status does not changed before sms received")

        test.log.step('13. List and read SMS messages from SM storage.')
        test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, "All"))
        test.expect(test.dut.at1.wait_for("CIEV: message,0", append=True), msg="Failed: CIEV: message,0 not occurred")
        test.expect(dstl_read_sms_message(test.dut, int(dstl_list_occupied_sms_indexes(test.dut)[-1])))

        test.log.step('14. Check the status of indicator "message".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'message' does not changed")

        test.log.step('15. Delete all SMS from ME and SM storage.')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.check_no_urc(test.dut.at1, "CIEV: message", test.time_value))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.check_no_urc(test.dut.at1, "CIEV: message", test.time_value))

        test.log.step('16. Disable the "message" indicator with SIND command for the test.')
        test.expect(test.set_status_sind(test.test_sind, test.disable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'message' is not deactivated")

        test.log.step('17. Check the status of indicator "message".')
        test.expect(test.get_status_sind(test.test_sind, test.disable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'message' is not deactivated")

        test.log.step('18. Send SMS.')
        test.expect(dstl_enable_sms_urc(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.nat_voice_nr, test.sms_message))

        test.log.step('19. Check "message" indicator.')
        test.expect(test.check_no_urc(test.dut.at1, "CIEV: message", test.wait_time_value))

        test.log.step('20. List and read SMS messages from preferred storage.')
        test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, "All"))
        test.expect(test.check_no_urc(test.dut.at1, "CIEV: message", test.wait_time_value))
        test.expect(dstl_read_sms_message(test.dut, int(dstl_list_occupied_sms_indexes(test.dut)[-1])))

        test.log.step('21. Delete SMS from preferred stored.')
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def cleanup(test):
        test.log.info('Delete all SMS from ME and SM storage for DUT and Remote.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))

    def set_precondition(test, interface):
        dstl_detect(interface)
        dstl_get_imei(interface)
        dstl_get_bootloader(interface)
        test.expect(dstl_register_to_network(interface))

    def set_status_sind(test, sind_param, sind_mode, sind_ind=0):
        return test.dut.at1.send_and_verify(f'AT^SIND="{sind_param}",{sind_mode}',
                                            f'^SIND: {sind_param},{sind_mode},{sind_ind}')

    def get_status_sind(test, sind_param, exp_sind, sind_ind):
        return test.dut.at1.send_and_verify(f'AT^SIND="{sind_param}",2',
                                            f'^SIND: {sind_param},{exp_sind},{sind_ind}')

    def check_no_urc(test, interface, urc, timeout):
        test.wait(timeout)
        interface.read(append=True)
        if re.search(urc, interface.last_response):
            test.log.error(f"URC {urc} occurred, Test Failed")
            return False
        else:
            test.log.info(f"URC {urc} not occurred, Test Passed")
            return True


if "__main__" == __name__:
    unicorn.main()