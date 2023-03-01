#responsible: kamil.kedron@globallogic.com
#location: Wroclaw
#TC0000329.002

import unicorn

from core.basetest import BaseTest

from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.status_control.sind_parameters import dstl_get_sind_read_response_dict
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.delete_sms import dstl_delete_sms_message_from_index
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """
    INTENTION
    Disable the indicator "smsfull" with "SIND" command.
    Now a check on on the status of following parameters becomes available:
    - "smsfull" the short message memory storage in the MT has become full (1)
    - memory locations are available (0) in the short message memory storage in the MT; i.e. the range is (0-1)

    PRECONDITION
    All other indicators not used in this test are disabled.
    2 Modules is logged in to the network.

    EXPECTED RESULTS
    The status of indicator "smsfull" is always output correctly.
    """
    def setup(test):
        test.time_value = 5
        test.wait_time_value = 90
        test.enable_state = 1
        test.disable_state = 0
        test.test_sind = "smsfull"
        test.sms_message = "The quick brown fox jumps over the lazy dog"

        test.set_precondition(test.dut)
        test.set_precondition(test.r1)

        if not test.dut.at1.send_and_verify("AT^SIND?", "^SIND: smsfull"):
            test.expect(False, critical=True,
                        msg=f"Product {test.dut.product} does not support AT^SIND= 'smsfull', scripts exit")

        test.log.info('Precondition: Delete all SMS from ME and SM storage.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
        test.log.step('1. Deactivate all other indicators not used in this test')
        sind_dict = dstl_get_sind_read_response_dict(test.dut)
        for sind_key, sind_value in sind_dict.items():
            test.expect(test.dut.at1.send_and_verify(f'AT^SIND="{sind_key}",0', ".*OK.*"),
                        msg=f'Failed: AT^SIND="{sind_key}" is not deactivated')

        test.log.step('2. Check "smsfull" indicator. Should be deactivated')
        test.expect(test.get_status_sind(test.test_sind, test.disable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' is not deactivated")

        test.log.step('3. Enable the "smsfull" indicator with SIND command for the test')
        test.expect(test.set_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' is not enabled")

        test.log.step('4. Check "smsfull" indicator. Should be activated')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' is not activated")

        test.log.step('5. Set SMS Text Mode')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(test.r1))

        test.log.step('6. Set SMS storage to ME and write SMS until storage is one sms before full.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        for mem_num in range(dstl_get_sms_count_from_memory(test.dut)[2],
                             int(dstl_get_sms_memory_capacity(test.dut, 3))-1):
            dstl_write_sms_to_memory(test.dut)

        test.log.step('7. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status changed before last sms saved to storage")

        test.log.step('8. Write one last SMS to storage.')
        dstl_write_sms_to_memory(test.dut)

        test.log.step('9. Check if "smsfull" URC was received')
        test.expect(test.dut.at1.wait_for("CIEV: smsfull,1", append=True), msg="Failed: CIEV: smsfull,1 not occurred")

        test.log.step('10. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.enable_state),
                    msg="Failed: AT^SIND= 'smsfull' status not changed after last sms saved to storage")

        test.log.step('11. Change storage to SM')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "SM"))

        test.log.step('12. Set Service Center Address')
        test.expect(dstl_set_sms_center_address(test.dut))
        test.expect(dstl_set_sms_center_address(test.r1))

        test.log.step('13. Send SMS until storage is one sms before full.')
        test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*", timeout=test.time_value)
        while True:
            test.expect(dstl_send_sms_message(test.r1, test.dut.sim.nat_voice_nr, test.sms_message))
            test.dut.at1.wait_for("CMTI:", timeout=test.wait_time_value, append=True)
            if range(dstl_get_sms_count_from_memory(test.dut)[2] == int(dstl_get_sms_memory_capacity(test.dut, 3)) - 1):
                break
            else:
                continue

        test.log.step('14. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status changed before last sms saved to storage")

        test.log.step('15. Send one last SMS.')
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.nat_voice_nr, test.sms_message))
        test.dut.at1.wait_for("CMTI:", timeout=test.wait_time_value, append=True)

        test.log.step('16. Check if "smsfull" URC was received')
        test.expect(test.dut.at1.wait_for("CIEV: smsfull,1", append=True), msg="Failed: CIEV: smsfull,1 not occurred")

        test.log.step('17. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.enable_state),
                    msg="Failed: AT^SIND= 'smsfull' status not changed after last sms saved to storage")

        test.log.step('18. Delete one SMS from SM storage.')
        test.expect(dstl_delete_sms_message_from_index(test.dut,0))

        test.log.step('19. Check if "smsfull" URC was received')
        test.expect(test.dut.at1.wait_for("CIEV: smsfull,0", append=True), msg="Failed: CIEV: smsfull,0 not occurred")

        test.log.step('20. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status not changed after one sms was deleted from storage")

        test.log.step('21. Delete one SMS from ME storage.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_sms_message_from_index(test.dut,0))

        test.log.step('22. Check if "smsfull" URC was received')
        test.expect(test.dut.at1.wait_for("CIEV: smsfull,0", append=True), msg="Failed: CIEV: smsfull,0 not occurred")

        test.log.step('23. Check with SIND command the indicator "smsfull".')
        test.expect(test.get_status_sind(test.test_sind, test.enable_state, test.disable_state),
                    msg="Failed: AT^SIND= 'smsfull' status not changed after one sms was deleted from storage")

        test.log.step('24. Delete all SMS from ME and SM storage.')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def cleanup(test):
        test.log.info('Delete all SMS from ME and SM storage.')
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.r1.at1.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))

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


if "__main__" == __name__:
    unicorn.main()