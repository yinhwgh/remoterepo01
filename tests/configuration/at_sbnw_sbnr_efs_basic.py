# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# LM0003750 - LM0003750 - LM0003750 - LM0007733 - LM0007733
# TC0093049.001
'''
This procedure provides the possibility of basic tests for the exec commands at^sbnw and at^sbnr related to EFS Items.
The procedure works without additional tools.
The File hello_world.txt will write into the EFS.
Then this File will read by using at^sbnr.
Then a loop of 10 time the same file will be write/read/delete
Then this File will write again with an bigger Content.
module will be restart
Then this File will read again.
Then this File will be deleted.
Restart is done between write and read
'''


import unicorn
import dstl.auxiliary.devboard
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.auxiliary.restart_module import dstl_restart

testcase_id = "LM0003750 - LM0003750 - LM0003750 - LM0007733 - LM0007733"
filename_short_file = "hello_world.txt"
filename_big_file = "hello_world100.txt"
ver = "1.1"

class at_sbnw_sbnr_efs_basic(BaseTest):

    def remove_old_files(test, old_file_name):
        if (test.dut.project == 'VIPER'):
            test.log.info("Viper can't delete efs files - see IPIS100340251 - IPIS100340243 - ")
        else:
            test.log.info ("If a File >" + str(old_file_name) + "<  is available inside the Module?")
            test.log.info ("         (It schould not be.) ")
            test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" + str(old_file_name) + "\"","O")) # CME ERROR: parameters error
            # CME ERROR: 22 means: "not found"
            res = test.dut.at1.last_response
            if (not ("ERROR" in res)) and  (old_file_name in res):
                test.log.info("File >" + str(old_file_name) + "< is there, it must removed")
                test.expect(test.dut.at1.send_and_verify("at^sbnw=\"EFS\",\"" + str(old_file_name) + "\",-1", ))
                test.remove_old_files(old_file_name)
            else:
                test.log.info("File >" + str(old_file_name) + "< is NOT there - nothing to do, OK")
        return

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + '*****')
        test.log.com ('***** Ver: ' + str(ver) + ' - Start *****')
        test.log.com ("***** " + testcase_id + " *****")
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()

    def run(test):
        '''
        This procedure provides the possibility of basic tests for the exec commands at^sbnw and at^sbnr related to EFS Items.
        The procedure works without additional tools.
        The File hello_world.txt will write into the EFS.
        Then this File will read by using at^sbnr.
        Then a loop of 10 time the same file will be write/read/delete
        Then this File will write again with an bigger Content.
        module will be restart
        Then this File will read again.
        Then this File will be deleted.
        Restart is done between write and read
        '''

        test.log.step ('Step 0.1: Prepare test')
        #==============================================================
        sbnw_test_resp = ".*\\^SBNW: \\(omadm\\), \\(\\)"
        sbnr_error_code = "100"
        write_hello_world_1 = ""
        write_hello_world_100_part_1 = ""
        write_hello_world_100_part_2 = ""

        write_hello_world_100_padd = "58319237E1DCDC8C"  # This is Padding during Write

        if (test.dut.project == 'BOBCAT'):
            write_hello_world_1 = "200000005A77616849D1757A68036CF2F93DD449868E31479EDD79AF1D761B543D8D5443"
            write_hello_world_100_part_1 = "900A0000B92ABDD2848634EBF76FEAFC8AE5FDEA4B638709E85EFF3E3275AD5D89C227BDBEE35CE05C0F859CB49A3A2B2F84040F42C82CAC1E7F10DAC9F444B195E49E8EDB595A5A12301B09090D2333F076787263228D87840A765E68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4434A6701FD5AE2BA4B638709E85EFF3E3275AD5D89C227BDF7E526D1E10A616CB49A3A2B2F84040F42C82CAC1E7F10DAF8AC0284EB4CB643DB595A5A12301B09090D2333F07678721034829E1C5B8B0768036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4B264F14D309CBC804B638709E85EFF3E3275AD5D89C227BD2A43F896E1951D2FBD73748D290FF4705C1EFB07A3666F6B664175385BD8D3DB68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C44BFC7FD081315380087BFED9618FC00797B90C97B89931600EF39A0FAC1AC620DB595A5A12301B09090D2333F07678723312F8E430024FB3722C7E6088B3CD668F88183604F79A6064D5623C7B370DA4BE2A6AE53BF130ACB49A3A2B2F84040F42C82CAC1E7F10DA1D458FF5414FE529C663C9631981A1EF29FAEB7D97DD247E7082A7AECB7A8C751190945D5E1A61C74B638709E85EFF3E3275AD5D89C227BDFB1565866C52CE86BD73748D290FF4705C1EFB07A3666F6B94918CD1D95A45E168036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C45D4D1EE35ABD1D9D087BFED9618FC00797B90C97B8993160379217B0A2C1CCD8DB595A5A12301B09090D2333F0767872DC5E9D4E49B9E59B722C7E6088B3CD668F88183604F79A6064D5623C7B370DA465B941CFE951A7BBB49A3A2B2F84040F42C82CAC1E7F10DA117F262540F712B2C663C9631981A1EF29FAEB7D97DD247E74BE821BA765AFA4434A6701FD5AE2BA4B638709E85EFF3E3275AD5D89C227BD5183DB5C38CCA9E3BD73748D290FF4705C1EFB07A3666F6B39779DCDECFE7C3368036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4C73F7198BEA25377087BFED9618FC00797B90C97B8993160B8994EF523EC9C2DDB595A5A12301B09090D2333F0767872E90623FE1AC2DC2A722C7E6088B3CD668F88183604F79A6064D5623C7B370DA4CE499560288910A7B49A3A2B2F84040F42C82CAC1E7F10DAEAF2109A1A141D78C663C9631981A1EF29FAEB7D97DD247EBC6BEECC3AA16304E29D3B06F0399DAC4B638709E85EFF3E3275AD5D89C227BD9FBE9DF6C99889F2BD73748D290FF4705C1EFB07A3666F6B96DF09FDAB41B82F68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C434485BF6E61750CC087BFED9618FC00797B90C97B899316019D5711ED914A902DB595A5A12301B09090D2333F0767872E8517EC485123E7C722C7E6088B3CD668F88183604F79A6064D5623C7B370DA42A890C5AA35BD465B49A3A2B2F84040F42C82CAC1E7F10DA95694DCD9B572E61C663C9631981A1EF29FAEB7D97DD247E93B3143C222A4798F76FEAFC8AE5FDEA4B638709E85EFF3E3275AD5D89C227BD77F9BF6675E10230BD73748D290FF4705C1EFB07A3666F6BD8D690DB7A6AA19068036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C45B0E699AC283F97F087BFED9618FC00797B90C97B89931609123F55007B3E48EDB595A5A12301B09090D2333F0767872D131A129DBFA16BC722C7E6088B3CD668F88183604F79A6064D5623C7B370DA44214EA67EF94C36BB49A3A2B2F84040F42C82CAC1E7F10DAA19D9A9B4D810A14C663C9631981A1EF29FAEB7D97DD247E93B3143C222A4798B264F14D309CBC804B638709E85EFF3E3275AD5D89C227BDADB066475F622D8BBD73748D290FF4705C1EFB07A3666F6BB65146D38F01A53C68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C47FA23D7AA217DF71087BFED9618FC00797B90C97B8993160EECFBEC37C9BE2FDDB595A5A12301B09090D2333F0767872E020C60F2BE5F533722C7E6088B3CD668F88183604F79A6064D5623C7B370DA4A3491376DAE3B107B49A3A2B2F84040F42C82CAC1E7F10DA60AF2E9D1EE78032C663C9631981A1EF29FAEB7D97DD247ECC07CEFBE36D483E1190945D5E1A61C74B638709E85EFF3E3275AD5D89C227BDE2D387DF88E45762BD73748D290FF4705C1EFB07A3666F6B3F070B25CE89B8B968036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C46B9A108DDACE3C69087BFED9618FC00797B90C97B8993160F9CCB2FF22E9AD9FDB595A5A12301B09090D2333F076787237ED822016AD7E20722C7E6088B3CD668F88183604F79A6064D5623C7B370DA479DD4486653E662CB49A3A2B2F84040F42C82CAC1E7F10DA7A87C30EBA1CD153C663C9631981A1EF29FAEB7D97DD247EFE50403D3839139D434A6701FD5AE2BA4B638709E85EFF3E3275AD5D89C227BD96A2452D385E5CECBD73748D290FF4705C1EFB07A3666F6BBDA13B09AD5080C168036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4DC90E8FFC5D19D2B087BFED9618FC00797B90C97B89931607D79E556DFC9981CDB595A5A12301B09090D2333F0767872673FA7C9E2F5839A722C7E6088B3CD668F88183604F79A6064D5623C7B370DA45ACCB2E7D6E60AE1B49A3A2B2F84040F42C82CAC1E7F10DABD01B5D0EFA09B9EC663C9631981A1EF29FAEB7D97DD247E15EC24E4A28D4D4FE29D3B06F0399DAC4B638709E85EFF3E3275AD5D89C227BDCE0ABB048B7EFA64BD73748D290FF4705C1EFB07A3666F6BF0E51F6F250262FF68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4C423EDAF2204BB9D087BFED9618FC00797B90C97B8993160F467EACFA44A987CDB595A5A12301B09090D2333F0767872E406EA0100AEFF5B722C7E6088B3CD668F88183604F79A6064D5623C7B370DA463D0793DD1AB5F1FB49A3A2B2F84040F42C82CAC1E7F10DA3D41F8ED26B6C106C663C9631981A1EF29FAEB7D97DD247E4955EDDDC0EABE9EF76FEAFC8AE5FDEA4B638709E85EFF3E3275AD5D89C227BD854B3A51D7E51FACBD73748D290FF4705C1EFB07A3666F6BF7653C3BDEA8910E68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4D8169E66505D3592087BFED9618FC00797B90C97B8993160990B3607D9D9B0BFDB595A5A12301B09090D2333F0767872422EE29DD08309C4722C7E6088B3CD668F88183604F79A6064D5623C7B370DA419B2E0A9A93548ADB49A3A2B2F84040F42C82CAC1E7F10DACF41E54E1DA9B7FEC663C9631981A1EF29FAEB7D97DD247E4955EDDDC0EABE9EB264F14D309CBC804B638709E85EFF3E3275AD5D89C227BDCB6D87BF18A7F657BD73748D290FF4705C1EFB07A3666F6B1836179F0E9DA13668036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4F1E921C2860F85CB087BFED9618FC00797B90C97B89931604372FDE2169052CFDB595A5A12301B09090D2333F0767872356D6562716121FA722C7E6088B3CD668F88183604F79A6064D5623C7B370DA4DC86339852A44A76B49A3A2B2F84040F42C82CAC1E7F10DA900D8C390FCC84D8"
            write_hello_world_100_part_2 = "C663C9631981A1EF29FAEB7D97DD247E7A01F55C3AB11F441190945D5E1A61C74B638709E85EFF3E3275AD5D89C227BDDB9C4B900DDAEBAABD73748D290FF4705C1EFB07A3666F6B941A6C4369EEE15C68036CF2F93DD44993869D4B9A391ED12D1ECE5AEE81C4C4469B3AB4B081742FB49A3A2B2F84040F42C82CAC1E7F10DA"
            write_hello_world_100_padd	= "58319237E1DCDC8C" # This is Padding during Write
            # read_hello_world_100_padd_1	= "0FA9971E7C9D0658"  # This is Padding during Read #
            # read_hello_world_100_padd_1 = "9EF6951E926C60F6" # BC25337CAF07BFF2
            # read_hello_world_100_padd_2	= "9AA4B373B0411B80"  #  This is Padding during Read
            sbnw_test_resp = ".*\\^SBNW: \\(agps, is_cert\\), \\(\\)";
            if "2" in test.dut.step:
                sbnw_test_resp = ".*\\^SBNW: \\(\"agps\", \"ciphersuites\", \"is_cert\", \"omadm\", \"sound\"\\),\\(1\\)";
            if "133" in test.dut.step:
                sbnw_test_resp = ".*\\^SBNW: \\(\"agps\", \"is_cert\", \"sound\"\\),\\(\\)";
            read_hello_world_1 = write_hello_world_1

        if (test.dut.project == 'VIPER'):
            # viper have a changed mefs tool,
            write_hello_world_1 = "200000006E431E8936D28AA2E4E8437D55C6448A561E0D26BF9290DF2042DE38A97DDAC0"
            write_hello_world_100_part_1 = "900A0000ABE6D06A6E67BAF83470B2935CD020305DFBB183053EC33FB572463EAFDE812FCD3E36FCF3776960718C9E7CB1E708C9BD1B7C7081E5288236CD64582C54D76C8910898D2439134F3C1369491E421D035192A0D826DB8E20E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFF19096487230050C5DFBB183053EC33FB572463EAFDE812FBDFE2A5BA1B883DB718C9E7CB1E708C9BD1B7C7081E528821D5DD2303116AAB88910898D2439134F3C1369491E421D034E26BEDDEECF07D5E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF4687090C57C459AC5DFBB183053EC33FB572463EAFDE812FD1E7994AA36F228E7F35B771000B7FDD9AFA59774C61E9A9079248AC7E285B9EE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF508E79D9FB11DAA4F0C6E77B6C45AFB4E72C5A167E5A414C978FAAC3765D4F278910898D2439134F3C1369491E421D032C0FB51097755F042DF552D30C90D342921FAF0E0941B1154F48A307C7163685D943092F31E8509A718C9E7CB1E708C9BD1B7C7081E52882861B9EE75913485394A4F769F4B39098A48ADD61E4D02AB27706E5EA19E4E62240DD485E4ABF1DA35DFBB183053EC33FB572463EAFDE812F841594FA9C75AD387F35B771000B7FDD9AFA59774C61E9A99CA36C1C70BAADEFE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFA8B021096CE0B67CF0C6E77B6C45AFB4E72C5A167E5A414CA790408A916C91548910898D2439134F3C1369491E421D033082DE6D46B8393F2DF552D30C90D342921FAF0E0941B1154F48A307C716368522D51D7584AF4F86718C9E7CB1E708C9BD1B7C7081E5288235AAC7147F21420994A4F769F4B39098A48ADD61E4D02AB24BC6059B2E548787F19096487230050C5DFBB183053EC33FB572463EAFDE812F77341F421D58AD377F35B771000B7FDD9AFA59774C61E9A904F2C2A99B68142CE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF54708F6851DF8AEDF0C6E77B6C45AFB4E72C5A167E5A414C21C7B1FA1948967D8910898D2439134F3C1369491E421D037A69E42A4A0E5DFF2DF552D30C90D342921FAF0E0941B1154F48A307C7163685C723EBFF13B1E212718C9E7CB1E708C9BD1B7C7081E52882F8E688F0DBE9805594A4F769F4B39098A48ADD61E4D02AB20DA3E77D0B5A02C247FBC5FC3DA3FDE85DFBB183053EC33FB572463EAFDE812F36DC52915DA0EE447F35B771000B7FDD9AFA59774C61E9A987D64E42E7597436E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF772958EF321323DEF0C6E77B6C45AFB4E72C5A167E5A414CC1A556A14222F5908910898D2439134F3C1369491E421D03CA29DB431B8B63C02DF552D30C90D342921FAF0E0941B1154F48A307C7163685F8E70202D5382DF4718C9E7CB1E708C9BD1B7C7081E52882773BEBC065ED4A4994A4F769F4B39098A48ADD61E4D02AB2E987D5AD8637AAF83470B2935CD020305DFBB183053EC33FB572463EAFDE812FC82B28A2653545937F35B771000B7FDD9AFA59774C61E9A99DB87664AB3A209AE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFA0E2D84CF7C5806FF0C6E77B6C45AFB4E72C5A167E5A414CE61B8F441F5726AE8910898D2439134F3C1369491E421D03F477EB0BDD84126E2DF552D30C90D342921FAF0E0941B1154F48A307C7163685C45233DF53012039718C9E7CB1E708C9BD1B7C7081E528824DD6F850D90EADB694A4F769F4B39098A48ADD61E4D02AB2E987D5AD8637AAF84687090C57C459AC5DFBB183053EC33FB572463EAFDE812FFC0445ECD303617D7F35B771000B7FDD9AFA59774C61E9A91643AA5C0927DDE7E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFEC0763868B2B1F77F0C6E77B6C45AFB4E72C5A167E5A414CF5CA763D9BE4BF738910898D2439134F3C1369491E421D03817A7D5E524444502DF552D30C90D342921FAF0E0941B1154F48A307C716368510A1A13AE56621CA718C9E7CB1E708C9BD1B7C7081E52882D04158769923861E94A4F769F4B39098A48ADD61E4D02AB2A18D14349E4ECB9040DD485E4ABF1DA35DFBB183053EC33FB572463EAFDE812F0CEAAAB924D108EF7F35B771000B7FDD9AFA59774C61E9A9ECDC1D3B93ED9530E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFB6AB6B7C11C84D31F0C6E77B6C45AFB4E72C5A167E5A414C5FE990EA523ABEDA8910898D2439134F3C1369491E421D0358F11F765785F4692DF552D30C90D342921FAF0E0941B1154F48A307C7163685ABDE6964BBCD55B8718C9E7CB1E708C9BD1B7C7081E52882D9DEAA1A723C509B94A4F769F4B39098A48ADD61E4D02AB2AF3C8A32CDF1301FF19096487230050C5DFBB183053EC33FB572463EAFDE812FE603C269FB3BDCD27F35B771000B7FDD9AFA59774C61E9A9DFFEA4437BEAB043E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF39765CBE38989318F0C6E77B6C45AFB4E72C5A167E5A414CDFAA6B7C2D3D305A8910898D2439134F3C1369491E421D034264A41A543330182DF552D30C90D342921FAF0E0941B1154F48A307C7163685C542D5D5B2866A83718C9E7CB1E708C9BD1B7C7081E52882491AACEC8F9BF17E94A4F769F4B39098A48ADD61E4D02AB2213D0AF31C8F7B3F47FBC5FC3DA3FDE85DFBB183053EC33FB572463EAFDE812FC858B7AB4BB463CD7F35B771000B7FDD9AFA59774C61E9A933F7E2E66E78D292E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF3232D9959AECBA09F0C6E77B6C45AFB4E72C5A167E5A414C0633540B7A8EE47F8910898D2439134F3C1369491E421D031B1A9F6E9EE220092DF552D30C90D342921FAF0E0941B1154F48A307C71636850B4F41091DE6F9A4718C9E7CB1E708C9BD1B7C7081E528828298D1057D3EEA4E94A4F769F4B39098A48ADD61E4D02AB22DA4B3DA454B29533470B2935CD020305DFBB183053EC33FB572463EAFDE812FA446E29FFA5969B27F35B771000B7FDD9AFA59774C61E9A929698D093B20CB94E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFCA932578D29AAA11F0C6E77B6C45AFB4E72C5A167E5A414C0C982224FF164ABE8910898D2439134F3C1369491E421D03B4448876668D2AF02DF552D30C90D342921FAF0E0941B1154F48A307C7163685C4AC2BF7E59917A5718C9E7CB1E708C9BD1B7C7081E528825BDD0B6684D524DC94A4F769F4B39098A48ADD61E4D02AB22DA4B3DA454B29534687090C57C459AC5DFBB183053EC33FB572463EAFDE812FC95CF1291C8C17DA7F35B771000B7FDD9AFA59774C61E9A98A359F5AE6854F10E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFDACBE5FFA8FE104FF0C6E77B6C45AFB4E72C5A167E5A414CFB766412F3308D1C8910898D2439134F3C1369491E421D03FDD2F79BF8CC72E52DF552D30C90D342921FAF0E0941B1154F48A307C7163685EF2F6C5BB35B6FC0718C9E7CB1E708C9BD1B7C7081E528824C273CDD002F0FBB94A4F769F4B39098A48ADD61E4D02AB25E43C6428CEB8BB440DD485E4ABF1DA35DFBB183053EC33FB572463EAFDE812FE2478E7E5255C6837F35B771000B7FDD9AFA59774C61E9A970B3CAFF2F87728EE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFCDA3250846A712E7718C9E7CB1E708C9BD1B7C7081E52882"
            write_hello_world_100_padd	= "FDE156EF94E6CE2C" # This is Padding during Write

            # new decoding since sw100_092
            read_hello_world_1 = "4800000005AFA6FF1BFE2DFBB9219EB4B63B070B970465A34BBC0DD3DF8D8437A3D26BE1DF8D8437A3D26BE1F9403AEFF4B2AEDEA42A38A5AD7E2EC1F651B7E782FE3FB3"
            read_hello_world_100 = "B00A000005AFA6FF1BFE2DFBB9219EB4B63B070B970465A34BBC0DD3DF8D8437A3D26BE1DF8D8437A3D26BE1769F940B880D4F4E8910898D2439134F3C1369491E421D03870ACF0A923E6D3DE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF47FBC5FC3DA3FDE85DFBB183053EC33FB572463EAFDE812F7F8077E9FC672287718C9E7CB1E708C9BD1B7C7081E52882A3D39ADFDA7C1EF48910898D2439134F3C1369491E421D03CDE8D941354CE478E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF40DD485E4ABF1DA35DFBB183053EC33FB572463EAFDE812FAFCD5A8FDEB84B07718C9E7CB1E708C9BD1B7C7081E52882D91824B6DCB4E2878910898D2439134F3C1369491E421D0393CB408E43BD6B8B2DF552D30C90D342921FAF0E0941B1154F48A307C71636853CA4B434DC3E3AD0718C9E7CB1E708C9BD1B7C7081E52882DE2739F066D3B51894A4F769F4B39098A48ADD61E4D02AB27706E5EA19E4E62247FBC5FC3DA3FDE85DFBB183053EC33FB572463EAFDE812F61FF6941F8BDD5DC7F35B771000B7FDD9AFA59774C61E9A9F12A644AD72972E1E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFFFA830ACAE0F4788F0C6E77B6C45AFB4E72C5A167E5A414C6D22BE0F859DD2558910898D2439134F3C1369491E421D03439F813B904003D92DF552D30C90D342921FAF0E0941B1154F48A307C716368528DEA2223C593A93718C9E7CB1E708C9BD1B7C7081E52882BF68DCA40C3F767394A4F769F4B39098A48ADD61E4D02AB24BC6059B2E5487873470B2935CD020305DFBB183053EC33FB572463EAFDE812F57BA968131A9B1A27F35B771000B7FDD9AFA59774C61E9A9F443B6ADAA25BB2EE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFB00DD19DE0D115E0F0C6E77B6C45AFB4E72C5A167E5A414C55B99D0419D0B9248910898D2439134F3C1369491E421D03816F02BC73E84E4D2DF552D30C90D342921FAF0E0941B1154F48A307C7163685261CE3B78EA70412718C9E7CB1E708C9BD1B7C7081E528824CD76CD8E600613594A4F769F4B39098A48ADD61E4D02AB24BC6059B2E5487874687090C57C459AC5DFBB183053EC33FB572463EAFDE812F8D54781AD0AF3EDE7F35B771000B7FDD9AFA59774C61E9A9F34A635DB39B84AFE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF23AC09D19CAA383AF0C6E77B6C45AFB4E72C5A167E5A414C61467A1892632E448910898D2439134F3C1369491E421D03F1D8FCED46AB07432DF552D30C90D342921FAF0E0941B1154F48A307C7163685C723A9B62B6B44A1718C9E7CB1E708C9BD1B7C7081E5288227CAAFE4D5BE900D94A4F769F4B39098A48ADD61E4D02AB20DA3E77D0B5A02C240DD485E4ABF1DA35DFBB183053EC33FB572463EAFDE812F653DA538898A8CE37F35B771000B7FDD9AFA59774C61E9A9A255621431E6470CE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFAF8BE3307154B703F0C6E77B6C45AFB4E72C5A167E5A414CBF27C4FBB9C701BE8910898D2439134F3C1369491E421D03C549819D159694B02DF552D30C90D342921FAF0E0941B1154F48A307C71636853FA49F301F30CD10718C9E7CB1E708C9BD1B7C7081E52882288834F0D24F5BF094A4F769F4B39098A48ADD61E4D02AB2E987D5AD8637AAF8F19096487230050C5DFBB183053EC33FB572463EAFDE812FC703B874272AA0337F35B771000B7FDD9AFA59774C61E9A9E702870AEFC6251CE4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF7D3ED7ED825006D4F0C6E77B6C45AFB4E72C5A167E5A414CD6B8418CEDDE55398910898D2439134F3C1369491E421D03D8B3793FC256F6D02DF552D30C90D342921FAF0E0941B1154F48A307C716368534911D240AF24CE8718C9E7CB1E708C9BD1B7C7081E52882DB35FDD7240FD34494A4F769F4B39098A48ADD61E4D02AB2A18D14349E4ECB9047FBC5FC3DA3FDE85DFBB183053EC33FB572463EAFDE812F324AA478B8077CDA7F35B771000B7FDD9AFA59774C61E9A9B2841D9BBF6EA8D5E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF8D00394F030292B0F0C6E77B6C45AFB4E72C5A167E5A414CB0F8BEEFCBFF5D948910898D2439134F3C1369491E421D033DABB2C6B9E5D4D22DF552D30C90D342921FAF0E0941B1154F48A307C716368513966DACF1BDE28D718C9E7CB1E708C9BD1B7C7081E52882265E3F13CC1F65D494A4F769F4B39098A48ADD61E4D02AB2AF3C8A32CDF1301F3470B2935CD020305DFBB183053EC33FB572463EAFDE812F07A595FC697ED93A7F35B771000B7FDD9AFA59774C61E9A9035F5785D7EB2BC6E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFE41DDEBACE674B66F0C6E77B6C45AFB4E72C5A167E5A414C2CA0428849138BF78910898D2439134F3C1369491E421D032709D6FAF3A21C482DF552D30C90D342921FAF0E0941B1154F48A307C71636853DB4D5F78B0A786C718C9E7CB1E708C9BD1B7C7081E5288290AD76882144CB7194A4F769F4B39098A48ADD61E4D02AB2AF3C8A32CDF1301F4687090C57C459AC5DFBB183053EC33FB572463EAFDE812F6BE472836AF511647F35B771000B7FDD9AFA59774C61E9A9AF81FA37D2A25554E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF83B1895CE9785900F0C6E77B6C45AFB4E72C5A167E5A414CF686ED7E2E555EAD8910898D2439134F3C1369491E421D0391A339070B42C73A2DF552D30C90D342921FAF0E0941B1154F48A307C7163685DB6578E9D39883F4718C9E7CB1E708C9BD1B7C7081E52882596479E1276ED38E94A4F769F4B39098A48ADD61E4D02AB2213D0AF31C8F7B3F40DD485E4ABF1DA35DFBB183053EC33FB572463EAFDE812F807FBCF20828AFD37F35B771000B7FDD9AFA59774C61E9A94138138445976E90E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF990019E19397AAE8F0C6E77B6C45AFB4E72C5A167E5A414C213A77785D462E638910898D2439134F3C1369491E421D03912DC4EFC9F68D1A2DF552D30C90D342921FAF0E0941B1154F48A307C716368554DD6BCC139A829A718C9E7CB1E708C9BD1B7C7081E5288258CC7BE67DFAAB5994A4F769F4B39098A48ADD61E4D02AB22DA4B3DA454B2953F19096487230050C5DFBB183053EC33FB572463EAFDE812FB231E1B3882D9BFD7F35B771000B7FDD9AFA59774C61E9A953439F4C6A19F7B6E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AF65323347C6AE61C7F0C6E77B6C45AFB4E72C5A167E5A414C3DBFA597A133B8BA8910898D2439134F3C1369491E421D035B9B2A79714703B22DF552D30C90D342921FAF0E0941B1154F48A307C716368502E64A32FC70FB15718C9E7CB1E708C9BD1B7C7081E5288222523516A6AB9D2E94A4F769F4B39098A48ADD61E4D02AB25E43C6428CEB8BB447FBC5FC3DA3FDE85DFBB183053EC33FB572463EAFDE812FFEED9F87A7D52ECF7F35B771000B7FDD9AFA59774C61E9A920E862A743A3A736E4E8437D55C6448A7F40B130F2E35C3B1F511AA9201C89AFCB8D8BA63B7207D6F0C6E77B6C45AFB4E72C5A167E5A414CDA8747D2A1FE36A28910898D2439134F3C1369491E421D035F76CDD731F287922DF552D30C90D342921FAF0E0941B1154F48A307C71636855C9E7582BE1409CF718C9E7CB1E708C9BD1B7C7081E52882A5A30342DBAC6889E4E8437D55C6448A7F40B130F2E35C3B"
            write_hello_world_100_part_2 = ""
            # list only the official parameter, the internal are not listet
            sbnw_test_resp = ".*\\^SBNW: \\(\"agps\",\"ciphersuites\",\"is_cert\",\"management_cert\"\\),\\(1\\)"

        write_hello_world_100			= write_hello_world_100_part_1 + write_hello_world_100_part_2 + write_hello_world_100_padd
        #  The next Strings are Response-Strings
        if (test.dut.project == 'VIPER'):
            read_hello_world_100 = "^SBNR:" + read_hello_world_100
        else:
            read_hello_world_100 = "^SBNR:" + write_hello_world_100_part_1 + write_hello_world_100_part_2

        test.log.step ('Step 1.0: check commando functions')
        #==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cmee=1"))
        test.expect(test.dut.at1.send_and_verify("at^sbnw=?", sbnw_test_resp ))

        test.expect(test.dut.at1.send_and_verify("at^sbnw?", "CME ERROR: 100")) # CME ERROR: unknown
        test.expect(test.dut.at1.send_and_verify("at^sbnw", "CME ERROR: 100")) # CME ERROR: unknown

        test.expect(test.dut.at1.send_and_verify("at^sbnr=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at^sbnr?", "OK"))

        if((test.dut.project == 'BOBCAT') or (test.dut.project == 'VIPER') ):
            test.expect(test.dut.at1.send_and_verify("at^sbnr?", "OK"))  # ok
        else:
            test.expect(test.dut.at1.send_and_verify("at^sbnr?", "CME ERROR: " + str(sbnr_error_code)))  # ok

        test.remove_old_files(filename_short_file)
        test.remove_old_files(filename_big_file)
        test.sleep(5)

        test.log.step ('Step 2.0: Write the short file >' + str(filename_short_file) +
                       '< with the content:\nHello World\nHallo Welt')
        #==============================================================

        test.expect(test.dut.at1.send_and_verify("at^sbnw=\"EFS\",\"" + str(filename_short_file) + "\",2",
                                expect="CONNECT.*EFS READY: SEND FILE", wait_for="CONNECT.*EFS READY: SEND FILE", timeout=60))
        test.expect(test.dut.at1.send_and_verify(str(write_hello_world_1), expect="EFS: END OK", wait_for="EFS: END OK", timeout=60))
        test.sleep(10)

        test.log.step ('Step 3.0: Read and compare the short file >' + str(filename_short_file) +
                       '< with the expected content:\nHello World\nHallo Welt')
        #==============================================================

        test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" + str(filename_short_file) +
                                                 "\"","SBNR:"+ str(read_hello_world_1) +".*OK"))

        test.log.step('Step 4.0: attempt to rewrite the files 10 times the short file >' + str(
            filename_short_file) + '< with the espected content:\nHello World\nHallo Welt')
        # ==============================================================

        for i in range(1, 11):
            test.log.info ("Loop: " + str(i))
            test.log.info ("===========================")
            test.expect(test.dut.at1.send_and_verify("at^sbnw=\"EFS\",\"" + str(filename_short_file) +
                                                     "\",2", expect="CONNECT.*EFS READY: SEND FILE", wait_for="CONNECT.*EFS READY: SEND FILE", timeout=60))
            test.expect(test.dut.at1.send_and_verify(str(write_hello_world_1),expect="EFS: END OK", wait_for="EFS: END OK", timeout=60))
            test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" +
                                                     str(filename_short_file) +  "\"","SBNR:" + str(read_hello_world_1) + ".*OK"))
            test.sleep(1)
            test.remove_old_files(filename_short_file)
            test.sleep(1)

        test.expect(test.dut.at1.send_and_verify("at^sbnw=\"EFS\",\"" + str(filename_short_file) +
                                                 "\",2", expect="CONNECT.*EFS READY: SEND FILE", wait_for="CONNECT.*EFS READY: SEND FILE" , timeout=60))
        test.expect(test.dut.at1.send_and_verify(str(write_hello_world_1),expect="EFS: END OK", wait_for="EFS: END OK", timeout=60))
        test.sleep(5)

        test.log.step ('Step 5.0: Restart the file and read the test file again')
        #==============================================================
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" + str(filename_short_file) + "\"",
                                                 str(read_hello_world_1) + ".*OK"))

        test.log.step ('Step 6.0: Write the big file >' + str(filename_big_file) +
                       '< with the content:\nHello World\nHallo Welt (50 times)')
        #==============================================================
        test.expect(test.dut.at1.send_and_verify("at^sbnw=\"EFS\",\"" + str(filename_big_file) +
                                                 "\",2", expect="CONNECT.*EFS READY: SEND FILE", wait_for="CONNECT.*EFS READY: SEND FILE", timeout=120))
        test.expect(test.dut.at1.send_and_verify(str(write_hello_world_100),expect="EFS: END OK", wait_for="EFS: END OK", timeout=120))

        test.log.step ('Step 7.0: Read the big file >' + str(filename_big_file) +
                       '< with the expected content:\nHello World\nHallo Welt (50 times)')
        #==============================================================

        test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" + str(filename_big_file) + "\"",
                                                  str(read_hello_world_100) ))

        test.log.step ('Step 8.0: Restart the file and read the test file again')
        #==============================================================
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" + str(filename_big_file) + "\"",
                                                  str(read_hello_world_100) ))

        test.log.step ('Step 9.0: Rewrite the same big File again')
        #==============================================================
        test.expect(test.dut.at1.send_and_verify("at^sbnw=\"EFS\",\"" + str(filename_big_file) +
                                                 "\",2", expect="CONNECT.*EFS READY: SEND FILE", wait_for="CONNECT.*EFS READY: SEND FILE", timeout=120))
        test.expect(test.dut.at1.send_and_verify(str(write_hello_world_100),expect="EFS: END OK", wait_for="EFS: END OK", timeout=120))
        test.sleep(1)

        test.log.step ('Step 10.0: Read the big file >' + str(filename_big_file) +
                       '< with the expected content:\nHello World\nHallo Welt (50 times)')
        #==============================================================
        test.expect(test.dut.at1.send_and_verify("at^sbnr=\"EFS\",\"" + str(filename_big_file) + "\"",
                                                  str(read_hello_world_100) ))

        test.log.step ('Step x.0: End')
        #==============================================================

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.remove_old_files(filename_short_file)
        test.remove_old_files(filename_big_file)

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()