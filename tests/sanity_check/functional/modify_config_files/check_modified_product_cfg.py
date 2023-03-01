#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
import os


class Test(BaseTest):
    """
    This test case is used to verify that changes in the bobcat.cfg file are applied correctly.
    Run this script after modify_product_cfg.py.
    Changes to bobcat.cfg file made by modify_product_cfg.py are made undone at the end of run method.
    """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        test.expect("bar" in test.dut.product_foo)

        if (test.dut.project == "SERVAL"):
            config_file = "serval.cfg"
        elif (test.dut.project == "BOBCAT"):
            config_file = "bobcat.cfg"
        else:
            config_file = "cougar.cfg"

        # string appending the config file
        test_line = "product_foo=bar"

        # find path to config file
        current_dir = os.path.dirname(__file__)
        base_path = current_dir[:current_dir.rfind("unicorn\\tests") + len("unicorn")]
        config_path = base_path + '\config\\devconfig\\' + config_file

        # remove test_line from file
        # os.chdir(current_dir)
        with open(config_path, "r") as f:
            lines = f.readlines()
        with open(config_path, "w") as f:
            for line in lines:
                if line.strip("\n") != test_line:
                    f.write(line)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
