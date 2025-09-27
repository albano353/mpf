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
    from mpf.core.platform import ShakerPlatform    # pylint: disable-msg=cyclic-import,unused-import
    from mpf.platforms.interfaces.shaker_platform_interface import ShakerPlatformInterface  # pylint: disable-msg=cyclic-import,unused-import

class Shaker(SystemWideDevice):

    """A digital output on either a light or driver platform."""

    config_section = 'shakers'
    collection = 'shakers'
    class_label = 'shaker'

    __slots__ = ["hw_shaker", "type", "__dict__"]

    def __init__(self, machine: MachineController, name: str) -> None:
        """Initialize digital output."""
        self.hw_shaker = None           # type: Optional[ShakerPlatformInterface]
        self.platform = None            # type: Optional[ShakerPlatform]
        super().__init__(machine, name)
        self.delay = DelayManager(self.machine)

    async def _initialize(self):
        await super()._initialize()
        self.platform = self.machine.get_platform_sections('shaker_controllers', self.config['platform'])
        self.platform.assert_has_feature("shakers")
        self.hw_shaker = await self.platform.configure_shaker(self.config['number'], self.config['platform_settings'])
        for event, config in self.config['control_events'].items():
            if config.get('action') == 'stop':
                self.machine.events.add_handler(event, self.event_stop)
                continue
            self.machine.events.add_handler(event,
                                            self.event_pulse,
                                            power=config.get('power'),
                                            duration=config['duration'].evaluate({}))

    @event_handler(1)
    def event_pulse(self, duration=None, power=None, **kwargs):
        del kwargs
        self.pulse(duration, power)

    def pulse(self, duration=None, power=None):
        if power is None:
            power = self.config['default_power']
        if not duration:
            raise AssertionError("Shaker pulse called with no duration value")
        self.hw_shaker.pulse(duration, power)

    @event_handler(2)
    def event_stop(self, **kwargs):
        del kwargs
        self.stop()

    def stop(self):
        self.hw_shaker.stop()
