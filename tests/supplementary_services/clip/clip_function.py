#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0084779.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0084779.001 - TpCclipFunc
    Intention: This is a functional test for the clip command.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

    def run(test):
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 0,[0|1|2]\s+OK"))

        test.log.step('1.Test clip=1')
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1", "OK"))
        test.expect(test.r1.at1.send_and_verify("AT+CLIP=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 1,1\s+OK"))
        test.r1.at1.send_and_verify(f"ATD{test.dut.sim.nat_voice_nr};")
        test.expect(test.dut.at1.wait_for('RING'))
        test.expect(test.dut.at1.wait_for(f'\+CLIP: "{test.r1.sim.nat_voice_nr}",129.*'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()

        test.log.step('2.Test clip=0')
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 0,1\s+OK"))
        test.r1.at1.send_and_verify(f"ATD{test.dut.sim.nat_voice_nr};")
        test.expect(test.dut.at1.wait_for('RING'))
        test.expect(test.dut.at1.wait_for('CLIP', timeout= 15) == False)
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()




    def cleanup(test):
        pass



if "__main__" == __name__:
    unicorn.main()

