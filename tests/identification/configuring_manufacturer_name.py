# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0088113.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader


class Test(BaseTest):
    """
    Intention: Check if changing the name of manufacturer with the command AT^SCFG="Ident/Manufacturer" takes effect
    with the commands: ATI and AT+CGMI.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.product_name = test.get_product_name()

    def run(test):
        test.log.step("1. Read the manufacturer name with AT^SCFG? and check if it is delivery value \"Cinterion\" "
                      "with commands:" "\nAT^SCFG?" "\nAT^SCFG=\"Ident/Manufacturer\"" "\nATI" "\nAT+CGMI")
        test.verifying_manufacturer_name("Cinterion")

        test.log.step("2. Change the manufacturer name with different valid values (empty string, 1 character, "
                      "25 characters, special characters) and check if it was stored correctly with all possible "
                      "commands.")
        test.log.step("Checking empty string")
        test.set_manufacturer_name("")
        test.verifying_manufacturer_name("")

        test.log.step("Checking 1 character")
        test.set_manufacturer_name("a")
        test.verifying_manufacturer_name("a")

        test.log.step("Checking 25 characters")
        test.set_manufacturer_name("aaaaabbbbbcccccdddddeeeee")
        test.verifying_manufacturer_name("aaaaabbbbbcccccdddddeeeee")

        test.log.step("Checking special characters")
        test.set_manufacturer_name("!@#%")
        test.verifying_manufacturer_name("!@#%")

        test.log.step("3. Restart module and check if the manufacturer name was stored in non-violated memory with "
                      "with all possible commands.")
        test.expect(dstl_restart(test.dut))
        test.verifying_manufacturer_name("!@#%")

        test.log.step("4. Try to change the manufacturer name with different invalid values (26 characters and more) "
                      "and check if proper error message was displayed.")
        test.log.step("Checking 26 characters")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\",\"aaaaabbbbbcccccdddddeeeeef\"",
                                                 "+CME ERROR: 21"))
        test.log.step("Checking 30 characters")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\",\"aaaaabbbbbcccccdddddeeeeefffff\"",
                                                 "+CME ERROR: invalid index"))

        test.log.step("5. Check if previously stored manufacturer name was not changed with all possible commands.")
        test.verifying_manufacturer_name("!@#%")

        test.log.step("6. Set back the original delivery manufacturer name and check if it was stored correctly with "
                      "all possible commands. ")
        test.set_manufacturer_name("Cinterion")
        test.verifying_manufacturer_name("Cinterion")

    def cleanup(test):
        test.set_manufacturer_name("Cinterion")

    def set_manufacturer_name(test, parameter):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\",\"{}\"".format(parameter),
                                                 "(?s).*SCFG: \"Ident/Manufacturer\",\"{}\".*OK.*".format(parameter)))

    def verifying_manufacturer_name(test, parameter):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*SCFG: \"Ident/Manufacturer\",\"{}\".*OK.*"
                                                 .format(parameter)))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\"",
                                                 "(?s).*SCFG: \"Ident/Manufacturer\",\"{}\".*OK.*".format(parameter)))
        if parameter == "":
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*{}\s*REVISION.*OK.*"
                                                     .format(test.product_name)))
            test.expect(test.dut.at1.send_and_verify("AT+CGMI", "(?s).*AT\+CGMI\s*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*{}\s*{}\s*REVISION.*OK.*"
                                                     .format(parameter, test.product_name)))
            test.expect(test.dut.at1.send_and_verify("AT+CGMI", "(?s).*AT\+CGMI\s*{}\s*OK.*".format(parameter)))

    def get_product_name(test):
        test.expect(test.dut.at1.send_and_verify("ATI", ".*OK.*"))

        name = re.search(r".*Cinterion\s*[\n\r](.*)[\n\r]REVISION.*", test.dut.at1.last_response)
        if name:
            test.log.info("Product name: {}".format(name.group(1)))
            return name.group(1)


if "__main__" == __name__:
    unicorn.main()
