#responsible: qingsong.kong@thalesgroup.com
#location: Beijing
# TC0093043.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class EMERG_RST_IdleState(BaseTest):
    """
    TC0093043.001 - OverUnderTemShutdownBasic

    Pre condition A module the over-/undertemperature shutdown behavior has never been disabled.

    Please note: the above precondition is mandatory for this test case, if the over-/undertemperature shutdown behavior of your module was ever disabled,
     you can erase whole flash of the module and update a new firmware

    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):

        test.log.info("== Check if module support  MEopMode/ShutdownOnCritTemp==")
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"','SCFG: "MEopMode/ShutdownOnCritTemp","on","on"'))
        test.log.info("If return is on off or off off ,It means this module's overundertemperature shutdown behavior has never been disabled.\nYou can erase whole flash of the module and update a new firmware")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","off"', 'SCFG: "MEopMode/ShutdownOnCritTemp","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"', 'SCFG: "MEopMode/ShutdownOnCritTemp","off","off"'))
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"', 'SCFG: "MEopMode/ShutdownOnCritTemp","off","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","on"', 'SCFG: "MEopMode/ShutdownOnCritTemp","on"'))
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"','SCFG: "MEopMode/ShutdownOnCritTemp","on","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SRTEH="temp"',
                                                 'SRTEH: "",""'))



        test.log.info("==Check invalid parameters for the write command.==")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp",in ',
                                                 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="MEopMode/ShutdownOnCritTemp","1","on" ',
                                                 'ERROR'))

        test.log.info('==Check if the command can be executed  with PIN==')
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","on"', 'SCFG: "MEopMode/ShutdownOnCritTemp","on"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","off"', 'SCFG: "MEopMode/ShutdownOnCritTemp","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"', 'SCFG: "MEopMode/ShutdownOnCritTemp","off","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","on"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","on"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","on","off"'))
        test.log.info('==Check if the command can be executed  under AIRPLANE MODE==')
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+CFUN=4'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","on"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","on"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","off"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","off","off"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","on"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","on"'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"',
                                             'SCFG: "MEopMode/ShutdownOnCritTemp","on","off"'))


    def cleanup(test):
        pass

if "__main__" == __name__:
        unicorn.main()
