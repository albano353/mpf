"""A digital output on either a light or driver platform."""
from typing import Union, Optional

from mpf.core.delays import DelayManager
from mpf.core.events import event_handler

from mpf.core.machine import MachineController
from mpf.core.platform import DriverConfig, LightConfig, LightConfigColors
from mpf.core.system_wide_device import SystemWideDevice
from mpf.platforms.interfaces.driver_platform_interface import PulseSettings, HoldSettings

MYPY = False
if MYPY:    # pragma: no cover
    from mpf.core.platform import DriverPlatform, LightsPlatform    # pylint: disable-msg=cyclic-import,unused-import
    from mpf.platforms.interfaces.driver_platform_interface import DriverPlatformInterface  # pylint: disable-msg=cyclic-import,unused-import; # noqa
    from mpf.platforms.interfaces.light_platform_interface import LightPlatformInterface    # pylint: disable-msg=cyclic-import,unused-import; # noqa


class Shaker(SystemWideDevice):

    """A digital output on either a light or driver platform."""

    config_section = 'shakers'
    collection = 'shakers'
    class_label = 'shaker'

    __slots__ = ["hw_driver", "type", "__dict__"]

    def __init__(self, machine: MachineController, name: str) -> None:
        """Initialize digital output."""
        self.hw_driver = None           # type: Optional[Union[DriverPlatformInterface, LightPlatformInterface]]
        self.platform = None            # type: Optional[Union[DriverPlatform, LightsPlatform]]
        super().__init__(machine, name)
        self.delay = DelayManager(self.machine)

    async def _initialize(self):
        await super()._initialize()
        self.platform = self.machine.get_platform_sections('stepper_controllers', self.config['platform'])
        self.platform.assert_has_feature("shakers")
        for event, config in self.config['pulse_events'].items():
            self.machine.events.add_handler(event,
                                            self.event_pulse,
                                            power=config.get('power'),
                                            duration=config['duration'])

    @event_handler(2)
    def event_pulse(self, power=None, duration=None, **kwargs):
        """Handle pulse control event."""
        del kwargs
        self.pulse(power, duration)

    def pulse(self, power=None, duration=None):
        if not power:
            power = self.config['default_power']
        if not duration:
            raise AssertionError("Shaker pulse called with no duration value")
        self.hw_driver.pulse(power, duration)

