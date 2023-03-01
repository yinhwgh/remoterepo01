#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest


class TpTLSServerCertPreloading (BaseTest):
    def setup(test):
        pass

    def run(test):
        server_cert_list = ['Amazon Root CA 1', 'Amazon Root CA 2', 'Amazon Root CA 3', 'Amazon Root CA 4', 'D-TRUST Root Class 3 CA 2 2009', 'Baltimore CyberTrust Root',
                            'DigiCert', 'GlobalSign', 'GTS Root R1', 'GTS Root R2', 'GTS Root R3', 'GTS Root R4', 'ISRG Root X1', 'stepnexus']
        test.log.info("To check preloading server certificate.")
        test.dut.at1.send_and_verify("at^sbnr=\"preconfig_cert\"")
        for item in server_cert_list:
            if item in test.dut.at1.last_response:
                test.expect(True)
#                test.log.info("The server certificate", item, "has preloaded.")
            else:
                test.expect(False)
  #              test.log.info("The server certificate", item, "has not preload.")

    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
