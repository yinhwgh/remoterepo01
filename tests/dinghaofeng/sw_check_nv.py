# responsible: hongwei.yin@thalesgroup.com
# location: Dalian


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
import time

shutdown_times = []
sysstart_times = []
at_times = []
simready_times = []
duration_time = 15 * 60 * 60
fsd_times = 0


class Test(BaseTest):
    """
       check sysstart time if become longer after reboot many times.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.devboard.send_and_verify("mc:urc=off", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.dut.at1.send_and_verify('AT+CMEE=2')
        test.dut.at1.send_and_verify('AT^SSET=1')
        test.dut.at1.send_and_verify('AT&W')
        test.dut.at1.send_and_verify('AT+CPIN=1234')
        test.dut.at1.send_and_verify('AT+CLCK="SC",0,1234')
        test.sleep(2)

    def run(test):
        i = 1
        start_time = time.time()
        while time.time() - start_time < duration_time:
            test.log.info(f"This is {i} loop.")
            i = i + 1
            change_nv(test)
            # test.dut.at1.send_and_verify('AT+CFUN=1,1')
            # test.dut.at1.wait_for('.*SYSSTART.*')
            fsd_and_checktime(test)
            check_nv(test)
            reset_nv(test)

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


def change_nv(test):
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","asc0"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","0"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","1"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","+CMT"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","RING"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","60"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","off"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","disabled"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"')


def reset_nv(test):
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC","std"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","all"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","0"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","3"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR","10"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT","6000"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","on"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"')


def check_nv(test):
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach"', expect='disabled'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS"', expect='0'))


def fsd_and_checktime(test):
    global fsd_times
    fsd_times = fsd_times + 1
    test.log.info(f"This is {fsd_times} loop in fsd.")
    test.log.step("1. Send AT^SMSO command and check shutdown urc")
    test.expect(test.dut.dstl_shutdown_smso(), critical=True)
    urc_shutdown = time.time()

    test.log.step("2. Using McTest check if module is Off(MC:PWRIND) with in 1s after URC pop out")
    test.expect(test.dut.devboard.wait_for('.*PWRIND: 1.*', timeout=3))
    # test.expect(test.dut.devboard.send_and_verify('MC:PWRIND', '.*PWRIND: 1.*', wait_for='.*PWRIND: 1.*', timeout=1), critical=True)
    urc_pwrind = time.time()

    test.log.step("3. Using McTest measurement module shutdown time")
    every_shutdown_time = urc_pwrind - urc_shutdown
    test.log.info('every_shutdown_time: ' + str(every_shutdown_time))
    shutdown_times.append(every_shutdown_time)
    test.expect(
        test.dut.devboard.send_and_verify('mc:vbatt=off', 'OK'))
    test.expect(
        test.dut.devboard.send_and_verify('mc:vbatt=on', 'OK'))
    test.sleep(2)

    test.log.step("4. Turn On module (MC:IGT=1000) and wait for ^SYSSTART")
    urc_igt = time.time()
    test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
    test.expect(test.dut.at1.wait_for('.*SYSSTART.*'), critical=True)
    urc_sysstart = time.time()
    every_sysstart_time = urc_sysstart - urc_igt
    test.log.info('every_sysstart_time: ' + str(every_sysstart_time))
    sysstart_times.append(every_sysstart_time)
    if 'SSIM READY' in test.dut.at1.last_response:
        test.log.info('every_simready_time: ' + str(every_sysstart_time))
        simready_times.append(every_sysstart_time)

        test.log.step("5. Send AT command to check if communication with module is possible")
        # test.expect(test.dut.at1.send_and_verify("AT", ".*OK", append=True))
        print('last_response: ', test.dut.at1.last_response)
        result = False
        while not result:
            test.dut.at1.send("AT")
            result = test.dut.at1.wait_for("OK", timeout=0.5, append=True)
        urc_at = time.time()
        every_at_time = urc_at - urc_igt
        test.log.info('every_at_time: ' + str(every_at_time))
        at_times.append(every_at_time)

    else:
        test.log.step("5. Send AT command to check if communication with module is possible")
        # test.expect(test.dut.at1.send_and_verify("AT", ".*OK", append=True))
        print('last_response: ', test.dut.at1.last_response)
        result = False
        while not result:
            test.dut.at1.send("AT")
            result = test.dut.at1.wait_for("OK", timeout=0.5, append=True)
        urc_at = time.time()
        every_at_time = urc_at - urc_igt
        test.log.info('every_at_time: ' + str(every_at_time))
        at_times.append(every_at_time)

        test.log.step("6. wait for the presentation of sim urc")
        test.expect(test.dut.at1.wait_for('SSIM READY', append=True), critical=True)
        urc_simready = time.time()
        every_simready_time = urc_simready - urc_igt
        test.log.info('every_simready_time: ' + str(every_simready_time))
        simready_times.append(every_simready_time)

        print('last_response: ', test.dut.at1.last_response)


if "__main__" == __name__:
    unicorn.main()