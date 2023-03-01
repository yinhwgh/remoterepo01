# responsible: marcin.kossak@globallogic.com
# location: Wroclaw
# TC0095391.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_radio_band import dstl_check_all_radio_bands, \
    dstl_save_current_radio_bands_setting, dstl_restore_current_radio_bands_setting, RadioBandBackup
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    Smoke test for all available bands
    """
    JIRA_ID = 'TC0095391.001'
    radio_bands_backup: RadioBandBackup
    SCENARIO: str = '''Scenario:
            1. set all available Radio/Band combinations
            2. check only the combinations, which are allowed
            3. TC will not check, if the module can register on the set Radio/Band

            NOTE: all available single Radio/Band combinations for module are checked
                    and at the end there is additional one to check sum of all.'''

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        status, test.radio_bands_backup = dstl_save_current_radio_bands_setting(test.dut)
        test.log.info('Backup of existing Radio Bands were saved')
        test.expect(status)

    def run(test):
        """
        Scenario:
            1. set all available Radio/Band combinations
            2. check only the combinations, which are allowed
            3. TC will not check, if the module can register on the set Radio/Band

            NOTE: all available single Radio/Band combinations for module are checked
                    and at the end there is additional one to check sum of all.
        """
        test.log.info(test.SCENARIO)
        status, band_statuses = dstl_check_all_radio_bands(test.dut)
        test.expect(status, msg='Not all Bands were set correctly')
        test.log.info('Summary of band operations:')
        for step_status, step_message in band_statuses:
            test.log.info(step_message.splitlines()[0])
            test.expect(step_status, msg=step_message)

    def cleanup(test):
        test.log.info('Restore Backup Radio Bands was done')
        test.expect(dstl_restore_current_radio_bands_setting(test.dut, test.radio_bands_backup))


if __name__ == "__main__":
    unicorn.main()
