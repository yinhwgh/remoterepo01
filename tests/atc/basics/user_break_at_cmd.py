#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC: TC0087865.001, TC0104116.002

#Precondition: for all ports that support at commands, should be configured to dut_at1, dut_at2, dut_at3


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.call import setup_voice_call
from dstl.sms import select_sms_format
from dstl.sms import sms_center_address
from dstl.sms import send_sms_message
from dstl.sms import write_sms_to_memory
from dstl.sms import sms_configurations
from dstl.sms import delete_sms
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim



class Test(BaseTest):
    '''
    TC0087865.001 - UserBreakAtCmd
    TC0104116.002 - userBreakCmdsStress
    Intention:
    The goal of this test case is to verify the "user break" mechanism when interactions 
    with the network are involved or for long running AT commands.
    Subscribers: 2
    :param : parameter loop_times should be past from campaign file.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.expect(test.dut.dstl_set_preferred_sms_memory())
        # Key is command to be tested, value is a list containing two items 
        # - the first one stands for detail at command to be interrupted
        # - the second is precondition command which should be executed before tested ATC
        # Call and SMS related ATCs are not included in the dict and will be tested
        test.AT_CMD_MAP = {
            'AT+COPS': ['AT+COPS=?',''],
            'AT^SPOS': ['AT^SPOS=?',''],
            'AT+COPN': ['AT+COPN',''],
            'AT+CPOL': ['AT+CPOL?',''],
            'AT+CLCK': [f'AT+CLCK="SC",1,"{test.dut.sim.pin1}"', f'AT+CLCK="SC",0,"{test.dut.sim.pin1}"'],
            'AT+CLIP': ['AT+CLIP',''],
            'AT+CLIR': ['AT+CLIR',''],
            'AT+CCFC': ['AT+CCFC=4,4', ''],
            'AT+CCWA': ['AT+CCWA=1,1,1', ''],
            'AT+CUSD': ['AT+CUSD=1,1', 'AT+CUSD=0'],
            'AT+CGATT': ['AT+CGATT=1', ''],
            'AT+CGDCONT': [f'AT+CGDCONT=1,"IP","{test.dut.sim.apn_v4}"', ''],
            'AT+CGACT': ['AT+CGACT=1,1', 'AT+CGACT=0,1']
        }

    def run(test):
        # All available ports should be configured to local.cfg
        test.test_ports = [test.dut.at1]
        if test.dut.at2 and test.dut.at2.send_and_verify("AT", ".*OK.*"):
            test.test_ports.append(test.dut.at2)
            test.log.info(f"Port {test.dut.at2.name} is available.")
        if test.dut.at3 and test.dut.at3.send_and_verify("AT", ".*OK.*"):
            test.test_ports.append(test.dut.at3)
            test.log.info(f"Port {test.dut.at3.name} is available.")

        # Since not all DSTLs preserve parameter for sending port interface
        # Will update test.dut.at1 to the port to test
        # So save original test.dut.at1 configuration and recover in the end is necessary
        if len(test.test_ports) >1:
            test.original_dut_at1 = test.dut.at1
        else:
            test.original_dut_at1 = None

        for test.test_port in test.test_ports:
            test.log.info(f"**************** Start tests for {test.test_port.name} ****************")
            test.dut.at1 = test.test_port
            for test.loop in range(test.loop_times):
                test.log.info("Delete all SMS before tests.")
                test.expect(test.dut.dstl_delete_all_sms_messages())
                test.log.step(f"Port {test.test_port.name} loop {test.loop + 1} 1. Test breaking for common AT commands.")
                test.broken_cmds = []
                test.ok_cmds = []
                i = 1
                for at_cmd, cmd_list in test.AT_CMD_MAP.items():
                    test.log.step(f"Port {test.test_port.name} loop {test.loop + 1} 1.{i} Test breaking {at_cmd}.")
                    test.test_breaking_common_command(test.test_port, cmd_list[0], cmd_list[1])
                    i += 1

                test.log.step(f"Port {test.test_port.name} loop {test.loop + 1} 2. Test breaking for Call related AT commands.")
                test.test_breaking_call_command(test.test_port)
                    
                test.log.step(f"Port {test.test_port.name} loop {test.loop + 1} 3. Test breaking for SMS related AT commands.")
                test.test_breaking_sms_command(test.test_port)

                test.log.info(f"*** For port {test.test_port.name}, loop {test.loop + 1}: Broken successfully cmds: {test.broken_cmds}.")
                test.log.info(f"*** For port {test.test_port.name}, loop {test.loop + 1}: Broken but returned OK cmds: {test.ok_cmds}.")

            test.log.info(f"**************** End tests for {test.test_port.name} ****************")

    def cleanup(test):
        if test.original_dut_at1:
            test.dut.at1 = test.original_dut_at1
        test.expect(test.dut.at1.send_and_verify("AT+CUSD=0"))
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def test_breaking_call_command(test, port):
        test.log.step(f"Port {port.name} loop {test.loop + 1} 2.1 Test breaking call related command ATD.")
        test.test_breaking_common_command(port, f"ATD\"{test.r1.sim.nat_voice_nr}\";", None)
        test.expect(test.dut.dstl_release_call())
        test.sleep(1)

        test.log.step(f"Port {port.name} loop {test.loop + 1} 2.2 Test breaking CALL related command ATA.")
        test.expect(test.r1.at1.send_and_verify(f"ATD\"{test.dut.sim.nat_voice_nr}\";"))
        ring = port.wait_for("RING", timeout=30)
        try_call = 1
        while not ring and try_call < 3:
            test.log.info(f"Call failed, try again - {try_call}.")
            test.r1.dstl_release_call()
            test.sleep(5)
            test.r1.at1.send_and_verify(f"ATD\"{test.dut.sim.nat_voice_nr}\";")
            ring = port.wait_for("RING", timeout=30)
            try_call += 1
        else:
            if ring == True:
                test.test_breaking_common_command(port, "ATA", None)
            else:
                test.expect(ring, msg="Fail to call dut from remote. Skip tests for ATA.")
        test.expect(test.r1.dstl_release_call())
        test.sleep(1)
        
        
        test.log.step(f"Port {port.name} loop {test.loop + 1} 2.3 Test breaking CALL related command AT+CLCC.")
        test.expect(port.send_and_verify(f"ATD\"{test.r1.sim.nat_voice_nr}\";"))
        test.expect(test.r1.at1.wait_for("RING"))
        test.test_breaking_common_command(port, "AT+CLCC", None)
        test.expect(test.dut.dstl_release_call())
        test.sleep(1)

        test.log.step(f"Port {port.name} loop {test.loop + 1} 2.4 Test breaking CALL related command AT+CHLD.")
        test.expect(test.r1.at1.send_and_verify(f"ATD\"{test.dut.sim.nat_voice_nr}\";"))
        ring = port.wait_for("RING")
        if ring == True:
            test.test_breaking_common_command(port, "AT+CHLD=2", None)
        else:
            test.expect(ring, msg="Fail to call dut from remote. Skip tests for AT+CHLD.")
        test.expect(test.r1.dstl_release_call())
        test.sleep(1)

    def test_breaking_sms_command(test, port):
        test.log.info("Preconditions for sending SMS.")
        test.expect(port.send_and_verify("AT+CMGF=1"))
        test.expect(port.send_and_verify("AT+CMGF?"))
        test.expect(test.dut.dstl_set_sms_center_address())
        test.expect(test.dut.dstl_set_preferred_sms_memory("SM"))
        sms_index = test.dut.dstl_write_sms_to_memory("This is the SMS to be sent from Storage.", return_index=True)
        i = 0
        while not sms_index and i < 3:
            test.log.warning(f"Fail to write message to memory, try the {i+2}th time.")
            sms_index = test.dut.dstl_write_sms_to_memory(
                "This is the SMS to be sent from Storage.", return_index=True)
            i += 1
        # A workaroud for converting return index from list type to integer. Should be removed once DSTL is fixed.
        if isinstance(sms_index, list) and len(sms_index)>0:
            sms_index = sms_index[0]
        else:
            sms_index = 1

        test.log.step(f"Port {port.name} loop {test.loop + 1} 3.1 Test breaking SMS related command AT+CMGS.")
        test.test_breaking_common_command(port, "AT+CMGS", None)
        

        test.log.step(f"Port {port.name} loop {test.loop + 1} 3.2 Test breaking SMS related command AT+CMSS.")
        test.test_breaking_common_command(port, f"AT+CMSS={sms_index}", None)

    def test_breaking_common_command(test, port, cmd, precondition_cmd):
        """Test if at command can be broken by "AT" 

        Args:
            port : the port to send command, e.g. test.dut.at1, test.dut.at2
            cmd (string): at command to be interrupted.
            precondition_cmd (string): at command should executed before executing <cmd>.
        """
        if precondition_cmd:
            test.log.info(f"Execute precondition command {precondition_cmd} for {cmd}.")
            set_precondition = port.send_and_verify(precondition_cmd)
            if not set_precondition:
                test.log.warning(f"Fail to set precondition for {cmd}, ")
        
        if "AT+CMGS" in cmd:
            test.expect(port.send_and_verify(f"AT+CMGS=\"{test.r1.sim.nat_voice_nr}\"", ">", wait_for=">"))
            port.send("This is the SMS for testing breaking AT+CMGS.", end="[CTRL+Z]")
        else:
            port.send(cmd, wait_after_send=0.2)
        port.send_and_verify("AT", ".*OK|ERROR|NO CARRIER.*", wait_for=".*OK|ERROR|NO CARRIER.*", append=False)
        last_response = port.last_response
        if "+CME ERROR: unknown" in last_response or ("ATA" in cmd and "NO CARRIER" in last_response):
            test.expect("+CME ERROR: unknown" in last_response or "NO CARRIER" in last_response)
            test.log.info(f"Command {cmd} was broken successfully and ERROR was returned")
            test.broken_cmds.append(cmd)
        elif "OK" in last_response:
            test.expect("OK" in last_response)
            test.log.info(f"Command {cmd} was NOT broken - module responded too quickly - That is correct behavior.")
            test.ok_cmds.append(cmd)
        else:
            test.expect("OK" in last_response,
                        msg=f"Command {cmd} was neither interrupted nor returned OK.")
            
 
    
if __name__=='__main__':
    unicorn.main()
