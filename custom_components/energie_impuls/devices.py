from .const import DOMAIN,CONF_WB_DEVICE_NAME, CONF_WB_DEVICE_ID

class EnergieImpulsWallboxDevice():
    def __init__(self, hass):
        self.hass=hass

    @property
    def device_info(self):
         return {
            "identifiers": {(DOMAIN, f"wallbox_{self.hass.data[DOMAIN][CONF_WB_DEVICE_ID]}")},
            "name": "Energie Impuls Wallbox",
            "manufacturer": "Planville",
            "model": self.hass.data[DOMAIN][CONF_WB_DEVICE_NAME],
            "configuration_url": "https://energie-impuls.site",
        }




class EnergieImpulsDevice():
    def __init__(self, hass):
        self.hass=hass

    @property
    def device_info(self):
         return {
            "identifiers": {(DOMAIN,"Myid")},
            "name": "Energie Impuls",
            "manufacturer": "Planville",
            "model": "Energie Impuls",
            "configuration_url": "https://energie-impuls.site",
        }
