# responsible: krzysztof.osak@globallogic.com
# location: Wroclaw
# author: christoph.dehm@thalesgroup.com
# TC0011135.001 CscbText
# note: this TC was created to have an automatic test instead of testing manually as TC0011135.001 was originally


import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_gsm
from dstl.sms.select_sms_format import dstl_select_sms_message_format


class Test(BaseTest):
    """
    TC0011135.001   CscbText

    NOTE on availability of CellBroadcast:
    - German providers have reduced the active channels to a minimum, unclear which are still active
    - only Ericsson test network shows CB messages, but only on 2G only.
      So, device has to register to GSM first to test CBM

    """

    def setup(test):
        test.log.info('According to additional info in TC Precondition section test will be executed on 1 module:'
                      '"For platforms: QCT, INTEL, SQN one module logged to the network is needed."')
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        imsi = test.dut.sim.imsi

        # check which operator is available
        if imsi.startswith("26295"):
            test.log.info(" SIM for Ericsson test network found - test can run.")
        else:
            test.expect(False, critical=True, msg=" no SIM for Ericsson test network found - abort!")

        # always register at 2G  -- CBMs are only available on 2G at Ericsson test network
        dstl_register_to_gsm(test.dut)

        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))

        # configure CB indications to TE
        # cnmi=2,1,2
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1,2", ".*OK.*"))
        pass

    def run(test):
        # set to Text mode
        dstl_select_sms_message_format(test.dut, sms_format='Text')

        # clear all active CB channels:
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=0", ".*OK.*"))

        # wait at least 18 sec
        test.log.info("wait for CB messages - wait for +CBM:")
        dstl_check_urc(test.dut, ".*CBM:.*", timeout=180)
        test.log.info("end of check_urc, wait again 1 minute")
        test.sleep(60)

        buf1 = test.dut.at1.last_response
        buf2 = test.dut.at1.read()
        buf = buf1 + buf2
        num = buf.count("+CBM: ")

        # +CBM: <sn>,<mid>,<dcs>,<page>,<pages> <CR> <LF> <data>
        # sn: int, serial number
        # mid: int, msg identifier
        # dcs: data coding scheme 0..247
        # page: page parameter bits 4..7
        # pages: page parameter bits 0..3

        res = re.findall(r"\+CBM: \d{1,2},\d{1,2},\d{1,3},\d,\d", buf)
        num_res = len(res)

        if num != num_res:
            test.log.info(res)
            test.expect(False, msg="+CBM: URCs found: {}, but found with correct syntax: {}".format(num, num_res))
        else:
            test.expect(True)
            test.log.info("all {} '+CMB:'-URCs have the correct syntax".format(num))
        pass

    def cleanup(test):
        # switch back to automatic network mode
        test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*")
        test.sleep(3)
        test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*")

        dstl_register_to_network(test.dut)
        # disable CB message service:
        test.dut.at1.send_and_verify("AT+CSCB=1", ".*OK.*")
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")
        pass


if "__main__" == __name__:
    unicorn.main()
