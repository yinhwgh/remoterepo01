#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0088220.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.packet_domain import config_pdp_context
from dstl.network_service import network_monitor
import re

class CGCONTRDPBasic(BaseTest):
    '''
    TC0088220.001 - CGCONTRDPBasic
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        test.log.info("Step 1. Check Test, Execute, Write commands before entering pin")
        sim_pin_error = "+CME ERROR: SIM PIN required"
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP=?", sim_pin_error))
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP", sim_pin_error))
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP=1", sim_pin_error))

        test.log.info("Step 2. Check Test, Execute, Write commands after entering pin")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))
        # Test command may incorrect if execute after pin immediately for BOBCAT
        test.sleep(10)
        test.log.info("*************** Test command: active cids are disaplyed ***************")
        test.init_active_cgact_cids = test.get_cgact_active_cids()
        init_active_cid_str = ",".join(test.init_active_cgact_cids)
        expect_available_cids = f"\+CGCONTRDP: \({init_active_cid_str}\)\s+OK"
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP=?", expect_available_cids))

        test.log.info("*************** Execute command: context parameters of active cids display ***************")
        actual_available_cids = re.findall("\+CGCONTRDP: \((.*)\)", test.dut.at1.last_response)[0]
        actual_available_cids = actual_available_cids.split(',')
        cid_pdp_type_dict = test.get_pdp_context_type()
        exec_result = ""
        # For IPV4V6, information occupies two lines.
        for cid in actual_available_cids:
            exec_result += f'\+CGCONTRDP: {cid}.*?\s+'
            if cid_pdp_type_dict[cid] == 'IPV4V6':
                exec_result += f'\+CGCONTRDP: {cid}.*?\s+'
        exec_result += "\s+OK\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP", exec_result))
        
        test.log.info("*************** Write command: context parameters display for each cid ***************")
        test.log.info("*************** Parameters are same with results of execute command ***************")
        exec_res = test.dut.at1.last_response
        for cid in actual_available_cids:
            expect_res_str = ""
            expect_res = re.findall(f"(\+CGCONTRDP: {cid}.*?)\s+", exec_res)
            for line in expect_res:
                expect_res_str += "\s+" + line.replace('+', '\+').replace('.', '\.')
            expect_res_str += "\s+OK"
            test.expect(test.dut.at1.send_and_verify(f"AT+CGCONTRDP={cid}", expect_res_str))
        

        test.log.info("Step 3. Define all possible PDP contexts")
        test.log.info("************ Store init cgdcont configurations for restoring after tests************")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?"))
        test.init_cgdcont_context = re.findall('\+CGDCONT: (\d+,".*?",".*?"),', test.dut.at1.last_response)
        
        test.log.info("********** Deactive context ************")
        # Stores that cids and is ipv4v6 info (True/False) that cannot be deactivated
        test.being_used_cids = {}
        for cid in test.init_active_cgact_cids:
            is_ipv4v6 = False
            if not test.dut.at1.send_and_verify(f"AT+CGACT=0,{cid}", "OK") and cid_pdp_type_dict[cid] == "IPV4V6":
                is_ipv4v6 = True
            test.being_used_cids[cid] = is_ipv4v6


        test.log.info("********** Re-write context for all deactive cids to maximum cid number ************")
        test.log.info("********** 1 IPV4, others IPV4V6 ************")
        test.max_id = test.dut.dstl_get_supported_max_cid("IPV4V6")
        real_cid_apn_dict = test.write_maximum_contexts(test.max_id, skip_cids=test.being_used_cids)
        test.log.info("********** Contexts should reach to the maximum number **********")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", "OK"))
        find_context = re.findall("\+CGDCONT: (\d+),", test.dut.at1.last_response)
        test.expect(find_context and len(find_context) == test.max_id, msg = "Contexts are not as defined.")
                
        test.log.info("Step 4. Activate the maximum number of PDP contexts")
        if len(real_cid_apn_dict) == 2:
            ipv4_real_apn_cid = list(real_cid_apn_dict.keys())[0]
            ipv6_real_apn_cid = list(real_cid_apn_dict.keys())[1]
        else:
            ipv4_real_apn_cid = -1
            ipv6_real_apn_cid = -1
        activated_ids, deactive_ids = test.active_all_pdp_contexts(max_id_num=len(find_context), ipv4_cid=ipv4_real_apn_cid)
                       
        test.log.info("Step 5. Enter the test command (a list of the activated PDP contexts shall be returned)")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?"))
        test.sleep(3)
        act_cid_string = ",".join(activated_ids)
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP=?", f"\+CGCONTRDP: \({act_cid_string}\)\s+OK"))

        test.log.info("Step 6.Eenter the execute command (the dynamic parameters for all activated PDP contexts shall be returned)")
        actual_available_cids = re.findall("\+CGCONTRDP: \(((\d{1,2},?)+)*\)", test.dut.at1.last_response)[0][0].split(',')
        cid_pdp_type_dict = test.get_pdp_context_type()
        exec_result = ""
        # For IPV4V6, information occupies two lines.
        for cid in activated_ids:
            if cid == ipv4_real_apn_cid:
                exec_result += f'\+CGCONTRDP: {cid},"IP","{real_cid_apn_dict[cid]}".*?\s+'
            elif cid == ipv6_real_apn_cid:
                exec_result += f'\+CGCONTRDP: {cid},"IPV4V6","{real_cid_apn_dict[cid]}".*?\s+'
                exec_result += f'\+CGCONTRDP: {cid},"IPV4V6","{real_cid_apn_dict[cid]}".*?\s+'
            else:
                exec_result += f'\+CGCONTRDP: {cid}.*?\s+'
                if cid_pdp_type_dict[cid] == 'IPV4V6':
                    exec_result += f'\+CGCONTRDP: {cid}.*?\s+'
        exec_result += "\s+OK\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CGCONTRDP", exec_result))

        test.log.info("Step 7. Enter the write command for each PDP context (the dynamic parameters for each respective PDP context shall be displayed if that context is active, otherwise OK only)")
        test.log.info("*************** Parameters are same with results of execute command ***************")
        exec_res = test.dut.at1.last_response
        for cid in activated_ids:
            expect_res_str = ""
            expect_res = re.findall(f"(\+CGCONTRDP: {cid}.*?)\s+", exec_res)
            for line in expect_res:
                expect_res_str += "\s+" + line.replace("+","\+").replace(".","\.")
            expect_res_str += "\s+OK"
            test.expect(test.dut.at1.send_and_verify(f"AT+CGCONTRDP={cid}", expect_res_str))
        for cid in deactive_ids:
            test.expect(test.dut.at1.send_and_verify(f"AT+CGCONTRDP={cid}", f"^AT\+CGCONTRDP={cid}\s+OK\s+$"))
        
        test.log.info("Step 8. Enter several illegal parameter values for the write command (shall be rejected)")
        invalid_parameters = {"", "17", "a", "#"}
        for invalid_para in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify(f"AT+CGCONTRDP={invalid_para}", "ERROR"))


    def cleanup(test):
        if hasattr(test, 'max_id'):
            test.log.info("Step 9. Deactivate the PDP contexts")
            test.log.info("************ Deactive context that not being used **************")
            for cid in range(1, test.max_id + 1):
                if str(cid) not in test.being_used_cids:
                    test.log.info(f"cid {str(cid)} is not in initial activated list {list(test.being_used_cids.keys())}, deactive")
                    test.expect(test.dut.at1.send_and_verify(f"AT+CGACT=0,{cid}", "OK"))

            test.log.info("Step 10. Reset the PDP contexts")
            for cid in range(1, test.max_id + 1):
                if str(cid) not in test.being_used_cids:
                    test.log.info(f"cid {cid} is not in intial context list {test.being_used_cids.keys()}, delete")
                    test.expect(test.dut.at1.send_and_verify(f"AT+CGDCONT={cid}", "OK"))
        
        if hasattr(test, 'init_cgdcont_context'):
            test.log.info("************ Set context back to initial value ************")
            for context_string in test.init_cgdcont_context:
                test.expect(test.dut.at1.send_and_verify(f"AT+CGDCONT={context_string}"))
    
    def get_cgact_active_cids(test):
        test.log.info("********** Get active cids with AT+CGACT? **********")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", "OK"))
        cgact_res = test.dut.at1.last_response
        active_ids = re.findall("\+CGACT: (\d+),1", cgact_res)
        return active_ids
    
    def get_pdp_context_type(test):
        """
        Parse cid and pdp type value from response of AT+CGDCONT?
        And save to a dictionary
        """
        cid_type_dict = {}
        test.dut.at1.send_and_verify("AT+CGDCONT?")
        contexts = re.findall("\+CGDCONT: (\d+),\"(.*?)\".*", test.dut.at1.last_response)
        if contexts:
            for context in contexts:
                cid_type_dict[context[0]] = context[1]
        else:
            test.log.error("Unexpected results of AT+CGDCONT?, test will be impacted.")
        return cid_type_dict


    def write_maximum_contexts(test, max_cid_num, skip_cids):
        """
        Get current network type, precedence to read corresponding apn value from simdata
        If apn from simdata is None, set to fake ones "internet", "internet1"...
        1 for IPV4, others are IPV4V6 in default
        skip_cids: a list containing the cids that context will not be modified.
        """ 
        rat_apn_dict = {
            "2G": "GRPS_APN",
            "3G": "UMTS_APN",
            "Cat.NB": "NB_IoT_APN"
        }
        network_type = test.dut.dstl_monitor_network_act()
        # Fetch apn value from sim data, if not configured set to "internet"
        if network_type in rat_apn_dict and hasattr(test.dut.sim, rat_apn_dict[network_type].lower()) and eval(f"test.dut.sim.{rat_apn_dict[network_type].lower()}"):
            real_apn_ipv4 = eval(f"test.dut.sim.{rat_apn_dict[network_type].lower()}")
            real_apn_ipv6 = real_apn_ipv4
        else: 
            real_apn_ipv4 = "internet"
            real_apn_ipv6 = "internet"
            if hasattr(test.dut.sim, 'apn_v6') and test.dut.sim.apn_v6:
                real_apn_ipv6 = test.dut.sim.apn_v6
            if hasattr(test.dut.sim, 'apn_v4') and test.dut.sim.apn_v4:
                real_apn_ipv4 = test.dut.sim.apn_v4
        test.log.info(f"According to simdata configuration, real apn for IP will be set to {real_apn_ipv6}, for IPV4V6 is {real_apn_ipv6}")
        real_apn_cids = []
        real_cid_apn_dict = {}
        ipv4_cid = -1
        ipv6_cid = -1
        # Configure one IP context and one IPV4V6 with real apn value, others will be IPV4V6, "internet<cid>"
        for cid in range(1, test.max_id + 1):
            if cid not in skip_cids:
                if ipv4_cid == -1:
                    test.expect(test.dut.at1.send_and_verify(f"AT+CGDCONT={cid},\"IP\",\"{real_apn_ipv4}\"", "OK"))
                    ipv4_cid = cid
                    real_cid_apn_dict[cid] = real_apn_ipv4
                elif ipv6_cid == -1:
                    test.expect(test.dut.at1.send_and_verify(f"AT+CGDCONT={cid},\"IPV4V6\",\"{real_apn_ipv6}\"", "OK"))
                    ipv6_cid = cid
                    real_cid_apn_dict[cid] = real_apn_ipv6
                else:
                    test.expect(test.dut.at1.send_and_verify(f"AT+CGDCONT={cid},\"IPV4V6\",\"internet{cid}\"", "OK"))
        
        return real_cid_apn_dict
    
    def active_all_pdp_contexts(test, max_id_num, ipv4_cid):
        """
        Try to active all PDP contexts that defined. 
        Save activated cids to list active_cids.
        Save activated-failed cids to list deactive_cids.
        """
        ok_or_error = "OK|ERROR"
        activated_ids = []
        deactive_ids = []
        for cid in range(1, max_id_num + 1):
            test.dut.at1.send_and_verify(f"AT+CGACT=1,{cid}", ok_or_error, timeout=30)
            if 'OK' in test.dut.at1.last_response:
                activated_ids.append(str(cid))
            else:
                if cid == ipv4_cid:
                    test.log.error("The only IPV4 context is not active.")
                deactive_ids.append(str(cid))
        return activated_ids, deactive_ids

        

if __name__=='__main__':
    unicorn.main()