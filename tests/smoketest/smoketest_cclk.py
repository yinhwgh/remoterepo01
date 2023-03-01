# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# TC0095319.001
# jira: xxx
# feature: LM0002573.001, LM0002573.002, LM0002573.003, LM0003209.001, LM0003209.002, LM0003209.004, LM0003359.001,
#   LM0003359.002, LM0004421.001, LM0004421.002, LM0004421.003, LM0004421.004, LM0004421.005

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.hardware import set_real_time_clock

import re


def own_restart(test):
    'extra restart rotine, because Tiger has no Mctest connected'
    'to call via test.own_restart()'

    if (re.search(test.dut.project, 'TIGER')):
        test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
        test.sleep(20)
        test.dut.at1.send_and_verify("ati", "MTK2")
        test.sleep(1)
        result = 1
    else:
        result = test.dut.dstl_restart()
    return result


class Test(BaseTest):

    def own_restart(test):
        'extra restart rotine, because Tiger has no Mctest connected'
        'to call via test.own_restart()'

        if (re.search(test.dut.project, 'TIGER')):
            test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
            test.sleep(20)
            test.dut.at1.send_and_verify("ati", "MTK2")
            test.sleep(1)
            result = 1
        else:
            result = test.dut.dstl_restart()
        return result

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()

    def run(test):
        """
        Intention:
        Simple check of the ati command with all parameters
        """
        test.log.step('Step 0: Start ')
        bTimeZoneInfomation = 0
        bResetTime = 0
        bNetworkTimeAfterRegister = 0
        bCtzuOnAfterRestart = 0

        # dummy = test.dut.sim.imsi
        # dummy2 = dummy[:5]
        # dummy= test.dut.sim.imsi
        # if ("26295" in test.dut.sim.imsi[:5]):
        #     test.log.info("aber sowas von")
        # else:
        #     test.log.info("nicht da")
        # if ("26293" in test.dut.sim.imsi[:5]):
        #     test.log.info("aber sowas von")
        # else:
        #     test.log.info("nicht da")

        # set some special functions for projects
        if (re.search(test.dut.project, 'DAHLIA|COUGAR|KOALA')):
            bTimeZoneInfomation = 1
            bResetTime = 1
        else:
            test.log.info("nicht da")

        # from 8.4.19 Test network Berlin send a SIP16 messages after register.
        # With these messages the time is also set
        if ("26295" in test.dut.sim.imsi[:5] and re.search(test.dut.project, 'BOBCAT|MIAMI|ZURICH')):
            bNetworkTimeAfterRegister = 1

        # switch of ctzu without check if it exist
        test.log.step('Step 1: switch of ctzu without check if it exist')
        test.dut.at1.send_and_verify("at+ctzu=0", "O")

        # restart module
        test.log.step('Step 2: restart module')
        test.own_restart()

        test.log.step('Step 3: set and check cclk')
        test.dut.at1.send_and_verify("at+cclk?", ".*CCLK: \".*\".*OK.*")
        # set CCLK to defined time
        if (bTimeZoneInfomation ==0):
            test.expect(test.dut.at1.send_and_verify("at+cclk=\"13/12/31,01:02:56\"", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk=\"13/12/31,01:02:56+00\"", "OK"))

        #  check CCLK
        if ( bResetTime ==1 ):
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \".*\".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk?","CCLK: \"13/12/31,01:02:5.*\".*OK.*"))

        #  enter pin
        test.log.step('Step 4: check cclk after PIN')
        test.expect(test.dut.dstl_enter_pin())
        # check cclk
        if ( bResetTime ==1 ):
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \".*\".*OK.*"))
        elif ( bCtzuOnAfterRestart ==1) :
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"\\d{2}/\\d{2}/\\d{2},\\d{2}:\\d{2}:\\d{2}\\+\\d{2}.*\".*OK.*"))
        elif ( bNetworkTimeAfterRegister == 1):
            test.log.com("SIP16 shall be received and Time shall be set automaticly, no check")
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"\\d{2}/\\d{2}/\\d{2},\\d{2}:\\d{2}:\\d{2}.*\".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"13/12/31,01:0.*\".*OK.*"))

        test.log.step('Step 5: set cclk')
        if (bTimeZoneInfomation ==0):
            test.expect(test.dut.at1.send_and_verify("at+cclk=\"14/12/31,02:05:00\"",".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk=\"14/12/31,02:05:00+00\"",".*OK.*"))

        test.own_restart()
        test.sleep(10)
        test.log.step('Step 6: check cclk')
        if (bResetTime==1):
            test.expect(test.dut.at1.send_and_verify("at+cclk?", "CCLK: \".*\"OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"14/12/31,02:0.*\".*OK.*"))

        test.log.step('Step 7: check cclk after network registration')
        test.expect(test.dut.dstl_enter_pin())
        #  check CCLK
        if ( bResetTime ==1 ):
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \".*\".*OK.*"))
        elif ( bCtzuOnAfterRestart ==1) :
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"\\d{2}/\\d{2}/\\d{2},\\d{2}:\\d{2}:\\d{2}\\+\\d{2}.*\".*OK.*"))
        elif ( bNetworkTimeAfterRegister == 1):
            test.log.com("SIP16 shall be received and Time shall be set automaticly, no check")
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"\\d{2}/\\d{2}/\\d{2},\\d{2}:\\d{2}:\\d{2}.*\".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"14/12/31,02:0.*\".*OK.*"))

        test.log.step('Step 8: set cclk')
        if ( bTimeZoneInfomation) :
            test.expect(test.dut.at1.send_and_verify("at+cclk=\"15/12/31,05:05:00+00\"", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk=\"15/12/31,05:05:00\"", "OK"))

        test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"15/12/31,05:05:0.*\".*OK"))

        test.log.step('Step 9: switch off module and wait 2 minutes')
        #      // switch off
        test.dut.at1.send_and_verify("at^smso")
        #      WmDevice.shutdownModule(_wm[wm1], _atCmdResult,_testProcedureResult);
        test.sleep(120)
        #   switch on
        #   extra handling for cougar must be adapted later
        #      if ( family.equals(EnumFamilyName.COUGAR) ) {
        #        String ver = mcTest.getVersion();// workaround for remote connection
        #        log(wm1, "McTest version = " + ver);
        #        if(ver.contentEquals("V3"))
        #        {
        #          mcTest.setEMERGOFF(50);
        #          Thread.sleep(2000);
        #        }
        #        else
        #        {
        #          //atCmd(mct, "AT", ".*OK.*") // workaround for remote connection
        #          mcTest.switchRelais(1,"0");
        #          //atCmd(mct, "AT^Mcrelais=1,0", ".*OK.*");
        #          Thread.sleep(2000);
        #          mcTest.setEMERGOFF(1);
        #          //atCmd(mct, "mc:emrg=1", ".*OK.*");
        #          Thread.sleep(2000);
        #          mcTest.setEMERGOFF(1);
        #          //atCmd(mct, "mc:emrg=0", ".*OK.*");
        #          Thread.sleep(2000);
        #          mcTest.switchRelais(1,"1");
        #          //atCmd(mct, "AT^Mcrelais=1,1", ".*OK.*");
        #          Thread.sleep(2000);
        #        }
        #      }

        test.dut.dstl_turn_on_igt_via_dev_board(igt_time = 1500)
        test.sleep(60)
        #        if ( family.equals(EnumFamilyName.COUGAR) ) atCmd(wm1, "at+cfun=1", ".*OK.*", 5);
        #        Thread.sleep(5000);

        test.log.step('Step 10: check cclk after moduel start')
        # check cclk
        if ( bResetTime ==1 ):
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \".*\".*OK.*"))
        elif ( bNetworkTimeAfterRegister == 1):
            test.log.com("SIP16 shall be received and Time shall be set automaticly, no check")
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"\\d{2}/\\d{2}/\\d{2},\\d{2}:\\d{2}:\\d{2}.*\".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"15/12/31,05:08:[01].*\".*OK.*"))
        #      // check CCLK
        #
        test.expect(test.dut.dstl_enter_pin())
        test.log.step('Step 11: check cclk after network registration')
        # check cclk
        if ( bResetTime ==1 ):
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \".*\".*OK.*"))
        elif ( bNetworkTimeAfterRegister == 1):
            test.log.com("SIP16 shall be received and Time shall be set automaticly, no check")
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"\\d{2}/\\d{2}/\\d{2},\\d{2}:\\d{2}:\\d{2}.*\".*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cclk?",".*CCLK: \"15/12/31,05:08.*\".*OK.*"))

        test.log.step('Step end')

    def cleanup(test):
        """Cleanup method.
		Nothing to do in this Testcase
        Steps to be executed after test run steps.
        """
        test.dut.dstl_set_real_time_clock()

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
