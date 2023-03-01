# responsible: hongwei.yin@thalesgroup.com
# location: Dalian


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
import time
import random

shutdown_times = []
sysstart_times = []
sysstart_extra_times = []
at_times = []
simready_times = []
duration_time = 24 * 60 * 60
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
            test.log.info(f"This is {i} loop in while.")
            if i % 250 == 0:
                test.log.info(f'shutdown_times in loop {i}: ' + " ".join(map(str, shutdown_times)))
                test.log.info(f'sysstart_times in loop {i}: ' + " ".join(map(str, sysstart_times)))
                test.log.info(f'at_times in loop {i}: ' + " ".join(map(str, at_times)))
                test.log.info(f'simready_times in loop {i}: ' + " ".join(map(str, simready_times)))
            i = i + 1
            test.sleep(5)
            timeout = random.randint(1, 30)
            test.log.info("timeout is: " + str(timeout))
            loop_time = time.time()
            if not run_atc_1(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_2(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_3(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_4(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_5(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_6(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_7(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_8(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_9(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_10(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_11(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_12(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_13(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_14(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_15(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_16(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_17(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_18(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_19(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_20(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_21(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_22(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_23(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_24(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_25(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_26(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_27(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_28(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_29(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_30(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_31(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_32(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_33(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_34(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_35(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_36(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_37(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_38(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_39(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_40(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_41(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_42(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_43(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_44(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_45(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_46(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_47(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_48(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_49(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_50(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_51(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_52(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_53(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_54(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_55(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue
            if not run_atc_56(test, force_fsd_flow=time.time() - loop_time > timeout):
                continue

        test.log.info('shutdown_times: ' + " ".join(map(str, shutdown_times)))
        test.log.info('sysstart_times: ' + " ".join(map(str, sysstart_times)))
        test.log.info('at_times: ' + " ".join(map(str, at_times)))
        test.log.info('simready_times: ' + " ".join(map(str, simready_times)))
        test.log.info('sysstart_extra_times: ' + " ".join(map(str, sysstart_extra_times)))

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


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
    if every_sysstart_time >= 14:
        sysstart_extra_times.append(every_sysstart_time)
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


def step_with_fsd_handle(max_retry, step_if_fsd):
    def wrapper(func):
        def retry(test, force_fsd_flow, *args, **kw):
            if force_fsd_flow:
                step_if_fsd(test)
            else:
                i = 0
                while i < max_retry:
                    test.log.info(f'Execute step: {func.__name__}, the {i + 1} time')
                    result = func(test, force_fsd_flow, *args, **kw)
                    if result:
                        return True
                    else:
                        i += 1
                        test.sleep(2)
                step_if_fsd(test)
            return False

        return retry

    return wrapper


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_1(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_2(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_3(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_4(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_5(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SNFOTA=url,"http://182.92.198.110:8081/diff.usf"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_6(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SNFOTA?',
                                                    expect='^SNFOTA: "url","http://182.92.198.110:8081/diff.usf"'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_7(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('at^snfota="urc","1"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_8(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SNFOTA?', expect='^SNFOTA: "urc","1"'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_9(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('at^snfota="conid","1"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_10(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SNFOTA?', expect='^SNFOTA: "conid","1"'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_11(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify(
        'at^snfota="crc","c97f1ec44e2ba0a6ac75f84a59d6ba72a89ddfd4e768b66ed3f90160ed11d044"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_12(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SNFOTA?',
                                                    expect='^SNFOTA: "crc","c97f1ec44e2ba0a6ac75f84a59d6ba72a89ddfd4e768b66ed3f90160ed11d044"'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_13(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_14(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_15(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_16(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_17(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_18(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_19(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_20(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_21(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC","gpio"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_22(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC","std"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_23(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_24(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","asc0"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_25(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_26(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","0"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_27(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","1"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_28(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_29(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT&C')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_30(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at&v', expect='&C: 0'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_31(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT&S')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_32(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at&v', expect='&S: 0'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_33(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT&C2')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_34(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at&v', expect='&C: 2'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_35(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT&S1')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_36(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at&v', expect='&S: 1'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_37(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT&C1')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_38(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at&v', expect='&C: 1'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_39(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","+CMT"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_40(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","RING"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_41(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","all"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_42(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","1"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_43(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","0"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_44(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SAIC=1,1,1,3,0,0,1,0,0')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_45(test, force_fsd_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at^saic?', expect='^SAIC: 1,1,1,3,0,0,1,0,0'))


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_46(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","60"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_47(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","3"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_48(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR","1"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_49(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR","10"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_50(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT","1"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_51(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT","6000"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_52(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/TLS/Version","MIN","MAX"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_53(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","off"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_54(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","on"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_55(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","disabled"')


@step_with_fsd_handle(max_retry=1, step_if_fsd=eval('fsd_and_checktime'))
def run_atc_56(test, force_fsd_flow=False):
    return test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"')


if "__main__" == __name__:
    unicorn.main()
