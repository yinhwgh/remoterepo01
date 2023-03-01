#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0104294.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class sedrxs(BaseTest):
    def setup(test):
        test.dut.dstl_detect()


    def run(test):
        test.log.info("1. test: check AT^SEDRXS without PIN code")
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=?', '.*\\^SEDRXS: \\(0\\-3\\),\\(2,4,5\\),\\("0000"\\-"1111"\\),\\("0000"\\-"1111"\\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS?', '.*\\^SEDRXS: 2,\\"[01]{4}\\",\\"[01]{4}\\".*\\^SEDRXS: 4,\\"[01]{4}\\",\\"[01]{4}\\".*\\^SEDRXS: 5,\\"[01]{4}\\",\\"[01]{4}\\".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=0', '.*OK.*'))

        test.log.info("2. test: enter PIN code")
        test.expect(test.dut.dstl_register_to_network())

        test.log.info("3. test: check test command AT^SEDRXS")

        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=?', '.*\\^SEDRXS: \\(0\\-3\\),\\(2,4,5\\),\\("0000"\\-"1111"\\),\\("0000"\\-"1111"\\).*OK.*'))

        test.log.info("4. test: check read command AT^SEDRXS")
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS?', '.*\\^SEDRXS: 2,\\"[01]{4}\\",\\"[01]{4}\\".*\\^SEDRXS: 4,\\"[01]{4}\\",\\"[01]{4}\\".*\\^SEDRXS: 5,\\"[01]{4}\\",\\"[01]{4}\\".*OK.*'))

        test.log.info("5. test: check write command AT^SEDRXS with disable eDRX")
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=0', '.*OK.*'))

        test.log.info("6. test: check write command AT^SEDRXS with enable eDRX,ACT-type is GSM")
        test.expect(test.dut.dstl_register_to_gsm())
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0000"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0001"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0010"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0011"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0100"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0101"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0110"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"0111"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1000"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1001"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1011"', '.*OK.*'))

        test.log.info("7. test: check write command AT^SEDRXS with enable eDRX, ACT-type is E-UTRAN Cat.M1.")
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0000","0000"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0001","0001"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0010","0010"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0011","0011"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0100","0100"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0101","0101"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0110","0110"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"0111","0111"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1000","1000"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1001","1001"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1010","1010"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1011","1011"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1100","1100"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1101","1101"', '.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1110","1110"', '.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,4,"1111","1111"', '.*OK.*'))

        test.log.info("8. test: check write command AT^SEDRXS with enable eDRX, ACT-type is E-UTRAN Cat.NB.")
        test.expect(test.dut.dstl_register_to_nbiot())
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0000","0000"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0001","0001"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0010","0010"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0011","0011"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0100","0100"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0101","0101"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0110","0110"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"0111","0111"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1000","1000"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1001","1001"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1010","1010"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1011","1011"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1100","1100"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1101","1101"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1110","1110"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"1111","1111"', '.*OK.*'))

        test.log.info("9. test: check write command AT^SEDRXS with enable eDRX and enable the +CEDRXP unsolicited result code.,ACT-type is GSM")
        test.expect(test.dut.dstl_register_to_gsm())
        # Since Ericsson Network does not support this function under 2G network. Here will not check +CEDRXP URC
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0000"', '.*OK.*'))
 #       test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0000",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0001"', '.*OK.*'))
 #       test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0001",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0010"', '.*OK.*'))
 #       test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0010",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0011"', '.*OK.*'))
 #       test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0011",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0100"', '.*OK.*'))
 #       test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0100",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0101"', '.*OK.*'))
 #       test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0101",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0110"', '.*OK.*'))
#        test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0110",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"0111"', '.*OK.*'))
#        test.dut.at1.wait_for('.*\\+CEDRXP: 2,"0111",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"1000"', '.*OK.*'))
#        test.dut.at1.wait_for('.*\\+CEDRXP: 2,"1000",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"1001"', '.*OK.*'))
#        test.dut.at1.wait_for('.*\\+CEDRXP: 2,"1001",\\"[01]{4}\\",\\"[01]{4}\\".*')
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=2,2,"1011"', '.*OK.*'))
#        test.dut.at1.wait_for('.*\\+CEDRXP: 2,"1011",\\"[01]{4}\\",\\"[01]{4}\\".*')

        test.log.info("10. test: check write command AT^SEDRXS with enable the +CEDRXP unsolicited result code, ACT-type is E-UTRAN Cat.M1.")
        test.expect(test.dut.dstl_register_to_lte())
        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0000","0000"', '.*OK.*\\+CEDRXP: 4,"0000",\\"[01]{4}\\",\\"[01]{4}\\".*', wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0001","0001"', '.*OK.*\\+CEDRXP: 4,"0001",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0010","0010"', '.*OK.*\\+CEDRXP: 4,"0010",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0011","0011"', '.*OK.*\\+CEDRXP: 4,"0011",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0100","0100"', '.*OK.*\\+CEDRXP: 4,"0100",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0101","0101"', '.*OK.*\\+CEDRXP: 4,"0101",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0110","0110"', '.*OK.*\\+CEDRXP: 4,"0110",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"0111","0111"', '.*OK.*\\+CEDRXP: 4,"0111",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"1000","1000"', '.*OK.*\\+CEDRXP: 4,"1000",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"1001","1001"', '.*OK.*\\+CEDRXP: 4,"1001",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"1010","1010"', '.*OK.*\\+CEDRXP: 4,"1010",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"1011","1011"', '.*OK.*\\+CEDRXP: 4,"1011",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"1100","1100"', '.*OK.*\\+CEDRXP: 4,"1100",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,4,"1101","1101"', '.*OK.*\\+CEDRXP: 4,"1101",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))


        test.log.info("11. test: check write command AT^SEDRXS with enable the +CEDRXP unsolicited result code, ACT-type is E-UTRAN Cat.NB.")
        test.expect(test.dut.dstl_register_to_nbiot())
        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0000","0000"', '.*OK.*\\+CEDRXP: 5,"0000",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0001","0001"', '.*OK.*\\+CEDRXP: 5,"0001",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0010","0010"', '.*OK.*\\+CEDRXP: 5,"0010",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0011","0011"', '.*OK.*\\+CEDRXP: 5,"0011",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0100","0100"', '.*OK.*\\+CEDRXP: 5,"0100",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0101","0101"', '.*OK.*\\+CEDRXP: 5,"0101",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0110","0110"', '.*OK.*\\+CEDRXP: 5,"0110",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"0111","0111"', '.*OK.*\\+CEDRXP: 5,"0111",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1000","1000"', '.*OK.*\\+CEDRXP: 5,"1000",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1001","1001"', '.*OK.*\\+CEDRXP: 5,"1001",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1010","1010"', '.*OK.*\\+CEDRXP: 5,"1010",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1011","1011"', '.*OK.*\\+CEDRXP: 5,"1011",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1100","1100"', '.*OK.*\\+CEDRXP: 5,"1100",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1101","1101"', '.*OK.*.*\\+CEDRXP: 5,"1101",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1110","1110"', '.*OK.*\\+CEDRXP: 5,"1110",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.dut.at1.send_and_verify('AT^SEDRXS=2,5,"1111","1111"', '.*OK.*\\+CEDRXP: 5,"1111",\\"[01]{4}\\",\\"[01]{4}\\".*',wait_for='CEDRXP',timeout=90)
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP',
                                                 '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.log.info("12. test: check write command AT^SEDRXS with disable eDRX and reset the <Requested_eDRX_value> and <Requested_Paging_time_window> to default.")
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=3 ', '.*OK.*'))

        test.log.info("13. test: Invalid value should be return error")
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=4', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=5', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=@', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=~', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=#', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,3', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,6', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,+', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,~', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,@', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,#', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1100"', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1101"', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1110"', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,2,"1111"', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,"@#$%"', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SEDRXS=1,5,', '.*ERROR.*'))

        test.log.info('*** END TEST ***')

    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
