# responsible: sebastian.lupkowski@globallogic.com
# location: Wroclaw
# TC0010530.001, TC0010530.002

import unicorn

import re
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """TC0010530.001/.002     IEIaConcatSms

    Write and send concatenated SMS with 8 and 16 bit reference number

    1) Send/write/read with 8/16 bit reference number
      1a. Send CON. SMS IEIA=8 bit and ref_nr 255 -> OK
      1b. Storage on DUT should be empty
      1c. Send CON. SMS IEIA=16 bit and ref_nr 65535 -> OK
      1d. Storage on DUT should be empty
      1e. Send CON. SMS with max_nr=255 -> OK
      1f. Storage on DUT should be empty
      1g. Write CON. SMS IEIA=8 bit and ref_nr 255 -> OK
      1h. Read SMS
      1i. Write CON. SMS IEIA=16 bit and ref_nr 65535 -> OK
      1j. Read SMS

    2) Send/write with larger than 8/16 bit reference number
      2a. Send CON. SMS IEIA=8 bit and ref_nr 256 -> ERROR ref_nr too big
      2b. Send CON. SMS IEIA=16 bit and ref_nr 65536 -> ERROR ref_nr too big
      2c. Send CON. SMS with max_nr=256 -> ERROR max nr too big
      2d. Send CON. SMS with seq larger than max -> ERROR seq nr too big
      2e. Write CON. SMS IEIA=8 bit and ref_nr 256 -> ERROR ref_nr too big
      2f. Write CON. SMS IEIA=16 bit and ref_nr 65536 -> ERROR ref_nr too big

    3a) Write with larger than 8 bit maximum number of segments
    3b) Write with larger sequence number than maximal number of segments

    4) Write/read with sequence number equals maximal number of segments
      4a. Write CON. SMS with max_nr=255 -> OK
      4b. Read SMS

    5) Write/read concat SMSes with status STO UNSENT and STO SENT
       5a. Write 1 CON. SMS with status STO SENT -> OK
       5b. Read SMS
       5c. Write 2 CON. SMS with status STO UNSENT -> OK
       5d. Read SMS
       5e. Sending all sms from storage on first module and reading on second module.
    """

    contents_send = [{'seq': '1', 'max': '2', 'ieia': '8', 'ref': '255',
                      'content': 'Send SMS IEIA=8 bit and ref_nr 255 -> O.K.', 'response': 'OK'},
                     {'seq': '1', 'max': '2', 'ieia': '16', 'ref': '65535',
                      'content': 'Send CON. SMS IEIA=16 bit and ref_nr 65535 -> O.K.', 'response': 'OK'},
                     {'seq': '255', 'max': '255', 'ieia': '8', 'ref': '16',
                      'content': 'Send CON. SMS with max_nr=255 -> O.K.', 'response': 'OK'},
                     {'seq': '2', 'max': '2', 'ieia': '8', 'ref': '256',
                      'content': '', 'response': 'ERROR'},
                     {'seq': '2', 'max': '2', 'ieia': '16', 'ref': '65536',
                      'content': '', 'response': 'ERROR'},
                     {'seq': '255', 'max': '256', 'ieia': '8', 'ref': '17',
                      'content': '', 'response': 'ERROR'},
                     {'seq': '2', 'max': '1', 'ieia': '8', 'ref': '19',
                      'content': '', 'response': 'ERROR'}
                     ]

    contents_write = [{'toda': '', 'status': '', 'seq': '1', 'max': '2', 'ieia': '8', 'ref': '255',
                       'content': 'Write SMS IEIA=8 bit and ref_nr 255 -> O.K.', 'response': 'OK'},
                      {'toda': '', 'status': '', 'seq': '1', 'max': '2', 'ieia': '16', 'ref': '65535',
                       'content': 'Write CON. SMS IEIA=16 bit and ref_nr 65535 -> O.K.', 'response': 'OK'},
                      {'toda': '', 'status': '', 'seq': '2', 'max': '2', 'ieia': '8', 'ref': '256',
                       'content': '', 'response': 'ERROR'},
                      {'toda': '', 'status': '', 'seq': '2', 'max': '2', 'ieia': '16', 'ref': '65536',
                       'content': '', 'response': 'ERROR'},
                      {'toda': '', 'status': '', 'seq': '255', 'max': '256', 'ieia': '8', 'ref': '17',
                       'content': '', 'response': 'ERROR'},
                      {'toda': '', 'status': '', 'seq': '2', 'max': '1', 'ieia': '8', 'ref': '19',
                       'content': '', 'response': 'ERROR'},
                      {'toda': '', 'status': '', 'seq': '255', 'max': '255', 'ieia': '8', 'ref': '16',
                       'content': 'Write CON. SMS with max_nr=255 -> O.K.', 'response': 'OK'},
                      {'toda': '145', 'status': '"STO SENT"', 'seq': '1', 'max': '2', 'ieia': '8', 'ref': '45',
                       'content': 'Write 1 CON. SMS with status STO SENT -> O.K.', 'response': 'OK'},
                      {'toda': '145', 'status': '"STO UNSENT"', 'seq': '2', 'max': '2', 'ieia': '8', 'ref': '45',
                       'content': 'Write 2 CON. SMS with status STO UNSENT -> O.K.', 'response': 'OK'},
                      ]
    sms_indexes = []

    def setup(test):
        test.log.h2("Starting TP for TC0010530.001/.002 - IEIaConcatSms")
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)

    def run(test):
        test.log.step("1) Send/write/read with 8/16 bit reference number")
        test.log.step("1a. Send CON. SMS IEIA=8 bit and ref_nr 255 -> OK")
        test.send_concat_sms_directly(test.contents_send[0])

        test.log.step("1b. Storage on DUT should be empty")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == 0)

        test.log.step("1c. Send CON. SMS IEIA=16 bit and ref_nr 65535 -> OK")
        test.send_concat_sms_directly(test.contents_send[1])

        test.log.step("1d. Storage on DUT should be empty")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == 0)

        test.log.step("1e. Send CON. SMS with max_nr=255 -> OK")
        test.send_concat_sms_directly(test.contents_send[2])

        test.log.step("1f. Storage on DUT should be empty")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == 0)

        test.log.step("1g. Write CON. SMS IEIA=8 bit and ref_nr 255 -> OK")
        test.write_concat_sms_to_memory(test.contents_write[0])
        test.get_scmw_index()

        test.log.step("1h. Read SMS")
        test.read_concat_sms(test.sms_indexes[0], test.contents_write[0])

        test.log.step("1i. Write CON. SMS IEIA=16 bit and ref_nr 65535 -> OK")
        test.write_concat_sms_to_memory(test.contents_write[1])
        test.get_scmw_index()

        test.log.step("1j. Read SMS")
        test.read_concat_sms(test.sms_indexes[1], test.contents_write[1])

        test.log.step("2) Send/write with larger than 8/16 bit reference number")
        test.log.step("2a. Send CON. SMS IEIA=8 bit and ref_nr 256 -> ERROR ref_nr too big")
        test.send_concat_sms_directly(test.contents_send[3])

        test.log.step("2b. Send CON. SMS IEIA=16 bit and ref_nr 65536 -> ERROR ref_nr too big")
        test.send_concat_sms_directly(test.contents_send[4])

        test.log.step("2c. Send CON. SMS with max_nr=256 -> ERROR max nr too big")
        test.send_concat_sms_directly(test.contents_send[5])

        test.log.step("2d. Send CON. SMS with seq larger than max -> ERROR seq nr too big")
        test.send_concat_sms_directly(test.contents_send[6])

        test.log.step("2e. Write CON. SMS IEIA=8 bit and ref_nr 256 -> ERROR ref_nr too big")
        test.write_concat_sms_to_memory(test.contents_write[2])

        test.log.step("2f. Write CON. SMS IEIA=16 bit and ref_nr 65536 -> ERROR ref_nr too big")
        test.write_concat_sms_to_memory(test.contents_write[3])

        test.log.step("3a) Write with larger than 8 bit maximum number of segments")
        test.write_concat_sms_to_memory(test.contents_write[4])

        test.log.step("3b) Write with larger sequence number than maximal number of segments")
        test.write_concat_sms_to_memory(test.contents_write[5])

        test.log.step("4) Write/read with sequence number equals maximal number of segments")
        test.log.step("4a. Write CON. SMS with max_nr=255 -> OK")
        test.write_concat_sms_to_memory(test.contents_write[6])
        test.get_scmw_index()

        test.log.step("4b. Read SMS")
        test.read_concat_sms(test.sms_indexes[2], test.contents_write[6])

        test.log.step("5) Write/read concat SMSes with status STO UNSENT and STO SENT")
        test.log.step("5a. Write 1 CON. SMS with status STO SENT -> OK")
        test.write_concat_sms_to_memory(test.contents_write[7])
        test.get_scmw_index()

        test.log.step("5b. Read SMS")
        test.read_concat_sms(test.sms_indexes[3], test.contents_write[7])

        test.log.step("5c. Write 2 CON. SMS with status STO UNSENT -> OK")
        test.write_concat_sms_to_memory(test.contents_write[8])
        test.get_scmw_index()

        test.log.step("5d. Read SMS")
        test.read_concat_sms(test.sms_indexes[4], test.contents_write[8])

        test.log.info("Clearing REM memory before receiving messages sent form DUT's memory")
        dstl_delete_all_sms_messages(test.r1)

        test.log.step("5e. Sending all sms from storage on first module and reading on second module.")
        for index in test.sms_indexes:
            test.expect(dstl_send_sms_message_from_memory(test.dut, index))
        test.expect(dstl_check_urc(test.r1, ".*\+CMTI:.*\"ME\",[\s]4.*", 360))
        test.expect(test.r1.at1.send_and_verify('AT^SCML="ALL"'))
        for index in [0, 1, 6, 7, 8]:
            test.expect(re.search(r".*{},{},{},{}.*[\r\n].*{}.*".format(test.contents_write[index]['seq'],
                                                                        test.contents_write[index]['max'],
                                                                        test.contents_write[index]['ieia'],
                                                                        test.contents_write[index]['ref'],
                                                                        test.contents_write[index]['content']),
                                  test.r1.at1.last_response))

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_delete_all_sms_messages(test.r1)

    def prepare_module(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_register_to_network(module))
        test.expect(module.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(module.at1.send_and_verify('AT+CNMI=2,1', '.*OK.*'))
        test.expect(dstl_set_preferred_sms_memory(module, 'ME'))
        test.expect(dstl_select_sms_message_format(module, 'Text'))
        dstl_delete_all_sms_messages(module)
        test.expect(dstl_set_sms_center_address(module))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', '.*OK.*'))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))

    def send_concat_sms_directly(test, content_dict):
        if content_dict['response'] == 'OK':
            if test.expect(test.dut.at1.send_and_verify('AT^SCMS="{}",,{},{},{},{}'
                                                                .format(test.r1.sim.int_voice_nr, content_dict['seq'],
                                                                        content_dict['max'],
                                                                        content_dict['ieia'], content_dict['ref']),
                                                        '.*>.*', wait_for='.*>.*')):
                test.expect(test.dut.at1.send_and_verify(content_dict['content'], end="\u001A", wait_for='.*OK.*'))

        else:
            test.expect(test.dut.at1.send_and_verify('AT^SCMS="{}",,{},{},{},{}'
                                                     .format(test.r1.sim.int_voice_nr, content_dict['seq'],
                                                             content_dict['max'], content_dict['ieia'],
                                                             content_dict['ref']),
                                                     '.*{}.*'.format(content_dict['response'])))

    def write_concat_sms_to_memory(test, content_dict):
        if content_dict['response'] == 'OK':
            if test.expect(test.dut.at1.send_and_verify('AT^SCMW="{}",{},{},{},{},{},{}'
                                                                .format(test.r1.sim.int_voice_nr, content_dict['toda'],
                                                                        content_dict['status'], content_dict['seq'],
                                                                        content_dict['max'], content_dict['ieia'],
                                                                        content_dict['ref']),
                                                        '.*>.*', wait_for='.*>.*')):
                test.expect(test.dut.at1.send_and_verify(content_dict['content'], end="\u001A", expect='.*OK.*'))

        else:
            test.expect(test.dut.at1.send_and_verify('AT^SCMW="{}",{},{},{},{},{},{}'
                                                     .format(test.r1.sim.int_voice_nr, content_dict['toda'],
                                                             content_dict['status'], content_dict['seq'],
                                                             content_dict['max'], content_dict['ieia'],
                                                             content_dict['ref']),
                                                     '.*{}.*'.format(content_dict['response'])))

    def read_concat_sms(test, index, content_dict):
        if index:
            test.expect(test.dut.at1.send_and_verify('AT^SCMR={}'.format(index), ".*OK.*"))
            test.expect(re.search(r'.*SCMR:.*{},"[+]{}".*{},{},{},{}.*[\r\n].*{}.*'
                                  .format(content_dict['status'], test.r1.sim.int_voice_nr[1:], content_dict['seq'],
                                          content_dict['max'], content_dict['ieia'], content_dict['ref'],
                                          content_dict['content']), test.dut.at1.last_response))
        else:
            test.expect(False, msg="Message not in memory")

    def get_scmw_index(test):
        try:
            test.sms_indexes.append(re.search(r".*SCMW:.*(\d{1,3}).*", test.dut.at1.last_response).group(1))
        except AttributeError:
            test.expect(False, msg="No SCMW index found!")


if "__main__" == __name__:
    unicorn.main()
