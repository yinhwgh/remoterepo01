#responsible: krzysztof.nowakowski@globallogic.com
#location: Wroclaw
#TC

import unicorn
from core.basetest import BaseTest
import re

from dstl.auxiliary.init import dstl_detect

module_with_midlet = ["JAKARTA", "BOXWOOD", "GINGER", "ODESSA"]
module_without_svn = ["ODESSA", "KINGSTON"]


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()

    def run(test):
        test.dut.software = clean_from_cdg_version(test.dut.software)
        test.dut.software_number = clean_from_cdg_version(test.dut.software_number)

        test.expect(test.dut.software == test.r1.software, msg="\nDUT: {}, REMOTE: {}".format(test.dut.software, test.r1.software))
        test.expect(test.dut.software_number == test.r1.software_number, msg="\nDUT: {}, REMOTE: {}".format(test.dut.software_number, test.r1.software_number))
        test.expect(test.dut.platform == test.r1.platform, msg="\nDUT: {}, REMOTE: {}".format(test.dut.platform, test.r1.platform))
        test.expect(test.dut.product == test.r1.product, msg="\nDUT: {}, REMOTE: {}".format(test.dut.product, test.r1.product))
        test.expect(test.dut.project == test.r1.project, msg="\nDUT: {}, REMOTE: {}".format(test.dut.project, test.r1.project))

        test.expect(test.dut.at1.send_and_verify("ATI1", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("ATI1", ".*OK.*"))
        test.expect(get_revision_number(test.dut.at1.last_response))
        test.expect(get_revision_number(test.dut.at1.last_response) == get_revision_number(test.r1.at1.last_response), msg="\nDUT: {}, REMOTE: {}".format(get_revision_number(test.dut.at1.last_response), get_revision_number(test.r1.at1.last_response)))
        test.expect(get_a_revision_number(test.dut.at1.last_response))
        test.expect(get_a_revision_number(test.dut.at1.last_response) == get_a_revision_number(test.r1.at1.last_response), msg="\nDUT: {}, REMOTE: {}".format(get_a_revision_number(test.dut.at1.last_response), get_a_revision_number(test.r1.at1.last_response)))

        test.expect(test.dut.at1.send_and_verify("ATI51", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("ATI51", test.dut.at1.last_response))

        if test.dut.project in module_with_midlet:
            test.expect(get_jrc_version(test.dut) == get_jrc_version(test.r1))
            test.expect(get_slae_version(test.dut) == get_slae_version(test.r1))

        if test.dut.project in module_without_svn:
            test.log.info("This product doesn't support this feature.")
        else:
            test.expect(get_svn_number(test.dut) == get_svn_number(test.r1))

    def cleanup(test):
        pass


def clean_from_cdg_version(software_number):
    return software_number.split("-CDG")[0]


def get_revision_number(response):
    result = re.search("(REVISION \d\d[.]\d\d\d)", response)
    return result.group(1) if result is not None else None


def get_a_revision_number(response):
    result = re.search("(A-REVISION \d\d[.]\d\d\d[.]\d\d)", response)
    return result.group(1) if result is not None else None


def get_svn_number(port):
    port.at1.send_and_verify("ATI176", "OK")
    result = re.search("\d+[.](\d+)", port.at1.last_response)
    return result.group(1) if result is not None else None


def get_jrc_version(port):
    port.at1.send_and_verify("AT^SJAM=4", "OK")
    result = re.search(":/JRC-(\d[.]\d\d[.]\d\d)", port.at1.last_response)
    return result.group(1) if result is not None else None


def get_slae_version(port):
    port.at1.send_and_verify("AT^SJAM=4", "OK")
    result = re.search("\^SJAM:.*?SLAE\.jad.*?\"([\d.]+)\"", port.at1.last_response)
    return result.group(1) if result is not None else None


if "__main__" == __name__:
    unicorn.main()

