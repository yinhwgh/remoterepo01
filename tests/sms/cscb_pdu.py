# responsible: krzysztof.osak@globallogic.com
# location: Wroclaw
# author: christoph.dehm@thalesgroup.com
# TC0011195.001 CscbPDU
# note: this TC was created to have an automatic test instead of testing manually as TC0011195.001 was originally


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_gsm
from dstl.sms.select_sms_format import dstl_select_sms_message_format


class Test(BaseTest):
    """
    TC0011195.001   CscbPdu

    NOTE on availability of CellBroadcast:
    - German providers have reduced the active channels to a minimum, unclear which are still active
    - only Ericsson test network shows CB messages, but only on 2G only.
      So, device has to register to GSM first to test CBM

    """

    def check_pdu_response(test, buffer=""):
        idx1 = buffer.find("+CBM")
        if idx1 < 0:
            return idx1     # nothing found

        errors = 0
        num_of_cbms = 0
        while idx1 >= 0:
            idx2 = buffer.find("\r\n", idx1+4)  # end of CBM-len, start of user data
            idx3 = buffer.find("\r\n", idx2+4)
            print("cbm len:", buffer[idx1:idx2])
            print("cbm msg:", buffer[idx2+2:idx3])
            # text = decodeGsm7(buffer[idx2+4:idx3])
            pdu_len = int(buffer[idx1+5:idx2])
            msg_len = len(buffer[idx2+2:idx3])
            print("cbm len", pdu_len)
            print("msg len", msg_len)
            num_of_cbms += 1
            if msg_len != pdu_len * 2:
                print("PDU len of", pdu_len, "is different to msg len of", msg_len)
                errors += 1

            idx1 = buffer.find("+CBM", idx3+4)
        print(num_of_cbms, "CBM messages verified,", errors, "errors found.")
        return errors, num_of_cbms

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
        # set to Text mode
        dstl_select_sms_message_format(test.dut, sms_format='PDU')
        # test.expect(test.dut.at1.send_and_verify("AT+CMGF=0", ".*OK.*"))
        pass

    def run(test):
        # clear all active CB channels:
        test.expect(test.dut.at1.send_and_verify("AT+CSCB=0", ".*OK.*"))

        # wait at least 18 sec
        test.log.info("wait for CB messages - wait for +CBM:")
        dstl_check_urc(test.dut, ".*CBM:.*", timeout=180)
        test.log.info("end of check_urc, wait again 1 minute")
        test.sleep(60)
        buf1 = test.dut.at1.last_response
        print(buf1)
        buf2 = test.dut.at1.read()
        print(buf2)
        buf = buf1 + buf2

        # check received messages if lengths of CBM: and real message is correct
        ret, num = test.check_pdu_response(buf)
        if ret != 0:
            test.expect(False, msg="PDU length of CBM messages are different to +CBM length indicator!")
        else:
            test.expect(True, msg="{}th CBM messages with correct length indicator found.".format(num))

        pass

    def cleanup(test):
        # disable CB message service:
        test.dut.at1.send_and_verify("AT+CSCB=1", ".*OK.*")

        # switch back to full network coverage
        test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*")
        test.sleep(3)
        test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*")
        dstl_register_to_network(test.dut)

        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")
        pass


if "__main__" == __name__:
    unicorn.main()
