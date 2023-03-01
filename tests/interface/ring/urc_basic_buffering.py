#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095663.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary import init
import re

class Test(BaseTest):
    '''
    TC0095663.001 - UrcBasicBuffering
    Intention:
    Check functionality of URC buffer of busy communication interface.
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step('1.Set AT^SCFG="GPIO/mode/RING0","std"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","std"', '.*OK.*'))
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_enter_pin()
        test.log.step('2.Set AT^SCFG="URC/Ringline","off"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"', '.*OK.*'))

        test.log.step('3.Set AT^SCFG="URC/Ringline/ActiveTime", "0" or "1" or "2"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","0"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime"', '\^SCFG: "URC/Ringline/ActiveTime","0".*OK.*'))

        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","1"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime"',
                                                 '\^SCFG: "URC/Ringline/ActiveTime","1".*OK.*'))

        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime"',
                                                 '\^SCFG: "URC/Ringline/ActiveTime","2".*OK.*'))
        test.log.step('4.Check configuration AT^SCFG?')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', '\^SCFG: "URC/Ringline/ActiveTime","2".*OK.*'))

        test.log.step('5.Run command to generate regular URC')
        if test.dut.project == 'VIPER':
            test.expect(test.dut.at1.send_and_verify('at^sind=simtray,1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at^sind=simstatus,1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SCKS=1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CMGW=\"12345678901\"', '>', wait_for='>'))
            for i in range(1, 30):
                test.dut.devboard.send_and_verify('mc:ccin=1','OK')
                test.sleep(2)
                test.dut.devboard.send_and_verify('mc:ccin=0','OK')
                test.sleep(2)
            test.dut.at1.send('\x1A')
            test.sleep(5)
            buffer = test.dut.at1.read()
            result = re.findall('\+CIEV: .*|\^SCKS:', buffer)
            count = len(result)

        else:
            test.expect(test.dut.at1.send_and_verify('AT^SRADC=1,1,1000', '.*OK.*'))
            test.log.step('6.Use AT+CMGS=(number) to enter SMS write mode.')
            test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CMGW=\"12345678901\"', '>', wait_for='>'))

            test.log.step('7.Use Ctrl+Z to quit SMS write mode.')
            test.sleep(150)
            test.dut.at1.send_and_verify('\x1A', '')
            test.expect(test.dut.at1.send_and_verify('AT^SRADC=1,0', '.*OK.*'))
            test.sleep(60)
            buffer = test.dut.at1.read()
            result = re.findall("\\^SRADC: \\d.*", buffer)
            count = len(result)

        test.log.info('****URC COUNT IS {}****'.format(count))
        if count == 100:
            test.log.info('Expect 100 URCs received, test pass.')
            test.expect(True)
        else:
            test.log.info(f'Received {count} URCs , but expect 100 URCs, test fail.')
            test.expect(False)


    def cleanup(test):
        test.log.info('***Test End, clean up***')
        test.dut.at1.send_and_verify('AT', '.*OK.*')
        test.dut.at1.send_and_verify('AT^SRADC=0,0', 'OK')
        test.dut.at1.send_and_verify('at^sind=simtray,0', '.*OK.*')
        test.dut.at1.send_and_verify('at^sind=simstatus,0', '.*OK.*')
        test.dut.at1.send_and_verify('AT^SCKS=0', '.*OK.*')


if "__main__" == __name__:
    unicorn.main()
