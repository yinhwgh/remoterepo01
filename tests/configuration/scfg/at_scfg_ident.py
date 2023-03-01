# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0088264.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader


class Test(BaseTest):
    """
    Check the configuration of SCFG=Ident/Manufacturer and Ident/Product.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.product_name = test.get_product_name()



    def run(test):
        test.log.step("Check AT^SCFG=Ident/Manufacturer and =Ident/Product with various String parameters (length, "
                      "illegal characters, character sets) "
                      "Check functionality by setting new identifier strings and "
                      "check for those strings for ATI, AT+CGMI/AT+GMI and AT+CGMM/AT+GMM.")

        test.log.step("Read the manufacturer name and product name with AT^SCFG? and check if it is delivery "
                      "value corresponding with module with commands:" "\nATI" "\nAT+CGMI" "\nAT+GMI" "\nAT+CGMM" 
                      "\nAT+GMM")
        test.verifying_manufacturer_name("Cinterion")
        test.verifying_product_name("{}".format(test.product_name))

        test.log.step("Test the manufacturer name")
        test.log.step("Change the manufacturer name with various String parameters (length, illegal characters, "
                      "character sets ")

        test.log.step("Checking name with spaces")

        test.set_manufacturer_name("example test name")
        test.verifying_manufacturer_name("example test name")

        test.log.step("Checking empty string - manufacturer only")
        if test.dut.project == 'SERVAL' or test.dut.project == 'VIPER':
            test.log.step(" empty string for Serval/Viper not allowed")
            test.set_manufacturer_name("", "CME ERROR: (21|invalid index)")
            test.verifying_manufacturer_name("example test name")
        else:
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

        test.log.step("Checking 26 characters")
        test.log.step("Checking 26 characters")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Manufacturer\",\"aaaaabbbbbcccccdddddeeeeef\"",
                                                 ".*ERROR.*"))

        test.log.step("Set back the original delivery manufacturer name and check if it was stored correctly with all "
                      "possible commands. ")
        test.set_manufacturer_name("Cinterion")
        test.verifying_manufacturer_name("Cinterion")

        test.log.step("Test the product name")
        test.log.step("Change the product name with various String parameters (length, illegal characters, "
                      "character sets ")

        test.log.step("Checking name with spaces")
        test.set_product_name("example test name")
        test.verifying_product_name("example test name")

        test.log.step("Checking empty string - product name")
        if test.dut.project == 'SERVAL' or test.dut.project == 'VIPER':
            test.log.step(" empty string for Serval/Viper not allowed")
            test.set_product_name("", "CME ERROR: (21|invalid index)")
            test.verifying_product_name("example test name")
        else:
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

        test.log.step("Checking 26 characters")
        test.log.step("Checking 26 characters")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Product\",\"aaaaabbbbbcccccdddddeeeeef\"",
                                                 ".*ERROR.*"))

        test.log.step("Set back the original product name and check if it was stored correctly with all possible "
                      "commands. ")
        test.set_product_name("{}".format(test.product_name))
        test.verifying_product_name("{}".format(test.product_name))


    def cleanup(test):
        test.set_manufacturer_name("Cinterion")
        test.set_product_name("{}".format(test.product_name))

    def set_manufacturer_name(test, parameter, exp_response=""):
        if exp_response is "":
            test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"Ident/Manufacturer\",\"{}\"'.format(parameter),
                                                     '(?s).*SCFG: \"Ident/Manufacturer\",\"{}\".*OK.*'.format(parameter)))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"Ident/Manufacturer\",\"{}\"'.format(parameter),
                                                     '.*{}.*'.format(parameter, exp_response)))

    def verifying_manufacturer_name(test, parameter):
        if parameter == "":
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*{}\s*REVISION.*OK.*"
                                                     .format(test.product_name)))
            test.expect(test.dut.at1.send_and_verify("AT+CGMI", "(?s).*AT\+CGMI\s*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+GMI", "(?s).*AT\+GMI\s*OK.*"))

        else:
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*{}\s*{}\s*REVISION.*OK.*"
                                                     .format(parameter, test.product_name)))
            test.expect(test.dut.at1.send_and_verify("AT+CGMI", "(?s).*AT\+CGMI\s*{}\s*OK.*".format(parameter)))
            test.expect(test.dut.at1.send_and_verify("AT+GMI", "(?s).*AT\+GMI\s*{}\s*OK.*".format(parameter)))

    def set_product_name(test, parameter, exp_response=""):
        if exp_response is "":
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Ident/Product\",\"{}\"".format(parameter),
                                                     "(?s).*SCFG: \"Ident/Product\",\"{}\".*OK.*".format(parameter)))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"Ident/Product\",\"{}\"'.format(parameter),
                                                     '.*{}.*'.format(parameter, exp_response)))

    def verifying_product_name(test, parameter):
        if parameter == "":
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*Cinterion\s*REVISION.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGMM", "(?s).*AT\+CGMM\s*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+GMM", "(?s).*AT\+GMM\s*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("ATI", "(?s).*ATI\s*{}\s*{}\s*REVISION.*OK.*"
                                                     .format("Cinterion", parameter)))
            test.expect(test.dut.at1.send_and_verify("AT+CGMM", "(?s).*AT\+CGMM\s*{}\s*OK.*".format(parameter)))
            test.expect(test.dut.at1.send_and_verify("AT+GMM", "(?s).*AT\+GMM\s*{}\s*OK.*".format(parameter)))

    def get_product_name(test):
        test.expect(test.dut.at1.send_and_verify("ATI", ".*OK.*"))

        name = re.search(r".*Cinterion\s*[\r\n](.*)[\r\n]REVISION.*", test.dut.at1.last_response)
        if name:
            test.log.info("Product name: {}".format(name.group(1)))
            return name.group(1).strip()


if "__main__" == __name__:
    unicorn.main()
