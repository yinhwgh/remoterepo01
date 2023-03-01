#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091877.001

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
    TC0091877.001 - TpAtCgqminBasic
    This procedure provides the possibility of basic tests for the test and write command of +CGQMIN.

    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.max_cid = test.dut.dstl_get_supported_max_cid()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        # Tags presenting whether new PDP contexts are added for tests, if yes, delete in cleanup.
        test.add_pdp_1 = False
        test.add_pdp_2 = False

    def run(test):
        test_resp = '\+CGQMIN: "IP",\(0-3\),\(0-4\),\(0-5\),\(0-9\),\(0-18,31\)\s+'
        test_resp += '\+CGQMIN: "PPP",\(0-3\),\(0-4\),\(0-5\),\(0-9\),\(0-18,31\)\s+'
        test_resp += '\+CGQMIN: "IPV6",\(0-3\),\(0-4\),\(0-5\),\(0-9\),\(0-18,31\)\s+'
        test_resp += '\+CGQMIN: "IPV4V6",\(0-3\),\(0-4\),\(0-5\),\(0-9\),\(0-18,31\)\s+OK'
        test.log.step('1. Check command without and with PIN')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        pdp_cids = test.read_configured_cids()
        r_pdp_cid = random.choice(pdp_cids)
        r_non_pdp_cid = random.randint(1, test.max_cid)
        while str(r_non_pdp_cid) in pdp_cids:
            r_non_pdp_cid = random.randint(1, test.max_cid)
        test.log.step('1.1 Check command without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGQMIN={r_pdp_cid}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGQMIN={r_non_pdp_cid}', 'OK'))
        test.log.step('1.2 Check command with PIN')
        test.expect(test.dut.dstl_register_to_network())
        test.clear_cgqmin()
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=?', test_resp))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', "\+CGQMIN:.*OK"))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGQMIN=1', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=1,0,0,0,0,0', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=2,0,0,0,0,0', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', "\+CGQMIN: 1,0,0,0,0,0\s+\+CGQMIN: 2,0,0,0,0,0\s+OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=1,1,1,1,1,1', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', "\+CGQMIN: 1,1,1,1,1,1\s+\+CGQMIN: 2,0,0,0,0,0\s+OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=2,2,2,2,2,2', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', "\+CGQMIN: 1,1,1,1,1,1\s+\+CGQMIN: 2,2,2,2,2,2\s+OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=1', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', "\+CGQMIN: 2,2,2,2,2,2\s+OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN=2', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', "\+CGQMIN:\s+OK"))

        for i in range(1, test.max_cid + 1):
            if str(i) in pdp_cids:
                expect_resp = "OK"
            else:
                expect_resp = "\+CME ERROR: invalid index"
            test.expect(test.dut.at1.send_and_verify(f'AT+CGQMIN={i},1,1,1,1,1', expect_resp))

        test.log.step('2. Check for invalid parameters')
        invalid_params = ['-1,1,1,1,1,1', 
                        f'{test.max_cid + 1},1,1,1,1,1', 
                        '1,-1,1,1,1,1',
                        '1,4,1,1,1,1',
                        '1,1,-1,1,1,1',
                        '1,1,5,1,1,1',
                        '1,1,1,-1,1,1',
                        '1,1,1,6,1,1',
                        '1,1,1,1,-1,1',
                        '1,1,1,1,10,1',
                        '1,1,1,1,1,-1',
                        '1,1,1,1,1,19',
                        '1,1,1,1,1,32',
                        ]
        for param in invalid_params:
            test.dut.at1.send_and_verify(f'AT+CGQMIN={param}', '\+CME ERROR: invalid index')


    def cleanup(test):
        test.clear_cgqmin()
        if test.add_pdp_1 == True:
            test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1', 'OK'))
        if test.add_pdp_2 == True:
            test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=2', 'OK'))


    def clear_cgqmin(test):
        test.log.h3("Clearing CGQMIN configurations.")
        result = True
        test.dut.at1.send_and_verify(f"AT+CGQMIN?")
        cids = re.findall("\+CGQMIN: (\d+),", test.dut.at1.last_response)
        if cids:
            for cid in cids:
                test.dut.at1.send_and_verify(f"AT+CGQMIN={cid}")
            test.dut.at1.send_and_verify("AT+CGQMIN?")
            cids = re.findall("\+CGQMIN: (\d+),", test.dut.at1.last_response)
            result = cids == []
        if result:
            test.log.info("Clear CGQMIN configurations successfully.")
        else:
            test.log.error("Fail to clear CGQMIN.") 

    def read_configured_cids(test):
        test.log.h3("Reading configured cids.")
        test.dut.at1.send_and_verify("AT+CGDCONT?")
        cids = re.findall("\+CGDCONT: (\d+),", test.dut.at1.last_response)
        for cid in ['1', '2']:
            if cid not in cids:
                test.log.info(f"No profile found for cid {cid}, add new for tests.")
                test.dut.at1.send_and_verify(f"AT+CGDCONT={cid},\"IPV4V6\",\"apn{cid}\"")
                write_ok = test.dut.at1.send_and_verify("AT+CGDCONT?", "\+CGDCONT: {cid}")
                if write_ok:
                    if cid == '1':
                        test.add_pdp_1 = True
                    elif cid == '2':
                        test.add_pdp_2 = True
                    cids.append(cid)
        test.log.info(f"Read pdp context ids: {cids}")
        return cids
            



if (__name__ == "__main__"):
    unicorn.main()
