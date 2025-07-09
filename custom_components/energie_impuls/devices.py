from .const import DOMAIN,CONF_WB_DEVICE_NAME, CONF_WB_DEVICE_ID

class EnergieImpulsWallboxDevice():
    def __init__(self, hass):
        self.hass=hass

    @property
    def info(self):
         return {
            "identifiers": {(DOMAIN, f"wallbox_{hass.data[DOMAIN][CONF_WB_DEVICE_ID]}")},
            "name": "Energie Impuls Wallbox",
            "manufacturer": "ABB",
            "model": self.hass.data[DOMAIN][CONF_WB_DEVICE_NAME ],
            "configuration_url": "https://energie-impuls.site",
        }




class EnergieImpulsWallboxDevice():
    def __init__(self, hass):
        self.hass=hass

    @property
    def device_info(self):
         return {
            "identifiers": {(DOMAIN, f"wallbox_{self.hass.data[DOMAIN][CONF_WB_DEVICE_ID]}")},
            "name": "Energie Impuls Wallbox",
            "manufacturer": "ABB",
            "model": self.hass.data[DOMAIN]["wb_device_name"],
            "configuration_url": "https://energie-impuls.site",
        }
