# responsible: lijuan.li@thalesgroup.com
# location: Beijing
# TC0104441.001
# update by: christoph.dehm@thalesgroup.com
# note: test was created on McTv4 and Serval04_400_006+ rebased on Serval03 merge

import unicorn
import time

from core.basetest import BaseTest
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class TpAtSMSOFastshutdown(BaseTest):
    wforsysstarttimer = 60
    time1 = 0

    def check_timing(test, teststep="", maxduration=10):
        if teststep == "":
            teststep = "general time measuring"

        time2 = time.perf_counter()
        # print("T1", time1, "T2", time2, "diff", (time2-time1) )
        duration = time2 - test.time1
        resultmsg = teststep, "was: {:.1f} sec.".format(duration)
        if duration > maxduration:
            resultmsg = resultmsg, "is bigger than " + str(maxduration) + " sec. - FAILED"
            test.log.critical(resultmsg)
            return -1
        else:
            resultmsg = resultmsg, "is lower than " + str(maxduration) + " sec. as expected."
            test.log.info(resultmsg)
        return 0

    def close_port_if_usb(test):
        if "usb" in test.dut.at1.name:
            test.dut.at1.close()
        pass

    def wait_for_sysstart_or_delay(test, wforsysstarttimer):
        if "usb" in test.dut.at1.name:
            time.sleep(wforsysstarttimer)
            test.dut.at1.open()
            ret = test.dut.at1.wait_for(".*SYSSTART.*")
            if not ret:
                test.expect(test.dut.at1.send_and_verify("AT^SQPORT?", ".*OK.*"))
                test.log.info(" URC SYSSTART not found over USB")
            else:
                test.log.info(" URC SYSSTART found over USB")
        else:
            test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=wforsysstarttimer))
        pass

    def setup(test):
        test.pin1_value = test.dut.sim.pin1

        #        test.dut.dstl_restart()
        #        test.sleep(5)
        test.dut.dstl_detect()
        if test.dut.project.upper() == 'SERVAL':
            test.wforsysstarttimer = 10

        if test.dut.project.upper() == 'BOBCAT':
            test.wforsysstarttimer = 60

        # enable URCs on MCT to see which serial lines are changing
        test.dut.devboard.send_and_verify('mc:URC=SER')
        test.dut.devboard.send_and_verify('mc:URC=PWRIND')

        pass

    def run(test):
        test.log.step("\n\t\t  0. check and deregister from network ")
        test.dut.at1.send_and_verify("AT+CPIN?", ".*\+CPIN: .*OK.*")

        resp = test.dut.at1.last_response
        if 'READY' in resp:
            test.dut.at1.send_and_verify('AT+CLCK="SC",2', ".*+CLCK: .*OK.*")
            resp = test.dut.at1.last_response
            if '+CLCK: 0' in resp:
                test.dut.at1.send_and_verify('AT+CLCK="SC",1,"{}"'.format(test.pin1_value), "^.*OK.*$")
            # perform deregistering (restart needs too much time)
            test.dut.at1.send_and_verify('AT+CFUN=0', '.*OK.*AIRPLANE MODE.*')
            test.sleep(1)
            test.dut.at1.send_and_verify('AT+CFUN=1', '.*OK.*SYSSTART.*')
            test.expect(test.dut.at1.send_and_verify_retry("AT+CPIN?", expect="OK", retry=15,
                                            retry_expect="(SIM not inserted|SIM busy)", timeout=5,
                                            wait_after_send=0, sleep=0.3))

        test.log.step("\n\t\t  1. test: check command without PIN ")
        test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*FAST.*"))
        test.dut.at1.send('AT^SMSO')
        test.time1 = time.perf_counter()
        test.close_port_if_usb()
        test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=12))
        ret = test.check_timing("1. SMSO normal without PIN", 9)

        test.dut.dstl_turn_on_igt_via_dev_board()
        test.wait_for_sysstart_or_delay(test.wforsysstarttimer)
        """
        if "usb" in test.dut.at1.name:
            time.sleep(12)
            test.expect(test.dut.at1.send_and_verify("AT^SQPORT?", ".*OK.*"))
        else:
            test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=test.wforsysstarttimer))
        """

        test.dut.at1.send('AT^SMSO="fast"')
        test.time1 = time.perf_counter()
        test.close_port_if_usb()
        test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
        ret = test.check_timing("1. SMSO=FAST without PIN", 1)

        test.dut.dstl_turn_on_igt_via_dev_board()
        test.wait_for_sysstart_or_delay(test.wforsysstarttimer)
        """
        if "usb" in test.dut.at1.name:
            time.sleep(12)
            test.expect(test.dut.at1.send_and_verify("AT^SQPORT?", ".*OK.*"))
        else:
            test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=test.wforsysstarttimer))
        """

        test.log.step("\n\t\t  2. test: check command with PIN ")
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*FAST.*"))

        test.dut.at1.send('AT^SMSO')
        test.time1 = time.perf_counter()
        test.close_port_if_usb()
        test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=9))
        ret = test.check_timing("2. SMSO normal with PIN", maxduration=9)

        test.dut.dstl_turn_on_igt_via_dev_board()
        test.wait_for_sysstart_or_delay(test.wforsysstarttimer)
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)

        test.dut.at1.send('AT^SMSO="fast"')
        test.time1 = time.perf_counter()
        test.close_port_if_usb()
        test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
        ret = test.check_timing("2. SMSO FAST with PIN", maxduration=1)

        test.dut.dstl_turn_on_igt_via_dev_board()
        test.wait_for_sysstart_or_delay(test.wforsysstarttimer)

        test.log.step("\n\t\t  3. test: check at command with invalid paramter ")
        test.expect(test.dut.at1.send_and_verify("AT^smso=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^smso="fst"', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^smso="ftst"', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^smso=fso', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^smso=fastshutdown', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^smso=', ".*ERROR.*"))

        test.log.step("\n\t\t  4. check fast shutdown by GPIO4 ")
        # ATTENTION: default value of GPIO-output is low, so it is active right then!
        # 1st we set the GPIO port to out, then we do the test
        # McTv4 shows problems with the default setting of this pin
        test.dut.devboard.send('mc:gpiocfg=3,outp')
        test.sleep(0.3)
        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(0.3)
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(test.wforsysstarttimer)
        test.dut.at1.send('ATi')
        test.dut.devboard.send_and_verify('mc:pwrind?')

        # now we can go on with GPIO test:
        test.dut.devboard.send('mc:gpio3=0')
        test.time1 = time.perf_counter()
        test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
        ret = test.check_timing("4. GPIO-Shutdown without PIN", maxduration=1)

        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=test.wforsysstarttimer))
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)

        test.dut.devboard.send('mc:gpio3=0')
        test.time1 = time.perf_counter()
        test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
        ret = test.check_timing("4. GPIO-Shutdown without PIN", maxduration=1)

        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(1)
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=test.wforsysstarttimer))
        pass

    def cleanup(test):
        # set MCT back to default settings
        test.dut.devboard.send('mc:gpiocfg=3,inp')
        test.dut.devboard.send('mc:time=OFF')
        pass


if __name__ == "__main__":
    unicorn.main()
