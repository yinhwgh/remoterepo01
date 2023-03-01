# responsible: dan.liu@thalesgroup.com
# location: Dalian
# TC0010524.001


import unicorn

from core.basetest import BaseTest
from core.simdata import SimData
from dstl.auxiliary import init
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.call import setup_voice_call


class dtmftonescommands(BaseTest):

    def setup(test):

        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()

    def run(test):
        test.log.info("1. Set all current parameters to manufacturer defaults")
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))


        test.log.info('2.Check all the possibilities for command AT+VTD,valid and invalid')
        test.expect(test.dut.at1.send_and_verify('at+vtd=?', "+VTD: (1-255)", wait_for='OK'))
        i = 1
        loop_time_duration = 256
        dtmf_char = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "*", "#"]

        while i < loop_time_duration:
            test.expect(test.dut.at1.send_and_verify('AT+VTD={}'.format(i), '.*OK.*'))
            i += 1
        else:
            test.expect(test.dut.at1.send_and_verify('AT+VTD=0', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('AT+VTD=-1', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('AT+VTD=256', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('AT+VTD=0.2', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('AT+VTD=a', '.*ERROR.*'))


        test.log.info('3. Establish a voice call')
        test.expect(test.dut.at1.send_and_verify('AT+VTD=1', '.*OK.*'))
        call_result = test.expect(test.dut.dstl_voice_call_by_number(test.r1,test.r1.sim.nat_voice_nr))

        if call_result:
            test.sleep(5)
            test.log.info('4. Check all the possibilities for command AT+VTS: valid and invalid')
            test.log.info('4.1 Check all the vaild parameter for command at+vts')
            test.expect(test.dut.at1.send_and_verify('at+vts=?', "+VTS: (0-9,#,*,A-D),(1-255)",wait_for='OK'))
            for c in dtmf_char:
                test.expect(test.dut.at1.send_and_verify(f'at+vts="{c}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+vts="0",1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+vts="1",20', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+vts="*",255', '.*OK.*',timeout=30))

            test.log.info('4.2 Check invalid parameter for command at+vts')
            test.expect(test.dut.at1.send_and_verify('at+vts=0', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('at+vts="E",1', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('at+vts="5",256', '.*ERROR.*'))
            test.log.info('5.Release  the voice call')
            test.expect(test.dut.dstl_release_call())
        else:
            test.log.error('Set up call fail')
            test.expect(False)

    def cleanup(test):
        test.log.info("6. Set all current parameters to manufacturer defaults")
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))


    def transfer_bin_to_hex(test,num):

        if num == 10:
            return 'A'
        elif num == 11:
            return 'B'
        elif num == 12:
            return 'C'
        elif num == 13:
            return 'D'
        elif num == 14:
            return '*'
        else:
            return '#'

if __name__=='__main__':
    unicorn.main()



