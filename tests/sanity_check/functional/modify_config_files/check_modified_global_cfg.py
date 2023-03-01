#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
import os


class Test(BaseTest):
    """
    This test case is used to verify that changes in the global.cfg file are applied correctly.
    Run this script after modify_global_cfg.py.
    Changes to global.cfg file made by modify_global_cfg.py are made undone at the end of run method.
    """

    def setup(test):
        pass

    def run(test):
        test.expect("bar" in test.global_foo)

        config_file = "global_global.cfg"

        # string appending the config file
        test_line = "global_foo=bar"

        # find path to config file
        current_dir = os.path.dirname(__file__)
        base_path = current_dir[:current_dir.rfind(os.path.join("unicorn", "tests")) + len("unicorn")]
        config_path = os.path.join(base_path, "config", config_file)

        # remove global_global.cfg
        os.remove(config_path)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
