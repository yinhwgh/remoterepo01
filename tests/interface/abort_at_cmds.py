# responsible: christoph.dehm@thalesgroup.com
# author: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0088281.001
# note: converted from original TP: \\view\aktuell\z_pegasus_swt\test\hierarchies\it\misc\ThAbortAtCmds.xml [script]
#       passed with VIPER_100_120C
# LM0002980.005 - Abortable AT commands

""" description:
        run several long running AT-cmds and try to abort them by sending any character
        cmds should immediately abort current execution and show '+CME ERROR: 100/unknown' or a better error code

"""

import unicorn
from core.basetest import BaseTest
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.packet_domain.ps_attach_detach import dstl_ps_attach


class Test(BaseTest):
    def setup(test):
        test.tln_dut_nat = test.dut.sim.nat_voice_nr

        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_register_to_network()

        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2"))
        pass

    def run(test):
        dev1_nat_phone_nr = test.dut.sim.nat_voice_nr
        supservice_response = '.*\+CME ERROR: (302|TeleService not provisioned).*'

        test.log.step(' 1. network related commands')
        test._check_abortable_atcmd('at+cops=?', delay_for_abort=10, timeout=9)
        test.dut.at1.send_and_verify('at+cops=2', '.*OK.*', timeout=59)
        test._check_abortable_atcmd('at+cops=0', delay_for_abort=0.1, timeout=9)
        test.sleep(5)
        test.dut.at1.send_and_verify('ATI1', '.*OK.*')
        test._check_abortable_atcmd('at+copn', delay_for_abort=1.0)
        # reregister to get module working again
        test.dut.at1.send_and_verify('at+cops=2', '.*OK.*', timeout=59)
        test.sleep(2)
        test.dut.at1.send_and_verify('at+cops=0', '.*OK.*', timeout=59)
        test.sleep(4)
        test.expect(test.dut.at1.send_and_verify("AT+CGATT=1"))
        test.sleep(4)
        test.expect(test.dut.dstl_ps_attach())
        # test.expect(test.dut.at1.send_and_verify("AT+CGATT=1"))
        test.sleep(8)

        test.log.step(' 2. call related commands')
        test._check_abortable_atcmd(f'atd*21*{dev1_nat_phone_nr}#;', delay_for_abort=1)
        # CME:133 = requested service option not subscribed

        test.log.step(' 3. supplementary service commands ')
        # test._check_abortable_atcmd('at+cpol?', delay_for_abort=0.5) # too fast: does not work with a short list
        test._check_abortable_atcmd('at+clip?', delay_for_abort=2)
        test._check_abortable_atcmd('at+clir?', delay_for_abort=2)
        test._check_abortable_atcmd('at+ccfc=0,2', delay_for_abort=2)

        ret = test._check_abortable_atcmd('at+ccfc=1,3,"0987"', delay_for_abort=2)
        if ret is False:
            test.dut.at1.send_and_verify('at+ccfc=1,2', '.*OK.*', timeout=9)
            test.dut.at1.send_and_verify('at+ccfc=1,4', supservice_response)

        test._check_abortable_atcmd('at+clck="AI",2', delay_for_abort=2, abort_character='p')
        test._check_abortable_atcmd('at+clck="IR",2', delay_for_abort=2, abort_character='H')

        test._check_abortable_atcmd('at+ccwa=1,1,1', delay_for_abort=1.7, abort_character='q')

        test.log.step(' 4. SMS commands ')
        # AT-Spec:
        #  After invoking the write command wait for the prompt ">" and then start to write the message.
        # To send the message simply enter <Ctrl-Z> (o32, 0x1A), to abort sending use <ESC> (o33, 0x1B)
        test.dut.at1.send_and_verify('at+cmgf=1')
        test.dut.at1.send_and_verify('at+cmgd=1')
        test.dut.at1.send_and_verify('at+cmgd=2')
        test.dut.at1.send_and_verify(f'at+cmgs={dev1_nat_phone_nr}', expect="(?i)(\s|^)>(\s|$)",
                                     wait_for="(?i).*>.*")
        test.dut.at1.send_and_verify('', end="\u001B")       # ESC
        test.sleep(7)
        resp = test.dut.at1.last_response
        if '+CMT' in resp:
            test.expect(False, msg="SMS cmd was performed instead of aborted - please check for failure!")



        # VIPER: next step does not work (+CMSS=idx for text mode does not work to abort)
        # prepare a stored SMS for next check:
        '''
        test.last_stored_sms_idx = -1
        test.dut.at1.send_and_verify(f'at+cmgw={dev1_nat_phone_nr}', expect="(?i)(\s|^)>(\s|$)",
                                     wait_for="(?i).*>.*")
        test.dut.at1.send('stored SMS for abort_at_cmd script', end="\u001A")  # CTRL-Z
        ret = test.dut.at1.wait_for('+CMGW:', 95)
        if ret is True:
            resp = test.dut.at1.last_response
            resp = resp.split('+CMGW: ')[1]
            resp = resp.split('\r')[0]
            print("resp:", resp)
            if resp.isdigit():
                test.last_stored_sms_idx = resp
                test._check_abortable_atcmd(f'at+cmss={test.last_stored_sms_idx}', abort_character='k',
                                            delay_for_abort=2, timeout=5, expect='.*ERROR.*')
        else:
            test.log.h2(" h2 - what is it ?")
        '''

        test.log.step(' 5. packet data basic commands ')
        test.dut.at1.send_and_verify('at+cops=0', '.*OK.*', timeout=90)
        test._check_abortable_atcmd('at+cgatt=1', delay_for_abort=0.2, timeout=60)
        test.sleep(3)
        test.dut.at1.send_and_verify('at+cgatt?', '.*OK.*', timeout=19)
        # test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*', timeout=19)
        test.expect(test.dut.dstl_ps_attach())
        test._check_abortable_atcmd('at+cgatt=0', delay_for_abort=1, timeout=60)
        test.sleep(3)
        test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*', timeout=19)
        test._check_abortable_atcmd('at+cgact=1,1', delay_for_abort=2, timeout=60)
        test.dut.at1.send_and_verify('at+cgatt?', '.*OK.*', timeout=19)
        test.dut.at1.send_and_verify('at+cops=0', '.*OK.*', timeout=19)
        pass

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('ATi'))
        test.dut.at1.send_and_verify('at+cmgd=0')
        test.dut.at1.send_and_verify('at+cmgd=1')
        test.dut.at1.send_and_verify('at+cmgd=2')
        test.dut.at1.send_and_verify('at+cmgd=3')
        test.expect(test.dut.dstl_ps_attach())
        test.dut.dstl_register_to_network()
        pass

    def _check_abortable_atcmd(test, at_cmd, abort_character='G', delay_for_abort=2, timeout=5, expect='.*ERROR.*'):
        """ perform at_cmd, wait delay, and send abort_character, wait timeout for expect string
        :param at_cmd: at-cmd to perform
        :param abort_character: character to be send as abort character, default: 'G'
        :param delay_for_abort: wait time after at-cmd execution, default: 2 (seconds)
        :param timeout: wait after aborting for, default: 5 (seconds)
        :param expect: string which is expected within timeout, default: '.*ERROR.*'
        :return result of .wait_for()
        """
        if at_cmd is not '':
            test.dut.at1.send(at_cmd)
        test.sleep(delay_for_abort)
        test.dut.at1.send(abort_character, end="")
        return test.expect(test.dut.at1.wait_for(expect, timeout))


if "__main__" == __name__:
    unicorn.main()
