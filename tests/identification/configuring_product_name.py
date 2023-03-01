#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0088115.001, TC0088115.002

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader


class Test(BaseTest):
    """
    Check if changing the name of product with the command AT^SCFG="Ident/Product" takes effect
    with the commands: ATI and AT+CGMM.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.product_name = test.get_product_name()

    def run(test):
        test.log.step("1. Read the product name with AT^SCFG? and check if it is delivery value corresponding "
                      "with module with commands:" "\nAT^SCFG?" "\nAT^SCFG=\"Ident/Product\"" "\nATI" "\nAT+CGMM")
        test.verifying_product_name("{}".format(test.product_name))

        test.log.step("2. Change the product name with different valid values (name with spaces, empty string, "
                      "1 character, 25 characters, special characters) and check if it was stored correctly with"
                      " all possible commands.")
        test.log.step("Checking name with spaces")
        test.set_product_name("example test name")
        test.verifying_product_name("example test name")

        test.log.step("Checking empty string")
        test.set_product_name("")
        test.verifying_product_name("")

        test.log.step("Checking 1 character")
        test.set_product_name("a")
        test.verifying_product_name("a")

        test.log.step("Checking 25 characters")
        test.set_product_name("aaaaabbbbbcccccdddddeeeee")
        test.verifying_product_name("aaaaabbbbbcccccdddddeeeee")

        test.log.step("Checking special characters")
        test.set_product_name("!@#%")
        test.verifying_product_name("!@#%")

        test.log.step("3. Restart module and check if the product name was stored in non-violated memory with "
                      "with all possible commands.")
        test.expect(dstl_restart(test.dut))
        test.verifying_product_name("!@#%")

        test.log.step("4. Try to change the product name with different invalid values (26 characters and more) "
                      "and check if proper error message was displayed.")
        test.log.step("Checking 26 characters")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\",\"aaaaabbbbbcccccdddddeeeeef\"",
                                                 "+CME ERROR: 21"))
        test.log.step("Checking 30 characters")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\",\"aaaaabbbbbcccccdddddeeeeefffff\"",
                                                 "+CME ERROR: invalid index"))

        test.log.step("5. Check if previously stored product name was not changed with all possible commands.")
        test.verifying_product_name("!@#%")

        test.log.step("6. Set back the original delivery product name and check if it was stored correctly with "
                      "all possible commands. ")
        test.set_product_name("{}".format(test.product_name))
        test.verifying_product_name("{}".format(test.product_name))

    def cleanup(test):
        test.set_product_name("{}".format(test.product_name))

    def set_product_name(test, parameter):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Product\",\"{}\"".format(parameter),
                                                 "(?s).*SCFG: \"Ident/Product\",\"{}\".*OK.*".format(parameter)))

    def verifying_product_name(test, parameter):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", ".*SCFG: \"Ident/Product\",\"{}\".*OK.*"
                                                 .format(parameter)))
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Product\"",
                                                 "(?s).*SCFG: \"Ident/Product\",\"{}\".*OK.*".format(parameter)))
        if parameter == "":
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*Cinterion\s*REVISION.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMM", "(?s).*AT\+CGMM\s*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*{}\s*{}\s*REVISION.*OK.*"
                                                     .format("Cinterion", parameter)))
            test.expect(test.dut.at1.send_and_verify("AT+CGMM", "(?s).*AT\+CGMM\s*{}\s*OK.*".format(parameter)))

    def get_product_name(test):
        test.expect(test.dut.at1.send_and_verify("ATI", ".*OK.*"))

        name = re.search(r".*Cinterion\s*[\n\r]([A-Z].*)[\n\r]REVISION.*", test.dut.at1.last_response)
        if name:
            test.log.info("Product name: {}".format(name.group(1)))
            return name.group(1).strip()
        else:
            test.expect(False, critical=True, msg="Product name not detected. TC will not be executed.")


if "__main__" == __name__:
    unicorn.main()
