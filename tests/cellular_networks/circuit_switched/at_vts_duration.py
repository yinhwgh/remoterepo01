#author: haofeng.ding@thalesgroup.com
#location: Dalian
#TC0093112.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported

class Test(BaseTest):
    '''
     TC0093112.001 - DtmfSequenceGapsAndTonesDurations
     Intention: To check if the duration of gaps between DTMF tones generate in sequence are no longer than
300 ms.
     Subscriber: 2
     '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()
        test.dut.dstl_register_to_network()
        test.log.info('Enable error reporting')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        r1_phone_num = test.r1.sim.int_voice_nr
        test.log.info('Test of the command: DTMF and tone generation (VTS)')
        test.expect(test.dut.at1.send_and_verify('at+vts=?', expect='.*+VTS: (0-9,#,*,A-D),(1-255)  OK.*'))
        test.log.info('Reset ME and start with full functionality')
        test.log.info('Establish call between DUT and 2nd subscriber')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        test.log.info('Enable error result code and use verbose values Get developer information Check the available commands Test, Write (for VTS)')
        dtmf_list = ['"0"', '"1"', '"2"', '"3"', '"4"', '"5"', '"6"', '"7"', '"8"', '"9"','"A"','"B"','"C"','"D"','"*"','"#"']
        for dtmf in dtmf_list:
            test.expect(test.dut.at1.send_and_verify('at+vts='+dtmf, expect='OK'))
        test.log.info('Test the limits of the parameter values for commands Test, Write (for VTS)')
        dtmf_error_list=['" "', '"!"', '"$"', '"%"', '"&"', '"\'"', '"("', '")"', '"+"', '","', '"-"', '"."', '"/"', '":"', '";"', '"<"', '"="', '">"', '"@"', '"E"', '"F"', '"G"', '"H"', '"I"', '"J"', '"K"', '"L"', '"M"', '"N"', '"O"', '"P"', '"Q"', '"R"', '"S"', '"T"', '"U"', '"V"', '"W"', '"X"', '"Y"', '"Z"', '"["', '"]"', '"^"', '"_"', '"`"', '"e"', '"f"', '"g"', '"h"', '"i"', '"j"', '"k"', '"l"', '"m"', '"n"', '"o"', '"p"', '"q"', '"r"', '"s"', '"t"', '"u"', '"v"', '"w"', '"x"', '"y"', '"z"', '"{"', '"|"', '"}"', '"~"', '"a"','"b"','"c"','"d"','"01"']
        for dtmf in dtmf_error_list:
            test.expect(test.dut.at1.send_and_verify('at+vts='+dtmf, expect='+CME ERROR: invalid characters in text string'))
        test.log.info('Test the limits of the parameter values for commands Test, Write (for VTS){"0123456789#*ABCD0123456789#*ABCD"}')
        test.expect(test.dut.at1.send_and_verify('at+vts="0123456789#*ABCD0123456789#*ABCD"', expect='+CME ERROR: invalid characters in text string'))
        test.log.info('Terminate the call')
        test.expect(test.dut.at1.send_and_verify('ath', expect='OK'))

    def cleanup(test):
        test.log.info('***Test End***')


if '__main__' == __name__:
    unicorn.main()
