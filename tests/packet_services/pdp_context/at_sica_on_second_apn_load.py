# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0107279.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object


class Test(BaseTest):
    """	To check Module behavior during activating/deactivating second PDP context/NV
    bearer for IP services."""

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        iterations = 1000

        test.log.info("Executing script for test case: 'TC0107279.001 AtSicaOnSecondApnLoad'")
        test.log.step("1) Define PDP contexts / NV bearers on Module:"
                      "\r\n- default APN on first CGDCONT"
                      "\r\n- second APN on second CGDCONT")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.expect(connection_setup_object.dstl_define_pdp_context())

        test.connection_setup_object_2 = dstl_get_connection_setup_object(test.dut, ip_version='IPv4',
                                                                          ip_public=True)
        test.connection_setup_object_2.cgdcont_parameters['cid'] = "2"
        test.expect(test.connection_setup_object_2.dstl_define_pdp_context())

        test.log.step("2) Attach Module to network on default APN")
        test.expect(connection_setup_object.dstl_activate_internet_connection())

        for iteration in range(1, iterations + 1):
            test.log.step("3) Activate second APN using AT^SICA=1,2 command")
            test.expect(test.connection_setup_object_2.dstl_activate_internet_connection())

            test.log.step("4) Wait 10-15 seconds")
            test.sleep(15)

            test.log.step("5) Deactivate second APN using AT^SICA=0,2 command")
            test.expect(test.connection_setup_object_2.dstl_deactivate_internet_connection())

            test.log.step("6) Wait 20-25 seconds")
            test.sleep(25)

            test.log.step("7) Repeat steps 3-6 {} times" "\nAlready done {} iterations".
                          format(iterations, iteration))

    def cleanup(test):
        test.expect(test.connection_setup_object_2.dstl_deactivate_internet_connection())


if "__main__" == __name__:
    unicorn.main()
