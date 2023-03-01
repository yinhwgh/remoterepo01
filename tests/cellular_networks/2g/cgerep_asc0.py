# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0011760.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.devboard.devboard import *


class Test(BaseTest):
    """
    TC0011760.001 - CgerepAsc0.inc
    Intention: The aim of this test is to check the right unsolicited result codes show the ME/ NW gprs state-changes.
    Subscriber: 1
    """
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_restart()
        pass

    def run(test):
        # select a CID which is free. In normal case CID 8 is free and can be used
        n = 8
        test.log.step('1. Define additional PDP context via AT+CGDCONT command')
        test.expect(test.dut.at1.send_and_verify(f'at+cgdcont={n},"IP","{test.dut.sim.apn_v4}"', 'OK'))

        test.log.step('2. Check if module is attach to PS – if not: attach module to PS via AT+CGATT=1')
        test.dut.dstl_register_to_network()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CGATT=1', 'OK', timeout=120))
        if test.dut.project is 'VIPER':
            test.log.error("OPEN ISSUE VPR02-976: attaching while already attached will take 6 min., so we abort it:")
            test.dut.at1.send_and_verify('AT', '.*O.*')

        test.log.step('3. Set AT+CGEREP=2,0')
        test.expect(test.dut.at1.send_and_verify('AT+CGEREP=2,0', 'OK'))
        test.step4to20(n)

        test.log.step('21. Set AT+CGEREP=1,1')
        test.expect(test.dut.at1.send_and_verify('AT+CGEREP=1,1', 'OK'))
        test.log.step('22. Repeat steps 4-20')
        test.step4to20(n)

        test.step23to27(n)

        test.log.step('28. Repeat steps 23-27 three times')
        for i in range(1, 4):
            test.log.info('Repeat 23-27 3 times: {} ')
            test.step23to27(n)

        test.log.step('29. Set CGEREP=2,1(Flush buffer)')
        test.expect(test.dut.at1.send_and_verify('AT+CGEREP=2,1', 'OK'))
        test.log.step('30. Verify CGEV URC, URC CGEV for steps 23-27 should be displayed')
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN ACT {i}'))  # VPR02-978: |\+CGEV: PDN ACT {i}'))
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN DEACT {i}'))  # VPR02-978: |\+CGEV: PDN DEACT {i}'))
        pass

    def cleanup(test):
        pass

    def step4to20(test, i):
        sleeptime=30
        test.log.step('4. Activate the next PDP context via AT+CGACT and check')
        test.expect(test.dut.at1.send_and_verify(f'AT+CGACT=1,{i}', 'OK',timeout=120))
        # test.expect(test.dut.at1.send_and_verify('AT+CGACT?', f'CGACT: {i},1'))

        test.log.step('5. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN ACT {i}|\+CGEV: PDN ACT {i}'))

        test.sleep(sleeptime)
        test.log.step('6. Deactivate the next PDP context via AT+CGACT and check')
        test.expect(test.dut.at1.send_and_verify(f'AT+CGACT=0,{i}', 'OK'))
        # test.expect(test.dut.at1.send_and_verify('AT+CGACT?', f'CGACT: {i},0'))

        test.log.step('7. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN DEACT {i}|\+CGEV: PDN DEACT {i}'))

        test.sleep(sleeptime)
        test.log.step('8. Detached module from PS via AT+CGATT=0')
        test.expect(test.dut.at1.send_and_verify('AT+CGATT=0', 'OK'))

        test.log.step('9. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc('\+CGEV: ME DETACH'))

        test.sleep(sleeptime)
        test.log.step('10. Attach module to PS via AT+CGATT=1')
        test.expect(test.dut.at1.send_and_verify('AT+CGATT=1', 'OK'))

        test.log.step('11. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc('\+CGEV: ME PDN ACT \d|\+CGEV: PDN ACT \d'))

        test.sleep(sleeptime)
        test.log.step('12. Activate the next PDP context via AT+CGACT and check')
        test.expect(test.dut.at1.send_and_verify(f'AT+CGACT=1,{i}', 'OK'))
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN ACT {i}|\+CGEV: PDN ACT {i}'))

        test.sleep(sleeptime)
        test.log.step('13. Detached module from PS via AT+CGATT=0')
        test.expect(test.dut.at1.send_and_verify('AT+CGATT=0', 'OK'))

        test.log.step('14. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc('\+CGEV: ME DETACH'))
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: PDN DEACT {i}|\+CGEV: PDN DEACT {i}'))

        test.sleep(sleeptime)
        test.log.step('15. Attach module to PS via AT+CGATT=1')
        test.expect(test.dut.at1.send_and_verify('AT+CGATT=1', 'OK'))

        test.log.step('16. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN ACT {i}|\+CGEV: PDN ACT {i}', timeout=12))

        test.sleep(sleeptime)
        test.log.step('17. Manually deregister from network via AT+COPS=2')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))

        test.log.step('18. Verify CGEV URC')
        test.expect(test.dut.at1.verify_or_wait_for('\+CGEV: NW DETACH'))
        test.expect(test.dut.at1.verify_or_wait_for(f'\+CGEV: ME PDN DEACT {i}|\+CGEV: PDN DEACT {i}'))

        test.sleep(sleeptime)
        test.log.step('19. Manually register to network via AT+COPS=0')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK'))

        test.log.step('20. Verify CGEV URC')
        test.expect(test.dut.dstl_check_urc(f'\+CGEV: ME PDN ACT {i}|\+CGEV: PDN ACT {i}', timeout=120))
        pass

    def step23to27(test, i):
        test.log.step('23. Set CGEREP=0,0')
        test.expect(test.dut.at1.send_and_verify('AT+CGEREP=0,0', 'OK'))

        test.log.step('24. Activate the next PDP context via AT+CGACT and check')
        test.expect(test.dut.at1.send_and_verify(f'AT+CGACT=1,{i}', 'OK'))
        # test.expect(test.dut.at1.send_and_verify('AT+CGACT?', f'CGACT: {i},1'))

        test.log.step('25. Verify CGEV URC, should be NO URC CGEV')
        test.expect(test.dut.dstl_check_urc('\+CGEV:.*', timeout=10)==False)

        test.log.step('26. Detached module from PS via AT+CGACT and check')
        test.expect(test.dut.at1.send_and_verify(f'AT+CGACT=0,{i}', 'OK'))
        # test.expect(test.dut.at1.send_and_verify('AT+CGACT?', f'CGACT: {i},0'))

        test.log.step('27. Verify CGEV URC, should be NO URC CGEV')
        test.expect(test.dut.dstl_check_urc('\+CGEV:.*', timeout=10)==False)
        pass


if "__main__" == __name__:
    unicorn.main()
