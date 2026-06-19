import os
from datetime import datetime, timezone

from astral import LocationInfo
from astral.sun import sun

_DEFAULT_LAT = 50.1109  # Frankfurt am Main
_DEFAULT_LON = 8.6821


def _dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() == "true"


class SunlightSensor:
    def is_daytime(self) -> bool:
        """True, wenn die aktuelle UTC-Zeit zwischen Sonnenaufgang und -untergang liegt."""
        if _dev_mode():
            return True

        lat = float(os.getenv("LATITUDE", str(_DEFAULT_LAT)))
        lon = float(os.getenv("LONGITUDE", str(_DEFAULT_LON)))
        location = LocationInfo(latitude=lat, longitude=lon)
        s = sun(location.observer, date=datetime.now(tz=timezone.utc).date())
        now = datetime.now(tz=timezone.utc)
        return s["sunrise"] < now < s["sunset"]
