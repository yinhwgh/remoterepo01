# responsible: mariusz.znaczko@globallogic.com
# location: Wroclaw
# TC0094205.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_ringline_filter import dstl_scfg_set_urc_ringline_filter
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    Check if is possible to set all parameters of AT^SCFG="URC/Ringline/SelWUrc" command according
    to documentation.

    1. Send AT^SCFG="URC/Ringline/SelWUrc","all" and check is it set to "all"
    2. Send AT^SCFG="URC/Ringline/SelWUrc","+CMT" and check is it set to "+CMT"
    3. Send AT^SCFG="URC/Ringline/SelWUrc","RING" and check is it set to "RING"
    4. Send AT^SCFG="URC/Ringline/SelWUrc","RING","+CMT" and check is it set to "RING" and "+CMT"
    5. Send AT^SCFG="URC/Ringline/SelWUrc","+CMT","RING" and check is it set to "+CMT" and "RING"
    6. Repeat all above steps using in random places small and big signs. eg. ALL, +CMT, ring.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.step('1. Send AT^SCFG="URC/Ringline/SelWUrc","all" and check is it set to "all".')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='all', exp_resp='.*OK.*', ))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","all".*'))

        test.log.step('2. Send AT^SCFG="URC/Ringline/SelWUrc",'
                      '"+CMT" and check is it set to "+CMT".')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='+CMT', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","\+CMT".*'))

        test.log.step('3. Send AT^SCFG="URC/Ringline/SelWUrc",'
                      '"RING" and check is it set to "RING".')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='RING', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING".*'))

        test.log.step('4. Send AT^SCFG="URC / Ringline / SelWUrc","RING",'
                      '"+CMT" and check is it set to "RING" and "+CMT".')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        param1='RING', param2='+CMT', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING","\+CMT".*'))

        test.log.step('5. Send AT^SCFG="URC / Ringline / SelWUrc","+CMT",'
                      '"RING" and check is it set to "+CMT" and "RING".')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        param1='+CMT', param2='RING', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING","\+CMT".*'))

        test.log.step('6.  Repeat all above steps using in random places'
                      ' small and big signs. eg. ALL, +CMT, ring.')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='ALL', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","all".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='aLL', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","all".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='Ring', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='RiNg', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='rING', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='+cMT', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","\+CMT".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1='+Cmt', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","\+CMT".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        param1='RiNg', param2='+Cmt', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING","\+CMT".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        param1='rinG', param2='+CmT', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING","\+CMT".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        param1='+CmT', param2='RiNg', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING","\+CMT".*'))

        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        param1='+CMT', param2='riNG', exp_resp='.*OK.*'))
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                        exp_resp='.*SCFG: "URC/Ringline/SelWUrc","RING","\+CMT".*'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
