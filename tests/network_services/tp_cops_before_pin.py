# responsible: johann.suhr@thalesgroup.com
# location: Berlin
# TC: TC0088045.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary.devboard import devboard
from dstl.network_service import register_to_network


class Test(BaseTest):
    """ TpCopsBeforePin """

    def setup(test):
        test.dut.dstl_detect()
        # Remove SIM
        test.dut.dstl_remove_sim()
        pass

    def run(test):
        # Enable creg indication with at+creg=2.
        test.dut.at1.send_and_verify('at+creg=2')

        # Enable text error message format.
        test.dut.at1.send_and_verify('at+cmee=2')

        # Check at+cops=? ----> ERROR_SIM_NOT_INSERTED.
        test.dut.at1.send_and_verify('at+cops=?', expect='+CME ERROR: SIM not inserted')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM not inserted' in last_response)

        # Check at+cops? ----> ERROR_SIM_NOT_INSERTED.
        test.dut.at1.send_and_verify('at+cops?', expect='+CME ERROR: SIM not inserted')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM not inserted' in last_response)

        # Check at+cops ----> ERROR_SIM_NOT_INSERTED.
        test.dut.at1.send_and_verify('at+cops', expect='+CME ERROR: SIM not inserted')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM not inserted' in last_response)

        # Check at+cops=2 ----> ERROR(deregestering not allowed in restricted mode).
        test.dut.at1.send_and_verify('at+cops=2', expect='+CME ERROR: SIM not inserted')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM not inserted' in last_response)

        # Check at+cops=3,1 ---> ERROR.
        test.dut.at1.send_and_verify('at+cops=3,1', expect='+CME ERROR: SIM not inserted')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM not inserted' in last_response)

        # Check at+cops=3,2 ---> ERROR.
        test.dut.at1.send_and_verify('at+cops=3,2', expect='+CME ERROR: SIM not inserted')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM not inserted' in last_response)

        # Check at+cops=0 ---> OK.
        test.dut.at1.send_and_verify('at+cops=0', expect='OK')
        last_response = test.dut.at1.last_response
        test.expect('OK' in last_response)

        # Check at+cops=2 ---> ERROR INVALID_INDEX.
        test.dut.at1.send_and_verify('at+cops=2', expect='ERROR')
        last_response = test.dut.at1.last_response
        test.expect('ERROR' in last_response)

        # Check at+cops=1,2,26301 ---> OK.
        test.dut.at1.send_and_verify('at+cops=1,2,26201', expect='OK')
        last_response = test.dut.at1.last_response
        test.expect('OK' in last_response)

        # Insert SIM with PIN1 enabled(PIN required). No Telekom SIM.
        test.dut.dstl_insert_sim()

        # check at+cops=?  ----> ERROR SIM_PIN_REQUIRED
        test.dut.at1.send_and_verify('at+cops=?', expect='+CME ERROR: SIM PIN required')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM PIN required' in last_response)

        # check at+cops?  ----> ERROR SIM_PIN_REQUIRED
        test.dut.at1.send_and_verify('at+cops?', expect='+CME ERROR: SIM PIN required')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM PIN required' in last_response)

        # check at+cops  ----> ERROR SIM_PIN_REQUIRED
        test.dut.at1.send_and_verify('at+cops', expect='+CME ERROR: SIM PIN required')
        last_response = test.dut.at1.last_response
        test.expect('+CME ERROR: SIM PIN required' in last_response)

        # Check at+cops=0 ---> OK.
        test.dut.at1.send_and_verify('at+cops=0', expect='OK')
        last_response = test.dut.at1.last_response
        test.expect('OK' in last_response)

        # Check at+cops=2 ---> ERROR INVALID_INDEX.
        test.dut.at1.send_and_verify('at+cops=2', expect='ERROR')
        last_response = test.dut.at1.last_response
        test.expect('ERROR' in last_response)

        # Check at+cops=1,2,26301 ---> OK.
        test.dut.at1.send_and_verify('at+cops=1,2,26201', expect='OK')
        last_response = test.dut.at1.last_response
        test.expect('OK' in last_response)

        # Enter Pin 1.
        test.dut.at1.send_and_verify(r'at+cpin="PIN1"')
        test.dut.at1.wait_for(r'+CREG:3')
        test.expect('+CREG:3' in last_response)

        # Enter at+cops=0.
        test.dut.at1.send_and_verify('at+cops=0')
        test.dut.at1.wait_for(r'+CREG:1')
        test.expect('+CREG:1' in last_response)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
