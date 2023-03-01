# responsible: mariusz.znaczko@globallogic.com
# location: Koszalin
# TC0095598.002

# feature: LM0000029.001, LM0000032.001, LM0000033.001, LM0000040.001, LM0000057.001, LM0001216.001, LM0001218.001
# LM0001220.001, LM0001478.001, LM0003202.001, LM0003202.002, LM0003202.003, LM0005638.001, LM0005638.003
# LM0007422.001

import re
import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.call.setup_voice_call import dstl_release_call, dstl_setup_and_maintain_call, \
    dstl_voice_call_by_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

        dstl_detect(test.r1)
        dstl_get_imei(test.r1)

        dstl_register_to_network(test.dut)
        dstl_register_to_network(test.r1)

    def run(test):
        """
        Intention:
        Simple check of voice calls via atd (MO and MT). no special radio band selected,
        no switch between CSS and VoLTE
        Description:
        Make MO and MT calls. For atd all modifiers "T, !, W , @ , A, B, C, D " are checked.
        The module shall use the network, which is available. No selection of band or technology.
        """
        test_call_duration = 10

        test.log.step("Step 1: normal MO calls: DUT -> remote")
        test.expect(dstl_setup_and_maintain_call(test.dut, test.r1, duration=test_call_duration,
                                                 direction=0, number=test.r1.sim.nat_voice_nr))
        dstl_release_call(test.dut)

        test.log.step("Step 2: normal MT calls: remote -> DUT")
        test.expect(dstl_setup_and_maintain_call(test.dut, test.r1, duration=test_call_duration,
                                                 direction=1, number=test.dut.sim.nat_voice_nr))
        dstl_release_call(test.dut)

        test.log.step("Step 3: normal calls MO DUT -> remote with modifiers ")
        if ((re.search(test.dut.project, 'BOBCAT') and (
                (test.dut.step == '2') or (test.dut.step == '3')))):
            test.log.error(
                "Workaround for IPIS100264424 - Dialing modifiers of ATD are not ignored")
            test.log.info("Bobcat2 can't use modifier")
            test.expect(False)
            dialing_modifiers = ["", "", "", "", "", "", "", "", ""]
        elif re.search(test.dut.project, 'TIGER'):
            dialing_modifiers = ["W", ",", "T", "P"]
        elif re.search(test.dut.project, 'VIPER'):
            dialing_modifiers = [",", "T", "!", "W", "@", "P", "PA", "PB", "PC", "PD"]
        elif test.dut.platform == 'QCT':
            dialing_modifiers = [",", "T", "!", "W", "@", "A", "B", "C", "D"]
        else:
            dialing_modifiers = [",", "T", "!", "W", "@", ",", ",", ",", ","]
        modi = ""

        for idx in range(0, len(dialing_modifiers)):
            modi = modi + " - " + dialing_modifiers[idx]

        for idx in range(0, len(dialing_modifiers)):
            test.log.info("make call and use modifier =>" + dialing_modifiers[idx] + "<=")
            if 'P' in dialing_modifiers[idx]:
                nat_voice_nr_with_modifier = f'{test.r1.sim.nat_voice_nr}{dialing_modifiers[idx]}'
                test.expect(dstl_voice_call_by_number(test.dut, test.r1,
                                                      number=nat_voice_nr_with_modifier))
                dstl_release_call(test.dut)
            else:
                nat_voice_nr_with_modifier = f'{dialing_modifiers[idx]}{test.r1.sim.nat_voice_nr}'
                test.expect(dstl_voice_call_by_number(test.dut, test.r1,
                                                      number=nat_voice_nr_with_modifier))
                dstl_release_call(test.dut)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
