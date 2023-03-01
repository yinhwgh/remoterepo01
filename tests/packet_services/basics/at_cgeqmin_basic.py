# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0091878.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context
from dstl.security import lock_unlock_sim
import random
import re


class Test(BaseTest):
    """
    TC0091878.001 - TpAtCgeqminBasic
    This procedure provides the possibility of basic tests for the test and write command of +CGEQMIN.

    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.max_cid = test.dut.dstl_get_supported_max_cid()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.add_pdp = False

    def run(test):
        test_resp = '+CGEQMIN: "IP",(0-4),(0-11520),(0-42200),(0-11520),(0-42200),(0-2),(0,10-1520,1502),\
            ("0E0","1E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E4","1E5","1E6","6E8"),\
            (0-3),(0,100-150,200-950,1000-4000),(0-3)\s+'
        test_resp += '+CGEQMIN: "PPP",(0-4),(0-11520),(0-42200),(0-11520),(0-42200),(0-2),(0,10-1520,1502),\
            ("0E0","1E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E4","1E5","1E6","6E8"),\
            (0-3),(0,100-150,200-950,1000-4000),(0-3)\s+'
        test_resp += '+CGEQMIN: "IPV6",(0-4),(0-11520),(0-42200),(0-11520),(0-42200),(0-2),(0,10-1520,1502),\
            ("0E0","1E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E4","1E5","1E6","6E8"),\
            (0-3),(0,100-150,200-950,1000-4000),(0-3)\s+'
        test_resp += '+CGEQMIN: "IPV4V6",(0-4),(0-11520),(0-42200),(0-11520),(0-42200),(0-2),(0,10-1520,1502),\
            ("0E0","1E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E4","1E5","1E6","6E8"),\
            (0-3),(0,100-150,200-950,1000-4000),(0-3)\s+OK'
        test_resp = test_resp.replace('+', '\+').replace('(', '\(').replace(')', '\)')

        traffic_class = 4
        deliver_order_default = 2
        deliver_error_sdu_default = 3
        value_default = [traffic_class, '0', '0', '0', '0', deliver_order_default, '0', '0E0', '0E0',
                         deliver_error_sdu_default, '0', '0']

        test.log.step('1. Check command without and with PIN')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        pdp_cids = test.read_configured_cids()
        r_cid = random.choice(pdp_cids)
        test.log.step('1.1 Check command without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGEQMIN={r_cid}', 'OK'))
        test.log.step('1.2 Check command with PIN')
        test.expect(test.dut.dstl_register_to_network())
        test.clear_cgeqmin()
        test.log.info("check CGEQMIN Read Command - read the actual value, should be empty")
        test.expect(test.dut.at1.send_and_verify("AT+CGEQMIN?", ".*\\+CGEQMIN: \s+OK.*"))

        test.log.info(f"check CGEQMIN Write Command - write for cid {r_cid} the traffic class 4")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class}", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},0,0,0,0,{deliver_order_default},0,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - write for cid {r_cid} the max. bitrate UL value 128")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,0,0,0,{deliver_order_default},0,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - write for cid {r_cid} the max. bitrate DL value 128")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,0,0,{deliver_order_default},0,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - write for cid {r_cid} the guaranteed bitrate UL value 128")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,0,{deliver_order_default},0,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - write for cid {r_cid} the guaranteed bitrate DL value 128")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,{deliver_order_default},0,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info("check CGEQMIN Write Command - change for cid {r_cid} the delivery order")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,0,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} max. SDU size")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,10,"0E0","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} SDU error ratio")
        test.expect(
            test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\"", ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,10,"1E2","0E0",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - write for cid {r_cid} the Residual bit error ratio")
        test.expect(
            test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\"",
                                         ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,10,"1E2","5E3",{deliver_error_sdu_default},0,0\s+OK'))

        test.log.info("check CGEQMIN Write Command - write for cid {r_cid} the Delivery of erroneous SDUs")
        test.expect(
            test.dut.at1.send_and_verify(f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",1",
                                         ".*OK.*"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,10,"1E2","5E3",1,0,0\s+OK'))

        trasfer_delay = ['100', '150', '200', '950', '4000']
        for delay in trasfer_delay:
            test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Transfer delay to {delay}")
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",1,{delay}"))
            test.log.info("check CGEQMIN Read Command - read the actual value")
            test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                     f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,10,"1E2","5E3",1,{delay},0\s+OK'))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Traffic handling priority")
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",1,1000,1"))
        test.log.info("check CGEQMIN Read Command - read the actual value")
        test.expect(test.dut.at1.send_and_verify('AT+CGEQMIN?',
                                                 f'\+CGEQMIN: {r_cid},{traffic_class},128,128,128,128,1,10,"1E2","5E3",1,1000,1\s+OK'))

        test.log.step('2. Check for invalid parameters')
        error_msg = "\+CME ERROR: invalid index"
        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Traffic handling priority")
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",1,1000,-1", error_msg))
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",1,1000,4", error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Transfer delay \r\n" +
                      "SHOULD BE ERROR BUT AS SAMUEL IS OK THIS IS ALSO OK")
        # response may be different for products with "3851"
        invalid_transfer_delay = ['3851', '4001', '9']
        for delay in invalid_transfer_delay:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",1,{delay},1", error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Delivery of erroneous SDUs")
        invalid_deliver_error_sdu = ['-1', '4', f'"{deliver_error_sdu_default}"']
        for value in invalid_deliver_error_sdu:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,10,\"1E2\",\"5E3\",{value},100,1", error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Maximum SDU size \r\n" +
                      "SHOULD BE ERROR BUT AS SAMUEL IS OK THIS IS ALSO OK")
        invalid_max_sdu = ['11', '9', '1530']
        for value in invalid_max_sdu:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,1,{value},\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
                error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Delivery order")
        invlaid_deliver_order = ['-1', '3']
        for value in invlaid_deliver_order:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,128,{value},1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
                error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Guaranteed bitrate DL")
        invalid_guarant_bit_dl = ['-1', '65', '257']
        for value in invalid_guarant_bit_dl:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,128,{value},3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
                error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Guaranteed bitrate UL")
        invalid_guarant_bit_ul = ['-1', '65', '129']
        for value in invalid_guarant_bit_ul:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,128,{value},128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
                error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Maximum bitrate DL")
        invalid_max_bit_dl = ['-1', '65', '257', '513']
        for value in invalid_max_bit_dl:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},128,{value},128,128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
                error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Maximum bitrate UL")
        invalid_max_bit_ul = ['-1', '65', '129', '127', '257', '511', '513']
        for value in invalid_max_bit_ul:
            test.expect(test.dut.at1.send_and_verify(
                f"AT+CGEQMIN={r_cid},{traffic_class},{value},128,128,128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
                error_msg))

        test.log.info(f"check CGEQMIN Write Command - change for cid {r_cid} the Traffic class")
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN={r_cid},5,128,128,128,128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
            error_msg))
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN={r_cid},-1,128,128,128,128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
            error_msg))

        test.log.info(f"check CGEQMIN Write Command - use of the CGEQMIN write command with not supported CID")
        test.expect(test.dut.at1.send_and_verify(f"AT+CGEQMIN={test.max_cid + 1}", error_msg))
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN=-1,1,128,128,128,128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1", error_msg))
        test.expect(test.dut.at1.send_and_verify(
            f"AT+CGEQMIN={test.max_cid + 1},1,128,128,128,128,3,1520,\"1E2\",\"5E3\",\"{deliver_error_sdu_default}\",100,1",
            error_msg))

    def cleanup(test):
        test.clear_cgeqmin()
        if test.add_pdp == True:
            test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify("AT&F"))

    def clear_cgeqmin(test):
        test.log.h3("Clearing CGEQMIN configurations.")
        result = True
        test.dut.at1.send_and_verify(f"AT+CGEQMIN?")
        cids = re.findall("\+CGEQMIN: (\d+),", test.dut.at1.last_response)
        if cids:
            for cid in cids:
                test.dut.at1.send_and_verify(f"AT+CGEQMIN={cid}")
            test.dut.at1.send_and_verify("AT+CGEQMIN?")
            cids = re.findall("\+CGEQMIN: (\d+),", test.dut.at1.last_response)
            result = cids == []
        if result:
            test.log.info("Clear CGEQMIN configurations successfully.")
        else:
            test.log.error("Fail to clear CGEQMIN.")

    def read_configured_cids(test):
        test.log.h3("Reading configured cids.")
        test.dut.at1.send_and_verify("AT+CGDCONT?")
        cids = re.findall("\+CGDCONT: (\d+),", test.dut.at1.last_response)
        if len(cids) == 0:
            test.log.info("No profile found for pdp, add new one.")
            test.dut.at1.send_and_verify("AT+CGDCONT=1,\"IPV4V6\",\"apn\"")
            write_ok = test.dut.at1.send_and_verify("AT+CGDCONT?", "\+CGDCONT: 1")
            if write_ok:
                test.add_pdp = True
                cids.append(1)
        test.log.info(f"Read pdp context ids: {cids}")
        return cids


if (__name__ == "__main__"):
    unicorn.main()