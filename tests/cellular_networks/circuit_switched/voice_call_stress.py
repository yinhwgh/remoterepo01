#responsible: hui.yu@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0086143.001, TC0086143.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import check_urc
from dstl.auxiliary.restart_module import dstl_restart
from dstl.call import setup_voice_call
from dstl.network_service import register_to_network

import random

class Test(BaseTest):
    """
    TC0086143.003 - TpVoiceCallStress
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        network_error = "Network is required for setting up calls."
        test.expect(test.dut.dstl_register_to_network(), critical=True, msg=network_error)
        test.expect(test.r1.dstl_register_to_network(), critical=True, msg=network_error)

    def run(test):
        test_loops = 3
        mo_call_count = 0
        mo_call_pass = 0
        mt_call_count = 0
        mt_call_pass = 0
        for dcs in range(1, test_loops + 1):
            call_type = random.randint(0,2)
            if call_type == 0:
                mo_module = test.dut
                mt_module = test.r1
                call_type = 'MO'
                mo_call_count += 1
            else:
                mo_module = test.r1
                mt_module = test.dut
                call_type = 'MT'
                mt_call_count += 1

            test.log.step(f"{dcs}/{test_loops} Setting up {call_type} call.")
            result = test.setup_voice_call(mo_module, mt_module)
            if result:
                if call_type == 'MO':
                    mo_call_pass += 1
                else:
                    mt_call_pass += 1

        test.log.info(f"***** Total {mo_call_count} MO voice calls were setup, {mo_call_pass} passed.")
        test.log.info(f"***** Total {mt_call_count} MT voice calls were setup, {mt_call_pass} passed.")


    def cleanup(test):
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()

    def setup_voice_call(test, mo_module, mt_module):
        result = True
        call_number = mt_module.sim.nat_voice_nr
        mo_module.at1.send_and_verify(f'ATD{call_number};', expect='OK')
        ring_received = mt_module.at1.wait_for('RING', timeout=30)
        retry = 0
        while not ring_received and retry < 3:
            test.log.info(f"Failed to setup call, maybe network issue, try again {retry + 1}/3.")
            mo_module.at1.send_and_verify(f'ATD{call_number};', expect='OK')
            ring_received = mt_module.at1.wait_for('RING', timeout=30)
        result &= ring_received
        if not ring_received:
            test.expect(ring_received, msg="Failed to setup voice call.")
            mo_module.dstl_release_call()
        else:
            result &= mt_module.at1.send_and_verify("ATA", "OK")
            test.sleep(2)
            result &= test.expect(mo_module.dstl_check_voice_call_status_by_clcc())
            result &= test.expect(mt_module.dstl_check_voice_call_status_by_clcc(is_mo=False))
            result &= test.expect(mo_module.dstl_release_call())
            result &= test.expect(mt_module.dstl_release_call())
        return result

if '__main__' == __name__:
    unicorn.main()
