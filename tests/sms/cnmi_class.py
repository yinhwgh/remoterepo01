#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0103983.001, TC0103974.001, TC0103980.001, TC0103981.001, TC0103982.001, TC0103976.001, TC0103977.001, TC0103978.001,
#TC0103979.001, TC0103975.001
#TC0103983.002, TC0103974.002, TC0103980.002, TC0103981.002, TC0103982.002, TC0103976.002, TC0103977.002, TC0103978.002,
#TC0103979.002, TC0103975.002
import re
import time
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    This TP is meant for executing series of CnmiTextClassX / CnmiPDUClassX (where X - class of SMS message)
    Args:
        sms_class (String): class of SMS message (eg. '0', 'None').
        sms_mode (String): type of SMS mode ('Text', 'PDU')
    """

    tc_number = {
        '0': 'TC0103974.001/.002',
        '1': 'TC0103980.001/.002',
        '2': 'TC0103981.001/.002',
        '3': 'TC0103982.001/.002',
        'None': 'TC0103983.001/.002'
    }
    tc_number_pdu = {
        '0': 'TC0103976.001/.002',
        '1': 'TC0103977.001/.002',
        '2': 'TC0103978.001/.002',
        '3': 'TC0103979.001/.002',
        'None': 'TC0103975.001/.002'
    }
    sms_class_content = {
        '0': 'SMSclass0',
        '1': 'SMSclass1',
        '2': 'SMSclass2',
        '3': 'SMSclass3',
        'None': 'SMSclassNone'
    }
    sms_class_content_pdu = {
        '0': 'D3E674CC0ECFE730',
        '1': 'D3E674CC0ECFE731',
        '2': 'D3E674CC0ECFE732',
        '3': 'D3E674CC0ECFE733',
        'None': 'D3E674CC0ECFE74E'
    }
    sms_class_dcs = {
        '0': '240',
        '1': '241',
        '2': '242',
        '3': '243',
        'None': '0'
    }
    sms_class_dcs_pdu = {
        '0': '0010FF09',
        '1': '0011FF09',
        '2': '0012FF09',
        '3': '0013FF09',
        'None': '0000FF09'
    }
    mode_values = ['0', '1', '2']
    mt_values = ['0', '1', '2', '3']
    sms_time_out_default = 360
    sms_time_out_extended = 600
    sms_time_out = 0
    send_timeout = 180
    time_out_wait = 30
    cmgl_all = '"ALL"'
    cmgf_value = '1'
    rx_cmti_me = ".*\\+CMTI: \"ME\".*"
    rx_cmti_sm = ".*\\+CMTI: \"SM\".*"
    rx_cmt = ".*\\+CMT:.*"
    rx_cmt_urc_generic = ".*\\+CMT.*"
    rx_cmt_class0 = ".*\\+CMT:.*SMSclass0.*"
    rx_cmt_class0_pdu ='.*\\+CMT:.*\\n0.91.*D3E674CC0ECFE730.*'
    pdu_content_to_sent = ''
    dut_ssda_support = False

    def setup(test):
        test.sms_class = str(test.sms_class[1:])  # workaround for unicorn issue with passing parameters from .cfg
        test.sms_mode = str(test.sms_mode[1:])  # workaround for unicorn issue with passing parameters from .cfg
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)
        test.clear_sms_memory('SM')
        test.clear_sms_memory('ME')

    def run(test):
        if 'PDU' in test.sms_mode:
            test.rx_cmt_class0 = test.rx_cmt_class0_pdu
            test.sms_class_content = test.sms_class_content_pdu
            test.tc_number = test.tc_number_pdu
            test.cmgl_all = '4'
            test.cmgf_value = '0'

        test.log.h2("Starting TP for {} - Cnmi{}Class{}".format(test.tc_number[test.sms_class], test.sms_mode,
                                                                test.sms_class))

        if test.dut.project.upper() == 'SERVAL':
            test.sms_time_out = test.sms_time_out_extended
        else:
            test.sms_time_out = test.sms_time_out_default

        test.log.step('Step 1. On DUT and RMT select SMS {} format (AT+CMGF={})'.format(test.sms_mode, test.cmgf_value))
        test.expect(dstl_select_sms_message_format(test.dut, test.sms_mode))
        test.expect(dstl_select_sms_message_format(test.r1, test.sms_mode))

        if 'PDU' in test.sms_mode:
            test.log.step('Step 2. Prepare PDU of Class {} which will be send in following steps'
                          .format(test.sms_class))
            test.pdu_content_to_sent = '{}1100{}{}{}'.format(test.r1.sim.sca_pdu,
                                                             test.dut.sim.pdu,
                                                             test.sms_class_dcs_pdu[test.sms_class],
                                                             test.sms_class_content_pdu[test.sms_class])
            test.log.info('PDU content to be sent: {}'.format(test.pdu_content_to_sent))
        else:
            test.log.step('Step 2. On RMT set SMS class {} (AT+CSMP=17,167,0,{})'
                          .format(test.sms_class, test.sms_class_dcs[test.sms_class]))
            test.set_csmp(test.sms_class)

        test.log.step('Step 3. Check URCs - +CMT and +CMTI')
        for mode in test.mode_values:
            for mt in test.mt_values:
                test.log.step('Step 3.1. On DUT change SMS event reporting to mode={} and mt={}'.format(mode, mt))
                test.set_cnmi(mode, mt)

                test.log.step('Step 3.2. Send SMS from RMT to DUT')
                test.send_sms_from_remote(test.sms_class, test.sms_mode)

                step_3_3_urc = ''
                if not (mode is not '0' and ((test.sms_class is '0' and mt is not '0') or
                                        (mt is '2' and test.sms_class is not '2') or
                                        (mt is '3' and test.sms_class is '3'))):
                    step_3_3_urc = 'I'

                test.log.step('Step 3.3. Receive SMS on DUT and check URC +CMT{}'.format(step_3_3_urc))
                test.verify_cnmi_answer(mode, mt, test.sms_class)
                test.receive_sms(test.sms_class, mode, mt)
                if not (mode is '0' and mt is '0'):
                    test.log.info('Wait {} seconds before checking AT+CNMI values'.format(str(test.time_out_wait)))
                    test.sleep(test.time_out_wait)

                test.log.step('Step 3.4. Verify AT+CNMI values')
                test.verify_cnmi_parameters(mode, mt, test.sms_class)

                if not (mode is '2' and mt is '3'):
                    test.log.step('Step 3.5. Repeat steps 3.1-3.4 with all supported and values(mode,mt) '
                                  'in +CNMI command.')
                if test.sms_class is '2':
                    if not (mode is '2' and mt is '3'):
                        test.log.info('Deleting messages from SM memory and setting back to ME memory')
                        test.clear_sms_memory('SM')
                        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", "all"))
                else:
                    test.log.info('Deleting messages from ME memory')
                    test.clear_sms_memory('ME')

        if test.sms_class is not '2':
            if test.sms_class is '0' or test.sms_class is '3':
                mt_step4 = test.mt_values[2:]
            else:
                mt_step4 = test.mt_values[2:3]

            test.log.step('Step 4. Test of SMS retransmission')
            for mode in test.mode_values:
                for mt in mt_step4:
                    test.log.step('Step 4.1. On DUT change SMS event reporting to mode={} and mt={}'.format(mode, mt))
                    test.set_cnmi(mode, mt)

                    test.log.step('Step 4.2. Send SMS from RMT to DUT')
                    test.send_sms_from_remote(test.sms_class, test.sms_mode)

                    test.log.step('Step 4.3. Wait for URC +CMT on DUT')
                    if mode is not '0':
                        test.log.info('+CMT should be received')
                        cmt_content = ''
                        if 'PDU' in test.sms_mode:
                            cmt_content = '{}{}.*'.format(test.rx_cmt, test.sms_class_content_pdu[test.sms_class])
                        else:
                            cmt_content = '{}{}.*'.format(test.rx_cmt, test.sms_class_content[test.sms_class])
                        test.expect(test.dut.at1.wait_for(cmt_content, timeout=test.sms_time_out))
                    else:
                        test.log.info("+CMT shouldn't be received")
                        test.expect(test.check_no_urc(test.rx_cmt_urc_generic, test.sms_time_out))

                    test.log.step('Step 4.4. Wait few minutes for retransmission.')
                    test.sleep(test.sms_time_out)

                    test.log.step('Step 4.5. Check received messages on DUT.')
                    test.check_retransmitted_messages(test.sms_class)

                    test.log.step('Step 4.6. Check AT+CNMI parameters.')
                    test.check_cnmi_reset(mode)

                    if not (mode is '2' and mt is mt_step4[-1]):
                        test.log.step('Step 4.7. Repeat steps 4.1-4.6 with all supported values(mode,mt) '
                                      'in +CNMI command that cause retransmission')

                    if not (test.dut_ssda_support and mode is '2' and mt is mt_step4[-1]):
                        test.log.info('Deleting messages from ME memory')
                        test.clear_sms_memory('ME')

        if test.sms_class is '0' and test.dut_ssda_support:
            test.log.step('Step 5. Test of AT^SSDA command (display an incoming Class 0 short message directly '
                          'to the user or to store it automatically in the SMS memory) (only for some QCT modules)')
            for mt in ['1', '3']:
                test.log.step('Step 5.1. Set AT^SSDA=0 and AT+CNMI=2,{},0,0,1 on DUT.'.format(mt))
                test.set_ssda('0')
                test.set_cnmi('2', mt)

                test.log.step('Step 5.2. Send SMS from RMT to DUT')
                test.send_sms_from_remote(test.sms_class, test.sms_mode)

                test.log.step('Step 5.3. Wait for URC +CMTI on DUT')
                test.expect(test.dut.at1.wait_for(test.rx_cmti_me, timeout=test.sms_time_out))
                test.check_retransmitted_messages(test.sms_class)

                test.log.step('Step 5.4. Set AT^SSDA=1 on DUT')
                test.set_ssda('1')

                test.log.step('Step 5.5. Send SMS from RMT to DUT')
                test.send_sms_from_remote(test.sms_class, test.sms_mode)

                test.log.step('Step 5.6. Wait for URC +CMT on DUT')
                test.expect(test.dut.at1.wait_for(test.rx_cmt_class0, timeout=test.sms_time_out))

                if mt is '1':
                    test.clear_sms_memory('ME')
                    test.log.step('Step 5.7. Repeat steps 5.1-5.6 with mt = 3')
        else:
            test.log.info('SSDA not supported, step omitted')

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def receive_sms(test, sms_class, mode, mt):
        if sms_class is '2':
            dstl_set_preferred_sms_memory(test.dut, "SM", "all")
        else:
            dstl_set_preferred_sms_memory(test.dut, "ME", "all")
        if sms_class is '0':
            test.receive_sms_class_0(mode, mt)
        elif sms_class is '1':
            test.receive_sms_class_1(mode, mt)
        elif sms_class is '2':
            test.receive_sms_class_2()
        elif sms_class is '3':
            test.receive_sms_class_3(mode, mt)
        else:
            test.receive_sms_class_none(mode, mt)

    def receive_sms_class_0(test, mode, mt):
        if (mode is '0' and mt is not '1') or (mode is not '0' and mt is '0'):
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all),
                                                     ".*{}.*OK.*".format(test.sms_class_content['0'])))
        elif (mode is '0' and mt is '1') or (mode is not '0' and mt is not '0'):
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all), ".*OK.*"))
            test.expect(not re.search(test.sms_class_content['0'], test.dut.at1.last_response))

    def receive_sms_class_1(test, mode, mt):
        if (mode is '0') or (mode is not '0' and mt is not '2'):
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all),
                                                     ".*{}.*OK.*".format(test.sms_class_content['1'])))
        elif mode is not '0' and mt is '2':
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all), ".*OK.*"))
            test.expect(not re.search(test.sms_class_content['1'], test.dut.at1.last_response))

    def receive_sms_class_2(test):
        test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all),
                                                 ".*{}.*OK.*".format(test.sms_class_content['2'])))

    def receive_sms_class_3(test, mode, mt):
        if (mode is '0') or (mode is not '0' and (mt is '0' or mt is '1')):
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all),
                                                     ".*{}.*OK.*".format(test.sms_class_content['3'])))
        elif mode is '0' and (mt is '2' or mt is '3'):
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all), ".*OK.*"))
            test.expect(not re.search(test.sms_class_content['3'], test.dut.at1.last_response))

    def receive_sms_class_none(test, mode, mt):
        if (mode is '0' and mt is not '4') or (mode is not '0' and mt is not '2'):
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all),
                                                     ".*{}.*OK.*".format(test.sms_class_content['None'])))
        elif mode is not '0' and mt is '2':
            test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all), ".*OK.*"))
            test.expect(not re.search(test.sms_class_content['None'], test.dut.at1.last_response))

    def verify_cnmi_urc(test, is_urc, is_cmt, sms_class, is_class0_mode0_mt1):
        if not is_urc:
            if is_class0_mode0_mt1:
                test.log.info("SMS shouldn't be stored (transfer&ack). No +CMTI and +CMT.")
            else:
                test.log.info('SMS should be stored. No +CMTI and +CMT.')
            test.expect(test.check_no_urc(test.rx_cmt_urc_generic, test.sms_time_out))
        elif not is_cmt:
            test.log.info('SMS should be stored. Wait for +CMTI.')
            if sms_class is '2':
                test.expect(test.dut.at1.wait_for(test.rx_cmti_sm, timeout=test.sms_time_out))
            else:
                test.expect(test.dut.at1.wait_for(test.rx_cmti_me, timeout=test.sms_time_out))
        else:
            test.log.info("SMS shouldn't be stored. Wait for +CMT.")
            cmt_content = ''
            if 'PDU' in test.sms_mode:
                cmt_content = '{}{}.*'.format(test.rx_cmt, test.sms_class_content_pdu[test.sms_class])
            else:
                cmt_content = '{}{}.*'.format(test.rx_cmt, test.sms_class_content[test.sms_class])
            test.expect(test.dut.at1.wait_for(cmt_content, timeout=test.sms_time_out))

    def verify_cnmi_answer(test, mode, mt, sms_class):
        is_urc = True
        is_cmt = False
        is_cnma = False
        is_class0_mode0_mt1 = False

        if mode is '0' and mt is '1' and sms_class is '0':
            is_class0_mode0_mt1 = True

        if mode is '0' or mt is '0':
            is_urc = False
            is_cmt = False

        if mode is not '0' and mt is not '0':
            is_urc = True
            if mt is '1' and sms_class is '0':
                is_cmt = True
            elif mt is '2' and sms_class is not '2':
                is_cmt = True
                is_cnma = True
            elif mt is '3' and sms_class is '0':
                is_cmt = True
                is_cnma = True
            elif mt is '3' and sms_class is '3':
                is_cmt = True
                is_cnma = True
            else:
                is_cmt = False

        test.verify_cnmi_urc(is_urc, is_cmt, sms_class, is_class0_mode0_mt1)
        if is_cnma:
            test.expect(test.dut.at1.send_and_verify("AT+CNMA", ".*OK.*"))

    def set_ssda(test, mode):
        test.expect(test.dut.at1.send_and_verify("AT^SSDA={}".format(mode), ".*OK.*"))

    def set_cnmi(test, mode, mt):
        test.expect(test.dut.at1.send_and_verify("AT+CNMI={},{},0,0,1".format(mode, mt), ".*OK.*"))

    def check_cnmi_reset(test, mode):
        test.expect(test.dut.at1.send_and_verify("AT+CNMI?", ".*\\+CNMI:.*{},0,0,0,1.*OK.*".format(mode)))

    def set_csmp(test, sms_class):
        test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(test.sms_class_dcs[sms_class]), ".*OK.*"))

    def check_retransmitted_messages(test, sms_class):
        test.expect(test.dut.at1.send_and_verify('AT+CMGL={}'.format(test.cmgl_all), ".*{}.*OK.*"
                                                 .format(test.sms_class_content[sms_class])))

    def verify_cnmi_parameters(test, mode, mt, sms_class):
        test.dut.at1.send_and_verify("AT+CNMI?", ".*OK.*")
        if mode is '0' and ((mt is '2' and sms_class is not '2') or
                            (mt is '3' and (sms_class is '0' or sms_class is '3'))):
            cnmi_regex = r".*[+]CNMI:.*{},0,0,0,1.*".format(mode)
        else:
            cnmi_regex = r".*[+]CNMI:.*{},{},0,0,1.*".format(mode, mt)
        test.log.info('Expected response: {}'.format(cnmi_regex))
        test.expect(re.search(cnmi_regex, test.dut.at1.last_response))

    def send_sms_from_remote(test, sms_class, mode):
        if 'PDU' in mode:
            if test.expect(test.r1.at1.send_and_verify('AT+CMGS=22', '.*>.*', wait_for='.*>.*')):
                test.expect(test.r1.at1.send_and_verify(test.pdu_content_to_sent, end="\u001A", expect='.*OK.*'))
        else:
            if test.expect(test.r1.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.int_voice_nr),
                                                       '.*>.*', wait_for='.*>.*')):
                test.expect(
                    test.r1.at1.send_and_verify(test.sms_class_content[sms_class], end="\u001A", expect='.*OK.*'))

    def clear_sms_memory(test, memory):
        test.expect(dstl_set_preferred_sms_memory(test.dut, memory, 'all'))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def prepare_module(test, module):
        dstl_detect(module)
        test.expect(dstl_get_imei(module))
        test.expect(dstl_get_bootloader(module))
        test.expect(dstl_register_to_network(module))
        test.expect(module.at1.send_and_verify('AT+CSMS=1', ".*OK.*"))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify('AT+CSCA="{}"'.format(module.sim.sca_int), ".*OK.*"))
        if module.project.upper() == 'BOBCAT'or module.project.upper() == 'VIPER' or module.project.upper() == 'MIAMI':
            test.expect(module.at1.send_and_verify('AT^SIND="message",1', ".*OK.*"))
            test.set_ssda('1')
            if module == test.dut:
                test.dut_ssda_support = True
        else:
            test.log.info('AT^SIND="message",1 and AT^SSDA=1 commands not supported, step omitted')
        test.expect(dstl_set_preferred_sms_memory(module, "ME", "all"))

    def check_no_urc(test, urc, timeout):
        elapsed_seconds = 0
        start_time = time.time()
        result = True
        while elapsed_seconds < timeout:
            if re.search(urc, test.dut.at1.last_response):
                result = False
                break
            elapsed_seconds = time.time() - start_time
        return result


if "__main__" == __name__:
    unicorn.main()
