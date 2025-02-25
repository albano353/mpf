"""ZeDMD.

Use libZeDMD
"""
import ctypes
import pathlib

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
        """Initialize ZeDMD."""
        super().__init__(machine)

        self.device = None        
        self.config = None

    async def initialize(self):
        """Initialize platform."""
        self.config = self.machine.config_validator.validate_config(
            config_spec='zedmd',
            source=self.machine.config.get('zedmd', {})
        )

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

    def __init__(self, config):
        """Initialize ZeDmd device."""
        self.config = config
        self.matrix = ZeDMD_ext()

    def update(self, data):
        """Update DMD data."""
        image = Image.frombytes('RGB', (128,32), data)
        self.matrix.RenderRgb888(image)

    def set_brightness(self, brightness: float):
        """Set brightness.
        Range is [0.0 ... 1.0].
        """
        if brightness < 0.0 or brightness > 1.0:
            raise AssertionError("Brightness has to be between 0 and 1.")
        self.matrix.SetBrightness(round(brightness * 15))

    def stop(self):
        """Stop device."""
        self.matrix.Close()
