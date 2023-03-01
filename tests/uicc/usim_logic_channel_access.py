#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0095127.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.security import lock_unlock_sim
from dstl.network_service import register_to_network
from dstl.usim import get_df_name

df_name=""

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_restart()
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        time.sleep(5)
        global df_name
        df_name = test.dut.dstl_get_df_name('01')
        return


    def run(test):
        test.log.info('***Test start***')
        test.log.info('***Restart module without enterpin')
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.log.info('***Open Logical Channel test, write and read command')
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO?', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=0', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=-1', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=a', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO="A0001122334455667788990011223344"', ".*CME ERROR.*"))
        test.log.info('***Close Logical Channel test, write and read command')
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC?', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=0', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=1', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=2', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=3', ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=-1', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=a', ".*CME ERROR.*"))
        test.log.info('***Generic Logical Channel Access test, write and read command')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA?', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,8,21', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,8,"01"', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=-1', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify(' AT+CGLA=a', ".*CME ERROR.*"))
        test.log.info('***Check "status" with Restricted SIM Access command.')
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=242', '.*CRSM: 144,0,"62.*OK.*'))
        test.log.info('***Check "get response" of EF_DIR(2F00) with Restricted SIM Access command.')
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=192,12032', '.*CRSM: 144,0,"62.*OK.*'))
        test.log.info('***Check "read record" for 1st record of EF_DIR with Restricted SIM Access command')
        test.expect(test.dut.at1.send_and_verify('at+CRSM=178,12032,1,4,00','.*CRSM: 144,0,"61.*OK.*'))
        test.log.info('***Open Channel #1 with application')
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=' + df_name, ".*CCHO: 1.*OK.*"))
        test.log.info('***Open Channel #2 with application')
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=' + df_name, ".*CCHO: 2.*OK.*"))
        test.log.info('***Open Channel #3 with application')
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=' + df_name, ".*CCHO: 3.*OK.*"))
        test.log.info('***Open Channel #4 with application')
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=' + df_name, ".*CME ERROR.*"))
        test.log.info('***Perform Generic Logical Channel Access with Channel #0,#1,#2,#3')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=1,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=2,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=3,10,"80F2000000"', ".*OK.*"))
        test.log.info('***Close Channel #2 with application')
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=2', ".*OK.*"))
        test.log.info('***Perform Generic Logical Channel Access with Channel #0,#1,#2,#3')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=1,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=2,10,"80F2000000"', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=3,10,"80F2000000"', ".*OK.*"))
        test.log.info('***Reopen Channel #2 with application')
        test.expect(test.dut.at1.send_and_verify('AT+CCHO=' + df_name, ".*CCHO: 2.*OK.*"))
        test.log.info('***Perform Generic Logical Channel Access with Channel #0,#1,#2,#3')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=1,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=2,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=3,10,"80F2000000"', ".*OK.*"))
        test.log.info('***Input PIN')
        test.expect(test.dut.dstl_enter_pin())
        test.log.info('***Perform Generic Logical Channel Access with Channel #0,#1,#2,#3')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=1,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=2,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=3,10,"80F2000000"', ".*OK.*"))
        test.log.info('***Close Channel #1,#2 and restart modle')
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=2', ".*OK.*"))
        test.dut.dstl_restart()
        test.log.info('***Perform Generic Logical Channel Access with Channel #0,#1,#2,#3')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=0,10,"80F2000000"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=1,10,"80F2000000"', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=2,10,"80F2000000"', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=3,10,"80F2000000"', ".*CME ERROR.*"))

        test.log.info('***Test end***')

    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
