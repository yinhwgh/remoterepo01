#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
import os


class Test(BaseTest):
    """
    This test case is used to verify that changes in the local.cfg file are applied correctly.
    Run this script after modify_local_cfg.py.
    Changes to local.cfg file made by modify_local_cfg.py are made undone at the end of run method.
    """

    def setup(test):
        pass

    def run(test):
        test.expect("bar" in test.local_foo)

        config_file = "local_local.cfg"

        # string appending the config file
        test_line = "local_foo=bar"

        # find path to config file
        current_dir = os.path.dirname(__file__)
        base_path = current_dir[:current_dir.rfind(os.path.join("unicorn", "tests")) + len("unicorn")]
        config_path = os.path.join(base_path, "config", config_file)

        # remove local_local.cfg
        os.remove(config_path)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
