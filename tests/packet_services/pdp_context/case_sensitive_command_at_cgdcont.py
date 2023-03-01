#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0096561.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    TC0096561.001    CaseSensitiveCommandAtCgdcont

    Purpose of this TC is checking, if command parameters are not case sensitive.
    For CGDCONT command PDP type shouldn't be case sensitive.
    Ref. IPIS100232371.

    Define a command parameter using only lowercase letters, only uppercase letters and using both
    lowercase and uppercase letters
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        if test.dut.project.upper() == 'VIPER':
            test.dic_pdp_type_lowercase = {4: "ip", 5: "ppp", 6: "ipv6", 7: "ipv4v6"}
            test.dic_pdp_type_uppercase = {4: "IP", 5: "PPP", 6: "IPV6", 7: "IPV4V6"}
            test.dic_pdp_type_mix = {4: "Ip", 5: "PpP", 6: "Ipv6", 7: "IPv4v6"}
        else:
            test.dic_pdp_type_lowercase = {4: "ip", 5: "ipv6", 6: "ipv4v6"}
            test.dic_pdp_type_uppercase = {4: "IP", 5: "IPV6", 6: "IPV4V6"}
            test.dic_pdp_type_mix = {4: "Ip", 5: "Ipv6", 6: "IPv4v6"}

    def run(test):
        test.log.step("Define a command parameter using only lowercase letters, only uppercase letters and using both "
                      "lowercase and uppercase letters")

        test.log.info("Define a command parameter using only lowercase letters")
        test.define_and_check_pdp_contexts(test.dic_pdp_type_lowercase)

        test.log.info("Define a command parameter using only uppercase letters")
        test.define_and_check_pdp_contexts(test.dic_pdp_type_uppercase)

        test.log.info("Define a command parameter using both: lowercase and uppercase letters")
        test.define_and_check_pdp_contexts(test.dic_pdp_type_mix)

    def cleanup(test):
        for cid in test.dic_pdp_type_mix:
            test.dut.at1.send_and_verify("AT+CGDCONT={}".format(cid), ".*OK.*")

    def define_and_check_pdp_contexts(test, dic_pdp_type):
        for cid, pdp_type in dic_pdp_type.items():
            test.expect(
                test.dut.at1.send_and_verify("AT+CGDCONT={0},\"{1}\",\"internet{0}\"".format(cid, pdp_type),
                                             ".*OK.*"))

        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*"))
        for cid, pdp_type in test.dic_pdp_type_uppercase.items():
            cgdcont_regex = r".*{0},\"{1}\",\"internet{0}\".*".format(cid, pdp_type)
            test.log.info('Expected response: {}'.format(cgdcont_regex))
            test.expect(re.search(cgdcont_regex, test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
