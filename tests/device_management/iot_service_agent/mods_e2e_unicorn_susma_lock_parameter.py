# responsible: johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-345 - LM0008378.001 Unicorn: Lock Functionality for LPAd Actions 

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.imei = test.dut.dstl_get_imei()
        test.available_devices = {
            "004401083893921": 360088,
            "004401083893855": 360088,
            "351562110230970": 475625,
        }
        test.spc_code = test.__get_spc_code(test.imei)

    def run(test):
        lock_mode = test.__get_lock_mode()
        test.__check_susma_output(lock_mode)

        if lock_mode == "LOCK":
            test.__update_lock_mode("UNLOCK", test.spc_code)
            lock_mode = test.__get_lock_mode()
            test.expect(lock_mode == "UNLOCK", critical=True, msg="Lock mode has not been set correctly")
            test.__check_susma_output(lock_mode)
        else:
            test.__update_lock_mode("LOCK", test.spc_code)
            lock_mode = test.__get_lock_mode()
            test.expect(lock_mode == "LOCK", critical=True, msg="Lock mode has not been set correctly")
            test.__check_susma_output(lock_mode)

        test.dut.dstl_restart()
        lock_mode_after_restart = test.__get_lock_mode()
        test.expect(lock_mode_after_restart == lock_mode)

        if lock_mode == "LOCK":
            test.__update_lock_mode("UNLOCK", test.spc_code)
            lock_mode = test.__get_lock_mode()
            test.expect(lock_mode == "UNLOCK", critical=True, msg="Lock mode has not been set correctly")
            test.sleep(10)
            test.__check_susma_output(lock_mode)
        else:
            pass

    def __get_lock_mode(test):
        test.dut.at1.send_and_verify('AT^SSECUG=Factory/Debug')
        match = '^SSECUG: "Factory/Debug"'
        lines = [line for line in test.dut.at1.last_response.splitlines() if match in line]
        *_, mode = lines[0].split(',')
        mode = mode.replace('"', '')

        return mode

    def __update_lock_mode(test, mode, spc_code):
        update_result = test.dut.at1.send_and_verify(f'at^ssecug=Factory/Debug,"{mode}",{spc_code}')
        test.expect(update_result)

    def __get_spc_code(test, imei):
        if imei in test.available_devices.keys():
            return test.available_devices[imei]
        else:
            default_spc_code = 360088
            test.log.warning(f"There is no SPC code related with imei {test.imei}. Proceeding with {default_spc_code}")
            return default_spc_code

    def __check_susma_output(test, lock_mode):
        test.dut.at1.send_and_verify('AT^SUSMA?')
        if lock_mode == "LOCK":
            not_allowed = ['Delete', 'Disable', 'Download', 'Enable']
            last_resp = test.dut.at1.last_response
            if any(word in last_resp for word in not_allowed):
                test.log.error(f"Should not be shown when mode is {lock_mode}")
                test.expect(False)
            else:
                test.expect(True)
        else:
            allowed = ['Delete', 'Disable', 'Download', 'Enable']
            last_resp = test.dut.at1.last_response
            if all(word in last_resp for word in allowed):
                test.expect(True)
            else:
                test.log.error(f"There is a missing output line when mode is {lock_mode}")
                test.expect(False)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
