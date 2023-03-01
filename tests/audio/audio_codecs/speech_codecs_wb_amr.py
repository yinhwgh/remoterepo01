# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0093927.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_release_call


class Test(BaseTest):
    '''
    TC0093927.001 - TpSpeechCodecsWbAmr
    Intention:
        Check AT^SCFG="Call/Speech/Codec" & AT^SCFG="Call/VoLTE/Codec"Parameter is global for all interfaces, non-volatile and will not be reset byÂ AT&F

    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.sleep(10)

    def run(test):

        test.log.info('1. check parameter set')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=?', '.*\^SCFG: "Call/Speech/Codec",\("0","2"\).*\^SCFG: "Call/VoLTE/Codec",\("0","2"\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', '.*\^SCFG: "Call/Speech/Codec","[0|2]".*\^SCFG: "Call/VoLTE/Codec","[0|2]".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec",5','ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec",1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec",0','OK'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec",a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec",1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec",0', 'OK'))

        test.log.info('2. check value whether change after at&f')
        test.expect(test.dut.at1.send_and_verify('at&f', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec"', '.*\^SCFG: "Call/Speech/Codec","0".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec"', '.*\^SCFG: "Call/VoLTE/Codec","0".*OK.*'))
        test.expect(
            test.dut.at2.send_and_verify('at^SCFG="Call/Speech/Codec"', '.*\^SCFG: "Call/Speech/Codec","0".*OK.*'))
        test.expect(
            test.dut.at2.send_and_verify('at^SCFG="Call/VoLTE/Codec"', '.*\^SCFG: "Call/VoLTE/Codec","0".*OK.*'))

        test.log.info('3. check value whether change after restart')
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec",2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec",2', 'OK'))
        test.dut.dstl_restart()
        test.expect(
            test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec"', '.*\^SCFG: "Call/Speech/Codec","2".*OK.*'))
        test.expect(
            test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec"', '.*\^SCFG: "Call/VoLTE/Codec","2".*OK.*'))
        test.expect(
            test.dut.at2.send_and_verify('at^SCFG="Call/Speech/Codec"', '.*\^SCFG: "Call/Speech/Codec","2".*OK.*'))
        test.expect(
            test.dut.at2.send_and_verify('at^SCFG="Call/VoLTE/Codec"', '.*\^SCFG: "Call/VoLTE/Codec","2".*OK.*'))

        test.log.info('4. restore default setting')
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/Speech/Codec",0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^SCFG="Call/VoLTE/Codec",0', 'OK'))


    def cleanup(test):
        test.log.info('***Test End, clean up***')



if "__main__" == __name__:
    unicorn.main()
