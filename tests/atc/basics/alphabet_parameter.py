#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0011601.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.configuration import character_set
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.internet_service import get_service_tags
import re

class Test(BaseTest):
    """
    TC0011601.001 -  AlphabetParameter
    Testing alphabet parameter (GSM, UCS2 and IRA) for bearer and service profiles
    Only check character set conversion, without opening network service
    """

    def setup(test):
        # Service profile dictionaries, all keys should be in lower case
        test.http_profile_id = 0
        test.http_profile = {
            'srvtype': 'Http',
            'conid': '1',
            'address': r'http://www.httpbin.org/post',
            'cmd': 'POST',
            'hccontlen': '15',
            'tcpmr': '10',
            'tcpot': '6000',
            'files': 'http_alphabet.txt',
            'hccontent': 'Test of http profile alphabet',
            'hcusragent': '60',  # Dingo
            'hcuseragent': '60',
            'hcprop': 'Accept-Encoding: identity',
            'user': 'usr_name',
            'passwd': 'gemalto',
            'alphabet': '1',
            'ipver': '4',
            'secopt': '0',
            'hcmethod': "1",
            'hcredir': "0",
            'hcauth': "1"
        }
        test.socket_profile_id = 1
        test.socket_profile = {
            'srvtype': 'Socket',
            'conid': '2',
            'address': 'sockudp://:80',
            'tcpmr': '10',
            'tcpot': '6000',
            'alphabet': '1',
            'ipver': '4',
            'secopt': '0'
        }
        test.ftp_profile_id = 2
        test.ftp_profile = {
            'srvtype': 'Ftp',
            'conid': '3',
            'address': r'ftp://jinyatuo_ext:LS123456@139.198.2.12',
            'cmd': 'POST',
            'tcpmr': '10',
            'tcpot': '6000',
            'ftpath': 'file:///a:/',
            'files': 'ftp_alphabet.txt',
            'user': 'usr',
            'passwd': 'gemalto',
            'alphabet': '1',
            'ipver': '4',
            'secopt': '0'
        }
        test.internet_profile_id = 1
        test.internet_profile = {
            'contype': 'GPRS0',
            'user': 'gemalto',
            'passwd': 'gemalto_pwd',
            'apn': 'cmnet',
            'inactto': '30',
            'dns1': '255.255.255.1',
            'dns2': '192.168.122.1',
            'ipv6dns1': '[240C::6666]',
            'ipv6dns2': '[240C::6644]',
            'alphabet': '1'
        }
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin(), critical=True)
        test.expect(test.dut.dstl_set_character_set("GSM"))

    def run(test):
        test.log.frame("1. Test with alphabet = 1")

        test.log.step("1.1 Set HTTP profile with the tags configured in <product>.cfg file, alphabet: 1")
        http_tags = test.dut.dstl_get_http_mandatory_tags() + test.dut.dstl_get_http_optional_tags()
        for srv_tag in http_tags:
            if srv_tag.lower() in test.http_profile:
                test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                            format(test.http_profile_id, srv_tag, test.http_profile[srv_tag.lower()]), "OK"))
            else:
                test.log.error("Service tag \"{}\" should be defined in test.http_profile".format(srv_tag.lower()))

        test.log.step("1.2 Set SOCKET profile with the tags configured in <product>.cfg file, alphabet: 1")
        socket_tags = test.dut.dstl_get_socket_mandatory_tags() + test.dut.dstl_get_socket_optional_tags()
        for srv_tag in socket_tags:
            if srv_tag.lower() in test.socket_profile:
                test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                         format(test.socket_profile_id, srv_tag,
                                                                test.socket_profile[srv_tag.lower()]), "OK"))
            else:
                test.log.error("Service tag \"{}\" should be defined in test.socket_profile".format(srv_tag.lower()))

        test.log.step("1.3 Set FTP profile with the tags configured in <product>.cfg file, alphabet: 1")
        ftp_tags = test.dut.dstl_get_ftp_mandatory_tags() + test.dut.dstl_get_ftp_optional_tags()
        for srv_tag in ftp_tags:
            if srv_tag.lower() in test.ftp_profile:
                if srv_tag.lower() == "address":
                    set_result = test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                              format(test.ftp_profile_id, srv_tag,
                                                                     test.ftp_profile[srv_tag.lower()]), "OK")
                    if not set_result:
                        test.ftp_profile["address"] = test.ftp_profile["address"].replace(r'@', r'\00')
                        test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                                 format(test.ftp_profile_id, srv_tag,
                                                                        test.ftp_profile[srv_tag.lower()]), "OK"))
                else:
                    test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                         format(test.ftp_profile_id, srv_tag,
                                                                test.ftp_profile[srv_tag.lower()]), "OK"))
            else:
                test.log.error("Service tag \"{}\" should be defined in test.ftp_profile".format(srv_tag.lower()))

        test.log.step("1.4 Set internet connection profile with the tags configured in <product>.cfg file, alphabet: 1")
        internet_tags = test.dut.dstl_get_internet_mandatory_tags() + test.dut.dstl_get_internet_optional_tags()
        alphabet_in_sics = False
        if 'alphabet' in internet_tags:
            alphabet_in_sics = True
        for con_tag in internet_tags:
            if con_tag.lower() in test.internet_profile:
                test.expect(test.dut.at1.send_and_verify("at^sics={},\"{}\",\"{}\"".
                            format(test.internet_profile_id, con_tag, test.internet_profile[con_tag.lower()]), "OK"))
            else:
                test.log.error("Service tag \"{}\" should be defined in test.internet_profile".format(con_tag.lower()))

        test.log.step("1.5 When alphabet is 1, character set should not vary with +CSCS: GSM")
        test.expect(test.dut.at1.send_and_verify("at^siss?", "OK", "OK"))
        last_response = test.dut.at1.last_response
        test.check_siss_profile("http", last_response)
        test.check_siss_profile("socket", last_response)
        test.check_siss_profile("ftp", last_response)
        test.check_sics_profile()

        test.log.step("1.6 When alphabet is 1, character set should not vary with +CSCS: UCS2")
        test.expect(test.dut.dstl_set_character_set("UCS2"))
        test.expect(test.dut.at1.send_and_verify("at^siss?", "OK", "OK"))
        last_response = test.dut.at1.last_response
        test.check_siss_profile("http", last_response)
        test.check_siss_profile("socket", last_response)
        test.check_siss_profile("ftp", last_response)
        test.check_sics_profile()

        test.log.frame("2 Character set of internet profile can be controlled by its own alphabet, "
                       "^siss - > alphabet: 1, ^sics - > alphabet: 0")
        if alphabet_in_sics:
            test.log.step("2.1 ^siss - > alphabet: 1, ^sics - > alphabet: 0, +CSCS: GSM")
            test.expect(test.dut.dstl_set_character_set("GSM"))
            test.internet_profile['alphabet'] = '0'
            test.expect(test.dut.at1.send_and_verify("at^sics={},\"{}\",\"{}\"".
                                                     format(test.internet_profile_id, "alphabet", "0")))
            test.check_sics_profile(is_ucs2=False)
            test.log.step("2.2 ^siss - > alphabet: 1, ^sics - > alphabet: 0, +CSCS: UCS2")
            test.expect(test.dut.dstl_set_character_set("UCS2"))
            test.check_sics_profile(is_ucs2=True)
        else:
            test.log.com("Internet profile of product {} does not support alphabet.".format(test.dut.project))

        test.log.frame("3. Test with alphabet = 0")
        test.expect(test.dut.dstl_set_character_set("GSM"))
        test.http_profile['alphabet'] = '0'
        test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                 format(test.http_profile_id, "alphabet", "0")))
        test.socket_profile['alphabet'] = '0'
        test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                 format(test.socket_profile_id, "alphabet", "0")))
        test.ftp_profile['alphabet'] = '0'
        test.expect(test.dut.at1.send_and_verify("at^siss={},\"{}\",\"{}\"".
                                                 format(test.ftp_profile_id, "alphabet", "0")))

        test.log.step("3.1 Check profile when alphabet is 0, character set is GSM")
        test.expect(test.dut.at1.send_and_verify("at^siss?", "OK", "OK"))
        last_response = test.dut.at1.last_response
        test.check_siss_profile("http", last_response)
        test.check_siss_profile("socket", last_response)
        test.check_siss_profile("ftp", last_response)
        test.check_sics_profile()

        test.log.step("3.2 Check profile when alphabet is 0, character set is UCS2")
        test.expect(test.dut.dstl_set_character_set("UCS2"))
        test.expect(test.dut.at1.send_and_verify("at^siss?", "OK", "OK"))
        last_response = test.dut.at1.last_response
        test.check_siss_profile("http", last_response, is_ucs2=True)
        test.check_siss_profile("socket", last_response, is_ucs2=True)
        test.check_siss_profile("ftp", last_response, is_ucs2=True)
        if alphabet_in_sics:
            test.check_sics_profile(is_ucs2=True)

    def cleanup(test):
        test.expect(test.dut.dstl_restart())

    def check_siss_profile(test, service_type, response, is_ucs2=False):
        test.log.info("****** Verify profile value of {}, is_ucs2: {}".format(service_type, is_ucs2))

        # Read response of AT^SISS
        if not response:
            test.expect(test.dut.at1.send_and_verify("at^siss?", "OK", "OK"))
            response = test.dut.at1.last_response

        # Get "profile id", "profile dictionary" according to service type
        exec('profile_id=test.{}_profile_id'.format(service_type))
        exec('profile_dict=test.{}_profile'.format(service_type))

        # Read content from specified profile id
        profile_pattern = "\^SISS: {},(\S.*\S)".format(locals()['profile_id'])
        profile_configs = re.findall(profile_pattern, response)
        test.expect(len(profile_configs) > 0, msg="Cannot parse {} response of at^siss.".format(service_type))

        # Verify value of each tag
        for config in profile_configs:
            actual_tag = config.split(',')[0].strip('"')
            actual_tag_value = config.split(',')[1].strip('"')
            if actual_tag.lower() in locals()['profile_dict'].keys():
                expected_tag_value = locals()['profile_dict'][actual_tag.lower()]
                if actual_tag.lower() == 'passwd':
                    expected_tag_value = '*****'
                # UCS2 format
                if is_ucs2:
                    expected_tag_value_ucs2 = test.dut.dstl_convert_to_ucs2(expected_tag_value)
                    test.expect(actual_tag_value == expected_tag_value_ucs2,
                                msg="tag: {}, expected value: {}, expected usc2 value: {}, actual value: {}".
                                format(actual_tag, expected_tag_value, expected_tag_value_ucs2, actual_tag_value))
                # Plain text
                else:
                    test.expect(expected_tag_value == actual_tag_value,
                                msg="profile: {}, tag: {}, expected value: {}, actual value: {}".
                                format(service_type, actual_tag, expected_tag_value, actual_tag_value))
            else:
                test.log.error("Cannot find information of {} in defined {} profile".format(actual_tag, service_type))

    def check_sics_profile(test, response=None, is_ucs2=False):
        test.log.info("****** Verify internet profile value, is_ucs2: {}".format(is_ucs2))

        # Read response of AT^SICS
        if not response:
            test.expect(test.dut.at1.send_and_verify("at^sics?", "OK", "OK"))
            response = test.dut.at1.last_response
        # Read content from specified profile id
        profile_pattern = "\^SICS: {},(\S.*\S)".format(test.internet_profile_id)
        profile_configs = re.findall(profile_pattern, response)
        test.expect(len(profile_configs) > 0, msg="Cannot parse response of at^sics with conProfileId - {}".format(test.internet_profile_id))

        # Verify value of each tag
        for config in profile_configs:
            actual_tag = config.split(',')[0].strip('"')
            actual_tag_value = config.split(',')[1].strip('"')
            if actual_tag.lower() in test.internet_profile:
                expected_tag_value = test.internet_profile[actual_tag.lower()]
                if actual_tag.lower() == 'passwd':
                    expected_tag_value = '*****'
                # UCS2 format
                if is_ucs2:
                    expected_tag_value_ucs2 = test.dut.dstl_convert_to_ucs2(expected_tag_value)
                    test.expect(actual_tag_value == expected_tag_value_ucs2,
                                msg="tag: {}, expected value: {}, expected usc2 value: {}, actual value: {}".
                                format(actual_tag, expected_tag_value, expected_tag_value_ucs2, actual_tag_value))
                # Plain text
                else:
                    test.expect(expected_tag_value == actual_tag_value,
                                msg="profileId: {}, tag: {}, expected value: {}, actual value: {}".
                                format(test.internet_profile_id, actual_tag, expected_tag_value, actual_tag_value))
            else:
                test.log.error("Cannot find information of {} in defined profile - ".format(actual_tag, test.internet_profile_id))


if "__main__" == __name__:
    unicorn.main()
