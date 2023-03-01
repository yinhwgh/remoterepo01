#author: lei.chen@thalesgroup.com
#location: Dalian
#TC0091748.001 TC0091749.001, TC0010801.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.configuration import character_set
from dstl.phonebook import phonebook_handle
from dstl.auxiliary import parse_text_to_regular_expression
from dstl.call import setup_voice_call
from dstl.supplementary_services import lock_unlock_facility
from dstl.phonebook import phonebook_types

class Test(BaseTest):
    """TC0088032.001 - IntelFdTypeClck
       Intention:
        Check if numbers of all supported types of address can be stored in FD phonebook,
        and directly dialed from the storrage during active SIM Fixed Dialing lock.
        Write (from the range 128-255) and select (only the following ones are valid: 129, 145) diffent type of address for the FD phonebook. FD phonebook will be locked with "CLCK" command.
       Description:
        1. Lock FD phonebook with "CLCK" command (AT+CLCK).
        2. Fill out the FD phonebook (AT+CPBW) with:
        - national number,
        - international number,
        - Calling Line Identity suppresed with a prefix #31# before national number,
        - Calling Line Identity enabled with a prefix *31# before international number,
        - star-hash code for cheking IMEI (*#06#),
        all with different type of address (128-255).
        3. Read out phonebook with (AT+CPBR).
        4. For the entries with types of address: 129 and 145 dial directly from phonebook (ATD>FD).
        5. Delete phonebook (AT+CPBW)
        6. Unlock FD with "CLCK" command (AT+CLCK)
    """
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

    def run(test):
        # For QCT: False, for Intel, maybe True
        allow_non_alphabet = False
        nat_rem_num = test.r1.sim.nat_voice_nr
        int_rem_num = test.r1.sim.int_voice_nr
        test.expect(test.dut.dstl_clear_all_pb_storage())
        test.number_types = test.dut.dstl_get_supported_number_types()
        test.type_count = len(test.number_types)
        test.expect(test.dut.dstl_set_pb_memory_storage('FD'))
        test.expect(test.dut.dstl_is_facility_locked('FD', '255')==False)
        test.expect(test.dut.dstl_lock_unlock_facility(facility='FD', lock=True))
        test.expect(test.dut.dstl_is_facility_locked('FD', '255')==True)

        test.log.step("1. Checking number without explicitly specified type, with or without text.")
        test.expect(test.dut.dstl_write_pb_entries(1, nat_rem_num, type="", text=""))
        test.expect(test.dut.dstl_write_pb_entries(2, nat_rem_num, type="", text="National"))
        test.expect(test.dut.dstl_write_pb_entries(3, int_rem_num, type="", text=""))
        test.expect(test.dut.dstl_write_pb_entries(4, int_rem_num, type="", text="International"))
        expect_read_response = f"\+CPBR: 1,\"{nat_rem_num}\",129,\"\"\s+"
        expect_read_response += f"\+CPBR: 2,\"{nat_rem_num}\",129,\"National\"\s+"
        expect_read_response += f"\+CPBR: 3,\"\{int_rem_num}\",145,\"\"\s+"
        expect_read_response += f"\+CPBR: 4,\"\{int_rem_num}\",145,\"International\"\s+OK"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1,4", expect_read_response))
        test.log.info("*** Clear FD phonebook ***")
        test.clear_fd_pb(4)

        
        test.log.step(f"2. Checking national, international, hash code numbers for all types [test.number_types]")
        for type_ in test.number_types:
            test.log.info(f"*** Writing items with national, international, hash code numbers for {type_} ***")
            test.expect(test.dut.dstl_write_pb_entries(1, nat_rem_num, type=type_, text=f"N Subscriber"))
            test.expect(test.dut.dstl_write_pb_entries(2, int_rem_num, type=type_, text=f"I Subscriber"))
            test.expect(test.dut.dstl_write_pb_entries(3, "#31#" + nat_rem_num, type=type_, text=f"# Subscriber"))
            test.expect(test.dut.dstl_write_pb_entries(4, "*31#" + nat_rem_num, type=type_, text=f"* Subscriber"))
            test.expect(test.dut.dstl_write_pb_entries(5, "*#06#", type=type_, text=f"06 Subscriber"))

            expect_read_response = f"\+CPBR: 1,\"{nat_rem_num}\",{type_},\"N Subscriber\""
            expect_read_response += f"\+CPBR: 2,\"\{int_rem_num}\",{type_}\",\"I Subscriber\""
            expect_read_response += f"\+CPBR: 3,\"#31#{nat_rem_num}\",{type_}\",\"# Subscriber\""
            expect_read_response += f"\+CPBR: 4,\"\*31#{nat_rem_num}\",{type_}\",\"\* Subscriber\""
            expect_read_response += f"\+CPBR: 5,\"\*#06#\",{type_},\"06 Subscriber\""
            test.expect(test.dut.at1.send_and_verify("AT+CPBR=1,5", expect_read_response))

            test.log.info(f"*** Dial number in each location ***")
            for i in range(1,6):
                dial_expect = 'OK'
                if i == 5:
                    dial_expect = "\d{15}\s+OK"
                dial_succeed = test.dut.dstl_mo_call_by_mem_index('FD', i, dial_expect)
                if dial_succeed and i != 5:
                    test.expect(test.r1.at1.wait_for("RING"))
                    test.expect(test.r1.dstl_release_call())
                test.expect(test.dut.dstl_release_call())

            test.log.info("*** Clear FD phonebook ***")
            test.clear_fd_pb(5)
        
        test.log.step("3. Cannot write numbers with type not in AT+CPBW=? list.")
        for i in range(128, 256):
            if str(i) not in test.number_types:
                test.expect(test.dut.at1.send_and_verify("AT+CPBW=1,\"{nat_rem_num}\",{i},\"Type{i}\"", "ERROR"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBW=1"))


    def cleanup(test):
        test.expect(test.dut.dstl_lock_unlock_facility(facility='FD', lock=False))
        test.expect(test.dut.dstl_is_facility_locked('FD', '255')==False)


    def clear_fd_pb(test, max_loc):
        for i in range(1, max_loc + 1):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i}"))


if '__main__' == __name__:
    unicorn.main()