# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0104692.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_identification
from dstl.identification import get_imei
from dstl.identification import check_identification_ati


class Test(BaseTest):
    """
        TC0104692.001	TpIdentificationCommandsBasic
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):

        # Two loops for with and without pin
        for i in range(2):
            with_or_without = "without" if i == 0 else "with"
            if i == 1:
                test.expect(test.dut.dstl_enter_pin())
            step_no = i + 1
            test.log.step(f"Step {step_no}. Check Identification commands {with_or_without} pin input")
            test.log.step(f"Step {step_no}.1. Check ATI related commands {with_or_without} pin input")
            test.log.step(f"Step {step_no}.1.1. Check valid ATI related commands {with_or_without} pin input")

            pin_locked = True if i == 0 else False
            test.expect(test.dut.dstl_check_all_supported_atix_format(pin_locked))

            test.log.step(f"Step {step_no}.1.2. Check invalid ATI commands {with_or_without} pin input")
            test.expect(test.dut.at1.send_and_verify("ATI*", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("ATI123", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("ATIbac", "ERROR"))

            test.log.step(f"Step {step_no}.2. Check AT+CGMI and AT+GMI commands {with_or_without} pin input")
            manufacturer = test.dut.dstl_get_defined_manufacturer()
            test.expect(test.dut.at1.send_and_verify("AT+CGMI", f"\s+{manufacturer}\s+OK\s+"))
            cgmi_response = test.dut.at1.last_response.split('\r\n')[-1]
            test.expect(test.dut.at1.send_and_verify("AT+GMI", cgmi_response))

            test.expect(test.dut.at1.send_and_verify("AT+CGMI?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMI=1", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GMI?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GMI=1", "ERROR"))

            test.log.step(f"Step {step_no}.3. Check AT+CGMM and AT+GMM commands {with_or_without} pin input")
            # Product information has been validated when check ATI information
            test.expect(test.dut.at1.send_and_verify("AT+CGMM", "OK"))
            cgmm_response = test.dut.at1.last_response.split('\r\n')[-1]
            test.expect(test.dut.at1.send_and_verify("AT+GMM", cgmm_response))

            test.expect(test.dut.at1.send_and_verify("AT+CGMM?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMM=1", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GMM?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GMM=1", "ERROR"))

            test.log.step(f"Step {step_no}.4. Check AT+CGMR and AT+GMR commands {with_or_without} pin input")
            sw_revision = test.dut.dstl_get_defined_sw_revision()
            test.expect(test.dut.at1.send_and_verify("AT+CGMR", sw_revision + "\s+OK\s+"))
            cgmr_response = test.dut.at1.last_response.split('\r\n')[-1]
            test.expect(test.dut.at1.send_and_verify("AT+GMR", cgmr_response))

            test.expect(test.dut.at1.send_and_verify("AT+CGMR?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMR=1", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GMR?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GMR=1", "ERROR"))

            test.log.step(f"Step {step_no}.5. Check AT+CGSN and AT+GSN commands {with_or_without} pin input")
            test.expect(test.dut.at1.send_and_verify("AT+CGSN", "\s+\d{15}\s+OK\s+"))
            cgsn_response = test.dut.at1.last_response.split('\r\n')[-1]
            test.expect(test.dut.at1.send_and_verify("AT+GSN", cgsn_response))

            test.expect(test.dut.at1.send_and_verify("AT+CGSN?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CGSN=1", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GSN?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GSN=1", "ERROR"))

            test.log.step(f"Step {step_no}.6. Check AT+CIMI command {with_or_without} pin input")
            expect_imsi = "+CME ERROR: SIM PIN required" if i == 0 else "\s+\d{15}\s+OK\s+"
            test.expect(test.dut.at1.send_and_verify("AT+CIMI", expect_imsi))
            test.expect(test.dut.at1.send_and_verify("AT+CIMI?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CIMI=1", "ERROR"))

            test.log.step(f"Step {step_no}.7. Check AT+GCAP command {with_or_without} pin input")
            expect_gcap = "+CME ERROR: SIM PIN required" if i == 0 \
                else test.dut.dstl_get_defined_capatibilities_list() + '\s+OK\s+'
            test.expect(test.dut.at1.send_and_verify("AT+GCAP", expect_gcap))
            test.expect(test.dut.at1.send_and_verify("AT+GCAP?", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+GCAP=1", "ERROR"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
