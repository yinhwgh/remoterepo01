#responsible: lei.chen@thalesgroup.com
#location: Dalian
# TC0094490.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.status_control import sind_parameters
from dstl.status_control import extended_indicator_control
from dstl.status_control import check_sind_simdata
from dstl.network_service import register_to_network
from dstl.configuration import network_registration_status

class Test(BaseTest):
    """
    TC0094490.001 - TpAtSindSimdata
    Check the status of indicator "simdata" with AT^SIND command.
    debugged: Serval
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.info("1. Enable SAT SSTK URC ")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"SAT/URC\", \"1\""))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"SAT/URC\"", expect="\^SCFG: \"SAT/URC\",\"1\""))
        test.log.info("2. Activate \"Query USIM and Chip Card Holder Status\" with command (At^Scks=1)")
        test.expect(test.dut.at1.send_and_verify("At^Scks=1"))
        test.expect(test.dut.at1.send_and_verify("At^Scks?", expect="\^SCKS: 1,1"))
        test.log.info("3. Enable network status report with CREG=1")
        test.expect(test.dut.dstl_set_network_registration_urc("CS", urc_mode="1"))
        test.expect(test.dut.dstl_read_network_registration_state("CS", urc_mode="1", expected_state="\d"))
        test.log.info("4. simdata can be read from AT^SIND=? and AT^SIND?")
        test.expect(test.dut.at1.send_and_verify("At^SIND=?", expect="(simdata,(0,1))"))
        test.expect(test.dut.at1.send_and_verify("At^SIND?", expect="\^SIND: simdata,0\s+"))
        test.log.info("5. Check command AT^SIND is invalid")
        test.expect(test.dut.at1.send_and_verify("At^SIND", expect="ERROR"))
        test.log.info("6. Enable indicator of simdata")
        test.expect(test.dut.at1.send_and_verify("At^SIND=simdata,1", expect="\^SIND: simdata,1\s+"))
        test.expect(test.dut.at1.send_and_verify("At^SIND=simdata,2", expect="\^SIND: simdata,1\s+"))
        test.log.info("7. Input pin code")
        test.expect(test.dut.dstl_enter_pin())
        test.log.info("8. Testing simdata indicator: +CIEV: simdata,...")
        test.dut.dstl_sind_simdata_functionality(enable_sstk_urc=False)
        test.log.info("9. Error message displays when incorrect parameter value is sent")
        test.expect(test.dut.at1.send_and_verify("At^SIND=simdata,3", expect="CME ERROR: (invalid index|21)"))
        test.expect(test.dut.at1.send_and_verify("At^SIND=simdata,ab", expect="CME ERROR: (invalid index|21)"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"SAT/URC\", \"0\""))
        test.expect(test.dut.at1.send_and_verify("At^Scks=0"))
        test.expect(test.dut.at1.send_and_verify("At^SIND=simdata,0", expect="\^SIND: simdata,0\s+"))
if "__main__" == __name__:
    unicorn.main()