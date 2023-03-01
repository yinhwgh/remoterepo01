#responsible maciej.gorny@globallogic.com
#location Wroclaw
#corresponding Test Case TC 0102410.001
import unicorn
import re
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """
        Short description: 	To check if the user defined list of available cipher suites can be correctly set.
        Check if created and default list of supported cipher suites are properly displayed.

        Detailed description:
        1. Reset and display current list of user defined cipher suites.
        2. Display supported cipher suites
        3. Select and copy a few of supported cipher suites from the list. Make sure they are in  correct format
        and OpenSSL notation (i.e. RC4-SHA:RC4-MD5:DES-CBC3- SHA:AES128-SHA:AES256-SHA:NULL-SHA).
        Count a number of characters of cipher  suite names (<length>), including colons (59 for the given example).
        4. Set the user defined list of available cipher suites, delimited by ’:’
         Wait until URC 'CIPHER SUITES: SEND FILE ... ' appears, then paste the list of cipher  suites.
        5. Display current set (user defined list) of cipher suites
        6. Try to set the user defined list of available cipher suites (the same as in step 3) but with
        incorrect <length> parameter (length shorter than actual value)
        7. Display current set (user defined list) of cipher suites
        8. Reset and display current list of user defined cipher suites.
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):
        command_for_reset_or_add_ciphers = "at^sbnw=\"ciphersuites\","
        display_cipher_suites = "at^sbnr=\"ciphersuites\","
        expected_response_OK = ".*OK.*"
        expected_response_empty_ciphers = ".*No Cipher Suites file found or loaded.*"
        expected_response_after_cipher_clearing = ".*OK.*|.*ERROR.*"

        test.log.step("1). Reset and display current list of user defined cipher suites.")
        test.expect(test.dut.at1.send_and_verify("{}0".format(command_for_reset_or_add_ciphers),
                                                 expected_response_after_cipher_clearing))
        test.expect(test.dut.at1.send_and_verify("{}current".format(display_cipher_suites),
                                                 expected_response_empty_ciphers))

        test.log.step("2). Display supported cipher suites")
        test.expect(test.dut.at1.send_and_verify("{}default".format(display_cipher_suites), expected_response_OK))

        try:
            splitted_cipher_suites = re.search(r".*:.*", test.dut.at1.last_response).group(0).split(':')
            selected_cipher_suites_to_enter = "{}:{}:{}:{}".format(splitted_cipher_suites[3], splitted_cipher_suites[4],
                                                                   splitted_cipher_suites[5], splitted_cipher_suites[6])
        except IndexError:
            test.expect(False, critical=True, msg="Exception happened during checking default ciphersuites.")

        test.log.step("3). Select and copy a few of supported cipher suites from the list.")
        test.log.info("List of selected cipher suites: {}".format(selected_cipher_suites_to_enter))

        test.log.step("4). Set the user defined list of available cipher suites, delimited by ’:’")
        test.expect(test.dut.at1.send_and_verify('{}{}'.
                    format(command_for_reset_or_add_ciphers, len(selected_cipher_suites_to_enter)), ".*CIPHERSUITES.*"))
        test.dut.at1.send(selected_cipher_suites_to_enter, end="")
        test.expect(test.dut.at1.wait_for(expected_response_OK))

        test.log.step("5). Display current set (user defined list) of cipher suites")
        test.expect(test.dut.at1.send_and_verify("{}current".format(display_cipher_suites),
                                                 ".*{}\r\n".format(selected_cipher_suites_to_enter)))

        test.log.step("6). Try to set the user defined list of available cipher suites (the same as in step 3) "
                      "but with incorrect <length> parameter (length shorter than actual values")
        test.expect(test.dut.at1.send_and_verify('{}{}'.format(
            command_for_reset_or_add_ciphers, len(selected_cipher_suites_to_enter)), ".*CIPHERSUITES.*"))
        test.dut.at1.send("{}:AES128-SHA256".format(selected_cipher_suites_to_enter), end="")
        test.expect(test.dut.at1.wait_for(".*LENGTH ERROR.*"))

        test.log.step("7). Display current set (user defined list) of cipher suites")
        test.expect(test.dut.at1.send_and_verify("{}current".format(display_cipher_suites),
                                                 ".*{}\r\n".format(selected_cipher_suites_to_enter)))

        test.log.step("8). Reset and display current list of user defined cipher suites.")
        test.expect(test.dut.at1.send_and_verify("{}0".format(command_for_reset_or_add_ciphers), expected_response_OK))
        test.expect(test.dut.at1.send_and_verify("{}current".format(display_cipher_suites), expected_response_empty_ciphers))

    def cleanup(test):
        test.log.h2("Clearing list of cipher suites:")
        test.dut.at1.send("at^sbnw=\"ciphersuites\",0")
        test.dut.at1.wait_for(".*OK.*|.*No Cipher Suites file found or loaded.*")

if "__main__" == __name__:
    unicorn.main()
