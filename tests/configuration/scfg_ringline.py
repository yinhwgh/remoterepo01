#responsible: lijuan.li@thalesgroup.com
#location: Beijing
#TC

import unicorn
import tkinter
import tkinter.messagebox

from core.basetest import BaseTest

from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.delete_sms import dstl_delete_all_sms_messages

class TpAtScfgRingline(BaseTest):
    def setup(test):
        test.dut.detect()
        test.log.info("******1. Restore to default configurations******")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*(OK|ERROR).*", timeout=30))
        test.log.info("*******************************************************************\n\r")
        test.log.info("******2. Enable SIM PIN lock before testing******")
        test.expect(test.dut.dstl_lock_sim())
        test.dut.dstl_restart()
        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):
        # AT^SCFG= "URC/Ringline"[,<urcRinglineCfg>]
        # AT^SCFG= "URC/Ringline/ActiveTime"[,<urcRinglineDuration>]
        urcRinglineCfg=['off','local','asc0']
        urcRinglineDuration=['0','1','2']

        test.log.info("******1. test: Check supported parameters and values of Ringline Configuration and Duration******")
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*{}[\S\s]*{}[\S\s]*OK.*'.format(
            'SCFG: "URC/Ringline",\("off","local","asc0"\)', '\^SCFG: "URC/Ringline/ActiveTime",\("0","1","2"\)')))
        test.log.info("*******************************************************************\n\r")

        test.log.info("******2. test: check illegal parameters******")
        test.log.info("******2.1 test: URC/Ringline - illegal parameters******")
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","0"'),".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","*"'),".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","ASC1"'), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","null"'), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","on"'), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","USB"'), ".*ERROR.*"))

        test.log.info("******2.1 test: URC/Ringline/ActiveTime - illegal parameters******")
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","3"'),".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","11"'),".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","000000"'), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","5"'), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime",""'), ".*ERROR.*"))

        test.log.info("******3. test: check all parameters - should be non volatile******")
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","off"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "URC/Ringline"', '.*{}.*.OK.*'.format(
            '\^SCFG: "URC/Ringline","off"')))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","local"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "URC/Ringline"', '.*{}.*.OK.*'.format(
            '\^SCFG: "URC/Ringline","local"')))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","asc0"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "URC/Ringline"', '.*{}.*.OK.*'.format(
            '\^SCFG: "URC/Ringline","asc0"')))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","0"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "URC/Ringline/ActiveTime"', '.*{}.*.OK.*'.format(
            '\^SCFG: "URC/Ringline/ActiveTime","0"')))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","1"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "URC/Ringline/ActiveTime"', '.*{}.*.OK.*'.format(
            '\^SCFG: "URC/Ringline/ActiveTime","1"')))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","2"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG= "URC/Ringline/ActiveTime"', '.*{}.*.OK.*'.format(
            '\^SCFG: "URC/Ringline/ActiveTime","2"')))

        test.log.info("******4. Function test: disable URC-RI-Line on all interfaces ******")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","off"'), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","0"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify((r'AT+CNMI=2,1'), ".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("mc:urc=on", ".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("mc:time=on", ".*OK.*"))
        test.expect(test.dut.dstl_delete_all_sms_messages())
        tkinter.messagebox.showwarning('TIP','Please check if no RING0 pulse')
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","1"'), ".*OK.*"))
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","2"'), ".*OK.*"))
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        #test.expect(test.dut.devboard.wait_for(".*Ringline.*", timeout=90,append=True))


        test.log.info("******5. Function test: enable URC-RI-Line LOCAL - only where the URC appears ******")
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline","local"'), ".*OK.*"))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","0"'), ".*OK.*"))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify((r'AT+CNMI=2,1'), ".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("mc:urc=on", ".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("mc:time=on", ".*OK.*"))
        test.expect(test.dut.dstl_delete_all_sms_messages())
        tkinter.messagebox.showwarning('TIP','Please check if RING0 pulse about 7ms')
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","1"'), ".*OK.*"))
        tkinter.messagebox.showwarning('TIP', 'Please check if RING0 pulse about 20ms')
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at1.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","2"'), ".*OK.*"))
        tkinter.messagebox.showwarning('TIP', 'Please check if RING0 pulse about 1s')
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.int_voice_nr))

        test.log.info("******6. Function test: URC appears on ASC1, local setting is ASC0: no RING activity ******")
        test.expect(test.dut.at2.send_and_verify((r'AT^SCFG="URC/Ringline","off"'), ".*OK.*"))
        test.expect(test.dut.at2.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","0"'), ".*OK.*"))
        test.dut.at2.dstl_restart()
        test.expect(test.dut.at2.dstl_register_to_network())
        test.expect(test.dut.at2.send_and_verify((r'AT+CNMI=2,1'), ".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("mc:urc=on", ".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("mc:time=on", ".*OK.*"))
        test.expect(test.dut.at2.dstl_delete_all_sms_messages())
        tkinter.messagebox.showwarning('TIP','Please check if no RING0 pulse')
        test.expect(test.dut.at2.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at2.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","1"'), ".*OK.*"))
        test.expect(test.dut.at2.dstl_send_sms_message(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at2.send_and_verify((r'AT^SCFG="URC/Ringline/ActiveTime","2"'), ".*OK.*"))
        test.expect(test.dut.at2.dstl_send_sms_message(test.dut.sim.int_voice_nr))

        def cleanup(test):
            pass

    if (__name__ == "__main__"):
        unicorn.main()
