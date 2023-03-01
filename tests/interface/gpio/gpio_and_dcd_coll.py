#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088191.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import switch_to_command_mode


class Test(BaseTest):
    '''
    TC0088191.001 - GPIOandDCDcoll
    Intention: Testing alternative functionality of GPIO2/DCD line
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()


    def run(test):

        test.log.info('***Test Start***')
        test.log.info('1.Set DCD line by at^scfg as "GPIO"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","GPIO"', 'OK'))

        test.log.info('2.Restart module')
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_register_to_network()

        test.log.info('3.Set GPIO2 by at^scpin as output')
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=1', 'O'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,1', 'OK'))

        test.log.info('4.Set GPIO2 by at^scpin as input')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,1', 'OK'))

        test.log.info('5.Try to set at&c0')
        test.expect(test.dut.at1.send_and_verify('at&c0', 'ERROR'))

        test.log.info('6.Try set at&c2')
        test.expect(test.dut.at1.send_and_verify('at&c2', 'ERROR'))

        test.log.info('7.Try set at&c1')
        test.expect(test.dut.at1.send_and_verify('at&c1', 'ERROR'))

        test.log.info('8.*Establish data connection (PPP) connection and check state of DCD line')
        test.expect(test.dut.at1.send_and_verify('atd*99#', 'CONNECT',wait_for='CONNECT'))
        test.sleep(1)
        test.expect(test.check_dcd_line(True))

        test.log.info('9.*Release data connection (PPP) connection and check state of DCD line')
        test.dut.at1.send_and_verify(b'+++',end='',wait_for ='OK')
        test.expect(test.check_dcd_line(True))

        test.log.info('10.*Return to data mode and abort connection.')
        test.expect(test.dut.at1.send_and_verify('ato', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)
        test.dut.at1.send_and_verify(b'+++',end='',wait_for ='OK')
        test.dut.dstl_switch_to_command_mode_by_dtr()
        test.sleep(5)
        test.log.info('11.*Check state of DCD line')
        test.expect(test.check_dcd_line(True))

        test.log.info('12.Configure GPIO2 by at^scpin as output to LOW state')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,1,1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,1', 'OK'))

        test.log.info('13.Set DCD line by at^scfg as "STD"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","std"', 'OK'))

        test.log.info('14.Restart Module')
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_register_to_network()

        test.log.info('15.Try to configure GPIO2 by at^scpin as output')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,1,1', 'ERROR'))

        test.log.info('16.Try to configure GPIO2 by at^scpin as input')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,1,0', 'ERROR'))

        test.log.info('17.Set at&c0')
        test.expect(test.dut.at1.send_and_verify('at&c0', 'OK'))

        test.log.info('18.Set at&c2')
        test.expect(test.dut.at1.send_and_verify('at&c2', 'OK'))

        test.log.info('19.Set at&c1')
        test.expect(test.dut.at1.send_and_verify('at&c1', 'OK'))

        test.log.info('20.*Establish data connection (PPP) connection and check state of DCD line')
        test.expect(test.dut.at1.send_and_verify('atd*99#', 'CONNECT',wait_for='CONNECT'))
        test.sleep(1)
        test.expect(test.check_dcd_line(True))

        test.log.info('21.*Release data connection (PPP) connection and check state of DCD line')
        test.dut.at1.send_and_verify(b'+++',end='',wait_for ='OK')
        test.expect(test.check_dcd_line(True))

        test.log.info('22.*Return to data mode and abort connection.')
        test.expect(test.dut.at1.send_and_verify('ato', 'CONNECT', wait_for='CONNECT'))
        test.dut.dstl_switch_to_command_mode_by_dtr()
        test.sleep(5)
        test.log.info('23.*Check state of DCD line')
        test.expect(test.check_dcd_line(False))



    def cleanup(test):
       test.log.info('***Test End***')

    def check_dcd_line(test,expect):
        if expect == True:
            test.log.info('Expect DCD line active')
            return test.dut.at1.connection.getCD() == True
        else:
            test.log.info('Expect DCD line inactive')
            return test.dut.at1.connection.getCD() == False



if "__main__" == __name__:
    unicorn.main()

