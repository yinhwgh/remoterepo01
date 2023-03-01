# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0104084.003

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.dual_sim_operation import dstl_enable_dual_sim_mode, \
    dstl_disable_dual_sim_mode, dstl_switch_to_sim_slot1, dstl_switch_to_sim_slot2


class Test(BaseTest):


    def setup(test):
        """
        1. Activate dual SIM mode by command: AT^SCFG="SIM/DualMode","2"
        2. Set first SIM slot as currently interface using: AT^SCFG="SIM/CS","SIM1"
        3. Set second SIM slot as currently interface using: AT^SCFG="SIM/CS","SIM3"
        4. Return to first SIM slot.
        """
        dstl_detect(device=test.dut)
        dstl_get_imei(device=test.dut)

    def run(test):
        test.log.step('1. Activate dual SIM mode by command: AT^SCFG="SIM/DualMode","2"')
        test.expect(dstl_enable_dual_sim_mode(device=test.dut, mode=2))

        test.log.step('2. Set first SIM slot as currently interface using: AT^SCFG="SIM/CS","SIM1"')
        test.expect(dstl_switch_to_sim_slot1(device=test.dut))

        test.log.step('3. Set second SIM slot as currently interface using: '
                      'AT^SCFG="SIM/CS","SIM3"')
        test.expect(dstl_switch_to_sim_slot2(device=test.dut))

        test.log.step('4. Return to first SIM slot.')
        test.expect(dstl_switch_to_sim_slot1(device=test.dut))

    def cleanup(test):
        test.expect(dstl_disable_dual_sim_mode(device=test.dut))


if "__main__" == __name__:
    unicorn.main()

