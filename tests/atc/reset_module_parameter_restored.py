#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0071421.001, TC0071421.002

import unicorn
from core.basetest import BaseTest
import re
import random
import sys
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.configuration import powerup_parameters
from dstl.status_control import extended_indicator_control
from dstl.configuration import shutdown_smso
from dstl.configuration import set_autoattach
from dstl.packet_domain import ps_attach_detach
from dstl.auxiliary.devboard import devboard
from dstl.call.setup_voice_call import dstl_voice_call_by_number, dstl_release_call
from dstl.configuration import functionality_modes


class Test(BaseTest):
    """
        TC0071421.001 -  TpResetTheModule
        TC0071421.002 - TpResetTheModule
        Subscribers:
    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.info('****** Disable auto attach to avoiding impact to at+cgatt ******')
        test.dut.dstl_disable_ps_autoattach()
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())
        # default sind mode value for writing at^sind corresponding parameter value
        test.sind_mode = 1
        test.log.info("Preparations before tests start")
        test.dut.dstl_set_scfg_volatile_cfun_mode(mode=1)
        test.cmds_not_restored = []

    def run(test):
        reset_commands = test.dut.dstl_get_powerup_parameter_value()
        # Parameters that in different powerup mode value from other parameters
        if 'AT^SIND_mode_except' in reset_commands:
            test.sind_mode_exceptions =  reset_commands['AT^SIND_mode_except']
            reset_commands.pop('AT^SIND_mode_except')
        else:
            test.sind_mode_exceptions = []

        test.log.info("Test commands with reset value:")
        for atc, value in reset_commands.items():
            test.log.info(atc + ': ' + str(value))

        for atc, value in reset_commands.items():
            reset_value = value[0]
            if '_' in atc:
                variables = atc.split('_')
                command = variables[0]
                parameter = variables[1]
            else:
                command = atc
                parameter = ""
            test.log.step(f"{command} {parameter} - 1. Test power up value when module was just restarted")
            test.expect(test.read_command_value(command, parameter, expect_value=reset_value))

            test.log.step(f"{command} {parameter} - 2.  Update power up value to a different one")
            if len(value) > 2:
                update_value = random.choice(value[1:])
            elif len(value) > 1:
                update_value = value[1]
            else:
                test.log.info(f"No update value is defined for {command}, "
                              "maybe it has not write command. Skipped updating its value.")
                update_value = None
            if update_value:
                test.expect(test.write_command_value(command, parameter, update_value))
            else:
                update_value = reset_value # for comparing with read response

            test.log.step(f"{command} {parameter} - 3.  Checking parameter value after updating")
            test.expect(test.read_command_value(command, parameter, update_value))

        test.log.step("4. Restart module and enter pin")
        test.expect(test.restart_module())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.dut.at1.send_and_verify("AT+COPS?")

        for atc, value in reset_commands.items():
            reset_value = value[0]
            if '_' in atc:
                command = atc.split('_')[0]
                parameter = atc.split('_')[1]
            else:
                command = atc
                parameter = None
            test.log.step(f"{command} {parameter} - 5. After restarting module, updated value was restored to reset one.")
            if not test.expect(test.read_command_value(command, parameter, expect_value=reset_value)):
                test.cmds_not_restored.append({f'{command}_{parameter}': reset_value})

    def cleanup(test):
        if test.cmds_not_restored:
            test.log.info('Restore commands whose value is not reset after ME restart.')
            for cmd_item in test.cmds_not_restored:
                for cmd_param, reset_value in cmd_item.items():
                    cmd = cmd_param.split('_')[0]
                    param = cmd_param.split('_')[1]
                    if param:
                        test.dut.at1.send_and_verify(f'{cmd}="{param}",{reset_value}')
                    else:
                        test.dut.at1.send_and_verify(f'{cmd}={reset_value}')
        test.dut.at1.send_and_verify('AT+CGDCONT=10')
        test.dut.dstl_enable_ps_autoattach()
        test.expect(test.dut.dstl_restart())
        test.sleep(2)

    def read_command_value(test, command, parameter=None, expect_value=""):
        expect_value = test.format_value_according_to_type(expect_value)
        if not parameter:
            if 'swwan' in command.lower() and expect_value.startswith('0'):
                test.log.info("0 will not be returned for AT^SWWAN if no context is activated.")
                expect_response = "AT\^SWWAN\?\s+OK\s+"
            else:
                if "cemode" in command.lower():
                    test.dut.dstl_ps_attach()
                    test.sleep(2)
                expect_response = "{}: {}".format(command.upper().replace('AT^', '').replace('AT+', ''),
                                                  expect_value)
            read_result = test.dut.at1.send_and_verify("{}?".format(command), expect_response, "OK")
        elif command.lower() == "at^sind":
            if parameter.lower() == "mode" and re.match('\d', expect_value):
                read_result = test.read_sind_mode(expect_value)
            else:
                read_result = test.read_sind_parameter(parameter, expect_value)
        elif 'at^snfota' in command.lower():
            expect_response = f'SNFOTA: "{parameter}",{expect_value}'
            read_result = test.dut.at1.send_and_verify("{}?".format(command), expect_response, "OK")
        # "at^scfg", "at^sgpsc"
        else:
            read_result = test.read_scfg_parameter(parameter, expect_value, command=command)
        if not read_result:
            test.log.info(f'Expected value for {command}: "{parameter}" is {expect_value}.')
        return read_result

    def read_sind_mode(test, expect_value):
        test.log.info("Reading AT^SIND mode value.")
        test.dut.at1.send_and_verify("AT^SIND?", "OK")
        last_response = test.dut.at1.last_response
        sind_rows = last_response.split('\n')
        result = True
        for sind_row in sind_rows:
            sind_row = sind_row.strip()
            expect_sind_row = ""
            if "orpco" in sind_row:
                test.log.info("Skip checking mode value for orpco, since only mode 2 is valid for it.")
                continue
            for parameter in test.sind_mode_exceptions:
                if parameter in sind_row:
                    temp_expect_value = str(1^int(expect_value))
                    expect_sind_row = "^\^SIND:\s\w+,[{}],?.*".format(temp_expect_value)
                    break
            if not expect_sind_row:
                expect_sind_row = "^\^SIND:\s\w+,[{}],?.*".format(expect_value)
            if "^SIND: " in sind_row and "AT^SIND" not in sind_row:
                match_result = re.match(expect_sind_row, sind_row)
                if match_result:
                    test.log.info(f"PASS: {sind_row}")
                    result &= True
                else:
                    test.log.error(f"FAIL: {sind_row}, expect mode: {expect_value}")
                    result &= False
        return result

    def read_scfg_parameter(test, parameter, expect_value, command="AT^SCFG"):
        test.log.info("Test {} parameter with value {}".format(command, expect_value))
        read_succeed = test.dut.at1.send_and_verify("{}=\"{}\"".format(command, parameter), "OK")
        if read_succeed:
            last_response = test.dut.at1.last_response
            expect_response = "{}: \"{}\",{}".format(command.upper().replace("AT^", ""),
                                                         parameter, expect_value)
            return expect_response in last_response
        else:
            return False

    def read_sind_parameter(test, parameter, expect_value):
        test.log.info("Test AT^SIND parameter with value {}".format(expect_value))
        read_succeed = test.dut.at1.send_and_verify("at^sind?", "OK")
        if read_succeed:
            last_response = test.dut.at1.last_response
            expect_response = "\^SIND: {},[01],{}".format(parameter, expect_value)
            find_result = re.search(expect_response, last_response)
            return find_result
        else:
            return False

    def write_command_value(test, command, parameter=None, update_value=""):
        update_value = test.format_value_according_to_type(update_value)
        if not parameter:
            if "cmut" in command.lower():
                update_result = test.write_and_read_cmut_value(update_value)
            elif "swwan" in command.lower():
                update_result = test.write_swwan_value(update_value)
            else:
                update_result = test.dut.at1.send_and_verify("{}={}".
                                                             format(command, update_value), "OK")
            return update_result
        elif command.lower() == "at^sind":
            if parameter.lower() == "mode" and re.match('\d', update_value):
                sind_mode = update_value
                return test.write_sind_mode(sind_mode)
            else:
                return test.write_sind_parameter(parameter, test.sind_mode, update_value)
        elif command.lower() in ("at^scfg", "at^sgpsc", "at^snfota"):
            return test.write_scfg_parameter(parameter, update_value, command)
        else:
            test.expect(False, msg="Writing command for atc {0} parameter {1} is not defined.".format(command, parameter))

    def write_sind_mode(test, update_value):
        indicators = test.dut.dstl_get_all_indicators()
        update_result = True
        if not indicators:
            test.log.error("Cannot recognize response of AT^SIND?")
            return False
        else:
            test.log.info("Found parameters are: {}".format(indicators))
            for indicator in indicators:
                # only mode 2 is available for orpco
                if 'orpco' not in indicator:
                    if indicator in test.sind_mode_exceptions:
                        update_result &= test.expect(
                            test.dut.at1.send_and_verify(f"at^sind={indicator},{1^int(update_value)}",
                                                         "OK"))
                    else:
                        update_result &= test.expect(
                            test.dut.at1.send_and_verify(f"at^sind={indicator},{update_value}", "OK"))
            return update_result

    def write_sind_parameter(test, parameter, mode, update_value):
        test.log.info("Updating AT^SIND parameter {} with mode {}, value {}".format(parameter, mode, update_value))
        update_succeed = test.dut.at1.send_and_verify("at^sind={},{},{}".format(parameter, mode, update_value), "OK")

        return update_succeed

    def write_scfg_parameter(test, parameter, update_value, command="AT^SCFG"):
        test.log.info("Writing {} parameter {} with value {}".format(command, parameter, update_value))
        write_succeed = test.dut.at1.send_and_verify("{}=\"{}\",{}".format(command, parameter, update_value), "OK")
        return write_succeed

    def write_and_read_cmut_value(test, update_value):
        test.log.info("****** Setup Voice call for AT+CMUT ******")
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr))
        result = test.dut.at1.send_and_verify(f"AT+CMUT={update_value}", "OK")
        result &= test.dut.at1.send_and_verify(f"AT+CMUT?", "\+CMUT: {update_value}\s+OK")
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        return result

    def write_swwan_value(test, update_value):
        test.dut.at1.send_and_verify(f'AT+CGDCONT=10,"IPV4V6","{test.dut.sim.apn_v4}"')
        test.dut.at1.send_and_verify('AT+CGDCONT=?')
        test.sleep(2)
        return test.dut.at1.send_and_verify(f'AT^SWWAN={update_value},10')

    def restart_module(test):
        """
        For checking default <fun> value of AT+CFUN, cannot restart module by AT+CFUN=1,1
        """
        test.dut.dstl_shutdown_smso()
        test.sleep(5)
        power_on = test.dut.dstl_turn_on_igt_via_dev_board()
        try_power_on = 1
        while not power_on and try_power_on < 3:
            test.log.info(f"Power on module with IGT failed, try again - {try_power_on}.")
            test.sleep(2)
            power_on = test.dut.dstl_turn_on_igt_via_dev_board()
            try_power_on += 1
        return power_on

    def format_value_according_to_type(test, value):
        if isinstance(value, int):
            test.log.info(f"Value {value} is integer, not need to be quoted.")
            str_value = str(value)
        elif isinstance(value, tuple):
            str_value = ""
            for v in value:
                if isinstance(v, int):
                    str_value += str(v) + ','
                else:
                    str_value += '"' + v + '"' + ','
            str_value = str_value.strip(',')
        else:
            test.log.info(f"Value {value} is string, need to be quoted.")
            str_value = '"' + value + '"'
        return str_value

if "__main__" == __name__:
    unicorn.main()
