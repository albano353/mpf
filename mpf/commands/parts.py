"""Command to generate a parts list for an MPF pinball game."""

import argparse
from ruamel.yaml import YAML

from mpf.core.machine import MachineController
from mpf.core.utility_functions import Util
from mpf.core.config_loader import YamlMultifileConfigLoader

SUBCOMMAND = False

class Command:

    """Parses an MPF project config and generates parts data."""

    def __init__(self, mpf_path, machine_path, args):
        """Run the analysis."""
        print("Initializing MPF Parts List...")

        parser = argparse.ArgumentParser(description='Generates wiring .yaml file')
        parser.add_argument("-c",
                            action="store", dest="configfile",
                            default="config.yaml", metavar='config_file',
                            help="The name of a config file to load. Default "
                                 "is "
                                 "config.yaml. Multiple files can be used "
                                 "via a comma-"
                                 "separated list (no spaces between)")

        self.args = parser.parse_args(args)
        self.args.configfile = Util.string_to_event_list(self.args.configfile)
        # Configure some values that are propagated by default in the main
        # command parser.
        self.args.__dict__["production"] = False
        self.args.__dict__["force_platform"] = "smart_virtual"
        self.args.__dict__["text_ui"] = False
        self.args.__dict__["bcp"] = False
        self.args.__dict__["platform_integration_test"] = False

        config_loader = YamlMultifileConfigLoader(machine_path, self.args.configfile,
                                                  False, False)

        config = config_loader.load_mpf_config()


        self.machine = MachineController(vars(self.args), config)
        self.machine.initialize_mpf()

        cabinet = {
            "switches": [s for s in self.machine.switches.values() if "cabinet" in s.tags],
            "coils": [c for c in self.machine.coils.values() if "cabinet" in c.tags],
            "lights": [l for l in self.machine.lights.values() if "cabinet" in l.tags]
        }

        print(f"Cabinet has {len(cabinet['switches'])} switches, {len(cabinet['coils'])} coils, and {len(cabinet['lights'])} lights.")
        print(f"Playfield has {len(self.machine.switches) - len(cabinet['switches'])} switches, {len(self.machine.coils) - len(cabinet['coils'])} coils, and {len(self.machine.lights) - len(cabinet['lights'])} lights.")
