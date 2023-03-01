# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0088242.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode



class TpAudioLoop(BaseTest):
    """
    To test audio loop function
    1.Check SCFG for Audio/Loop
    2.Check value range of parameters
    3.Check influence to other audio settings: AT^SNFS>1, SNFO, SNFTTY, SRTC, SAIC, SNFI
    4.Check Audio/Loop within calls
    """
    def setup(test):

        dstl_detect(test.dut)
        test.log.info('Reset to default value')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def run(test):
        test.log.info('Set supported audio modes via AT^SNFS')
        # check AT^SNFS default value
        test.expect((test.dut.at1.send_and_verify("AT^SNFS?", ".(0).*OK.*")))

        # Set AT^SNFA value
        test.expect(test.dut.at1.send_and_verify("AT^SNFS="))

        test.log.info('Connect WBCA by both microphone and speaker')
        tkinter.messagebox.showwarning('Please connect the microphone and speaker to WBCA')
        test.log.info('Set WBCA to PCM')

        # check AT^SAIC default value and set the proper value for PCM
        test.expect(test.dut.at1.send_and_verify("AT^SAIC?", "4,1,1,1,0,1,1,0.*OK.*"))

        tkinter.messagebox.showerror('Please set the PCM mode in WBCA board', 'Continue?')

        # switch on audio loop and generate some audio
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Audio/Loop\",\"1\"", ".*OK.*"))

        # check whether there is some voice in headphone
        audio_loop_on = tkinter.messagebox.askquestion('Please check whether there is voice', 'Continue?')
        if audio_loop_on is False:
            test.log.info('Test failed')

        # switch off audio loop and generate some audio
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Audio/Loop\",\"0\"", ".*OK.*"))
        # check whether there is some voice in headphone
        audio_loop_off = tkinter.messagebox.askquestion('Please check whether there is voice', 'Continue?')
        if audio_loop_off is True:
            test.log.info('Test failed')

        # swich on audio loop and reset module

        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Audio/Loop\",\"1\"", ".*OK.*"))
        test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Audio/Loop\",\"?\"", "0.*OK.*"))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()







