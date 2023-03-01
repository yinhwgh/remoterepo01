# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107236.001 - NmeaOutputDuration
# intention: enable NMEA output, but keep NMEA port closed for over 1 hour. Check if module does not crash,
#            see IPIS100193076 COmega: EXIT after about 1 hours during GPS engine switch ON and NMEA port not opened
# prerequisites: at lest 2 port of dut (dut_at1, dut_nmea, roof Antenna or SMBV
# execution time: >=1 hour


import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    OK_counter = 0
    ERR_counter = 0
    number_of_rate_meas = 0

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()
        pass

    def run(test):
        duration_time = {}

        test.log.step('Step 1: Initialise GNSS engine to default setting, check if NMEA output appears - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Urc\",\"on\"", ".*OK.*")
        test.log.step('Step 1: Switch on GNSS engine - Start')
        test.dut.dstl_switch_on_engine()

        test.dut.nmea.read()
        ret = test.dut.nmea.wait_for(".*G[NP]GGA.*", 10)
        test.dut.nmea.read()
        # test.dut.nmea.wait_for("GNGSA", 10)

        if not ret:
            test.expect(False, critical=True, msg=" NMEA sentence expected, but not found on dut_nmea port - ABORT!")

        test.dut.dstl_switch_off_engine()

        test.log.step('Step 2: real test: close NMEA port, enable GNSS again and wait a long time')
        test.dut.nmea.close()
        test.dut.dstl_switch_on_engine()
        # wait a long time - test case says: 1 hour
        test.sleep(60)
        # check if module is still working:
        test.dut.dstl_restart_and_sgpsc_check(restart=False)

        test.dut.nmea.open()
        last_nmea_data = test.dut.nmea.read()

        test.log.info(f'buffered response from closed port was:\r\n{last_nmea_data}')

        test.log.step('Step 9: main test finished')
        pass

    def cleanup(test):
        if test.smbv_active is True:
            test.smbv.dstl_smbv_close()

        test.dut.nmea.open()
        test.dut.at1.send_and_verify("ati1")

        test.log.step('Step 9: Switch off GNSS engine')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())
        test.dut.dstl_nmea_disable_interface()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
