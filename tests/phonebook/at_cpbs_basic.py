#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091694.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.phonebook import phonebook_handle
from dstl.phonebook import developed_storage
import re

class Test(BaseTest):
    """
    TC0091694.001 - TpAtCpbsBasic
    """

    def setup(test):
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        usim_storage_list = test.get_current_usim_storage()
        me_storage_list = test.dut.dstl_get_developed_me_storage_list()
        all_storage_list = usim_storage_list + me_storage_list
        un_writable_storage_list = ["DC", "LD", "MC", "RC", "EN"]
        cpbs_clear_storage_list = ["DC", "LD", "MC", "RC"]
        test.log.step("1. Check commands without PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=1", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "\+CME ERROR: SIM PIN required"))
        for s in all_storage_list:
            if s == "EN":
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBS={s}", "OK"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "\+CPBS: \"EN\""))
            else:
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBS={s}", "\+CME ERROR: SIM PIN required"))

        test.log.step("2. Check valid commands after PIN input")
        test.log.info("2.1 Check query command AT+CPBS=?")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(10)
        test.attempt(test.dut.at1.send_and_verify,"AT+CPBS?", "OK", retry=5, sleep=3)        
        actual_storages = test.dut.dstl_get_supported_pb_memory_list()
        if actual_storages:
            match_with_expect = len(all_storage_list) == len(actual_storages)
            for s in all_storage_list:
                match_with_expect &= s in actual_storages
            expect_storages = '("{}")'.format('","'.join(all_storage_list))
            if match_with_expect == True:
                test.log.info(f"Actual response match with {expect_storages}")
                test.expect(match_with_expect)
            else:
                test.expect(match_with_expect, msg=f"Actual storages {actual_storages} are not matched with expected {expect_storages}.")
        else:
            test.log.error("No storage found from AT+CPBS=?")
        
        un_writable_storages = ', '.join(un_writable_storage_list)
        test.log.info(f"2.2. AT+CPBW command is applicable to all storage that module currently supports except {un_writable_storages}")
        test.log.info("Clear un-writable storage")
        test.expect(test.dut.at1.send_and_verify("AT+CPBS"))
        for s in actual_storages:
            test.log.info(f"Setting PB storage to {s}")
            test.expect(test.dut.dstl_set_pb_memory_storage(s))
            record = f"1,\"123456\",129,\"{s}1\""
            if s not in un_writable_storage_list:
                exp_resp = "OK"
                read_resp = f"CPBR: {record}"
            else:
                test.log.info(f"AT+CPBW command is not applicable to {s}")
                exp_resp = "\+CME ERROR: operation not allowed"
                if s == "EN":
                    read_resp = "OK|\+CME ERROR: not found"
                else:
                    read_resp = "\+CME ERROR: not found" 
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={record}", exp_resp))
            test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", read_resp))
        
        test.log.step("3. Functionality test for un-writable storage")
        dc_ld = []
        if "DC" in actual_storages:
            dc_ld.append("DC")
        if "LD" in actual_storages:
            dc_ld.append("LD")
        if len(dc_ld) > 0:
            test.log.info("Generating records for LD/DC")
            test.expect(test.dut.at1.send_and_verify(f"atd\"{test.r1.sim.int_voice_nr}\";"))
            test.expect(test.r1.at1.wait_for("RING"))
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
            for s in dc_ld:
                test.expect(test.dut.dstl_set_pb_memory_storage(s))
                test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", f"CPBR: 1,\"{test.r1.sim.int_voice_nr}\","))
        else:
            test.log.info("Module does not support DC or LD, skip steps.")

        if "MC" in actual_storages:
            test.log.info("Generating records for MC")
            test.expect(test.r1.at1.send_and_verify(f"atd{test.dut.sim.int_voice_nr};"))
            test.expect(test.dut.at1.wait_for("RING"))
            test.expect(test.r1.at1.send_and_verify("AT+CHUP", "OK"))
            test.expect(test.dut.dstl_set_pb_memory_storage("MC"))
            test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", "\+CPBR: 1,\"{test.r1.sim.int_voice_nr}\","))
        else:
            test.log.info("Module does not support MC, skip steps.")

        if "RC" in actual_storages:
            test.log.info("Generating records for RC")
            test.expect(test.r1.at1.send_and_verify(f"atd{test.dut.sim.int_voice_nr};"))
            test.expect(test.dut.at1.wait_for("RING"))
            test.expect(test.dut.at1.send_and_verify("ATA", "OK"))
            test.sleep(1)
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
            test.expect(test.dut.dstl_set_pb_memory_storage("RC"))
            test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", "\+CPBR: 1,\"{test.r1.sim.int_voice_nr}\","))
        else:
            test.log.info("Module does not support RC, skip steps.")
        
        test.log.info("AT+CPBS clear all records in DC, LD, MC and RC.")
        test.expect(test.dut.at1.send_and_verify("AT+CPBS", "OK"))
        for s in cpbs_clear_storage_list:
            if s in actual_storages:
                test.expect(test.dut.dstl_set_pb_memory_storage(s))
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=\"{s}\"", "OK"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\+CPBS: \"{s}\",0,"))
    
        test.log.step("4. Check invalid commands after PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"MM\"", "\+CME ERROR: \w+"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"1\"", "\+CME ERROR: \w+"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=1", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"-1\"", "\+CME ERROR: \w+"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=-1", "\+CME ERROR: \w+"))

        test.log.step("5. AT&F restore storage to SM")
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "OK"))
        if "SM" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=\"{me_storage_list[0]}\"", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"{me_storage_list[0]}"))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "SM"))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))

    def get_current_usim_storage(test):
        """
        Get storage list which module supports and correct SIM card supports
        """
        full_usim_storage_list = test.dut.dstl_get_developed_usim_storage_list()
        full_usim_storages = ', '.join(full_usim_storage_list)
        test.log.info(f"Got all USIM storages that module supports: {full_usim_storages}")
        supported_storage_list = ['SM', 'ON']
        test.log.info("Reading PB storage properties from SIM")
        for s in full_usim_storage_list:
            if s not in supported_storage_list:
                if s == 'VM':
                    s_param = f"pb_{s.lower()}_availability"
                else:
                    s_param = f"pb_{s.lower()}_available"
                if hasattr(test.dut.sim, s_param):
                    s_param_value = eval(f"test.dut.sim.{s_param}")
                    test.log.info(f"Read SIM {s_param}: {s_param_value}")
                    if s_param_value.strip() == "true":
                        supported_storage_list.append(s)
                else:
                    test.log.error(f"Please configure SIM property: {s_param}")
        supported_storages = ', '.join(supported_storage_list)
        test.log.info(f"Current SIM card supports: {supported_storages}")
        return supported_storage_list


if __name__ == "__main__":
        unicorn.main()
