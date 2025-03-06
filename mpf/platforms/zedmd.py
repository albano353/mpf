"""ZeDMD.

Use PPUC
https://github.com/PPUC

Use libZeDMD Python extension
https://github.com/PPUC/libzedmd-python-pybind11-extension

"""
import logging

import ctypes
import pathlib

try:
    import numpy
except ImportError as e:
    IMPORT_FAILED = e
else:
    IMPORT_FAILED = None    # type: ignore


# Load ZeDMD library using ctypes
libzedmd = ctypes.CDLL(str(pathlib.Path(__file__).parent.resolve()) + '/zedmd_ext/libzedmd.so')


from mpf.platforms.zedmd_ext.extending import ZeDMD_ext

from PIL import Image

from mpf.core.platform import RgbDmdPlatform
from mpf.platforms.interfaces.dmd_platform import DmdPlatformInterface


class ZeDmdPlatform(RgbDmdPlatform):

    """ZeDMD."""

    __slots__ = ["device", "config"]

    def __init__(self, machine):
        if IMPORT_FAILED:
            raise AssertionError('Failed to load numpy. Did you install numpy ? '
                                 'Try: "pip3 install numpy".') from IMPORT_FAILED

        """Initialize ZeDMD."""
        super().__init__(machine)

        self.device = None
        self.config = None

        self.config = self.machine.config_validator.validate_config(
            config_spec='zedmd',
            source=self.machine.config.get('zedmd', {})
        )

        self._configure_device_logging_and_debug('ZeDMD',self.config)


    async def initialize(self):
        """Initialize platform."""


    def stop(self):
        """Stop platform."""
        if self.device:
            self.device.stop()

    def __repr__(self):
        """Return string representation."""
        return '<Platform.ZeDmd>'

    def configure_rgb_dmd(self, name: str):
        """Configure rgb dmd."""
        if not self.device:
            self.device = ZeDmdDevice(self.config)
        return self.device



# noinspection PyCallingNonCallable
class ZeDmdDevice(DmdPlatformInterface):

    """A ZeDmd device."""

    __slots__ = ["config","log","matrix"]

    def __init__(self, config):
        """Initialize ZeDmd device."""
        self.config = config
        self.matrix = ZeDMD_ext()
        self.log = logging.getLogger('ZeDMDDevice')

    def update(self, data):
        """Update DMD data."""
        image = Image.frombytes('RGB', (self.config["width"],self.config["height"]), data)
        self.matrix.RenderRgb888(image)

    def set_brightness(self, brightness):
        """Set brightness.
        Range is [0.0 ... 1.0].
        """
        if brightness < 0.0 or brightness > 1.0:
            raise AssertionError("Brightness has to be between 0 and 1.")
        new_brightness = round(brightness * 15)
        self.log.info("Set brightness = {0:d}".format(new_brightness))
        self.matrix.SetBrightness(new_brightness)

        # If you prefer memorize brightness:
        #if new_brightness != self.matrix.GetBrightness():
        #  self.log.info("Set brightness = {0:d}".format(new_brightness))
        #  self.matrix.SetBrightness(new_brightness)
        #  self.matrix.SaveSettings()

    def stop(self):
        """Stop device."""
        self.matrix.Close()
