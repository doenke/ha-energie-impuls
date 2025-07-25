
DOMAIN = "energie_impuls"
LOGIN_URL = "https://energie-impuls.site/api/auth/login"
DATA_URL = "https://energie-impuls.site/api/c/devices/flow/"
WALLBOX_URL = "https://energie-impuls.site/api/c/devices/wallbox/?nested=true"
WALLBOX_SETPOINT_URL = "https://energie-impuls.site/api/c/devices/wallbox/setpoint/"
USER_ID = "user_id"
CONF_WB_DEVICE_ID = "wb_device_id"
CONF_WB_DEVICE_NAME = "wb_device_name"
CONF_MODE_ENTITY = "mode_entity"
CONF_AUTO_SWITCH_ENTITY = "auto_switch_entity"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_AUTO_MIN_PV = "auto_min_pv"
CONF_AUTO_MINUTES = "auto_minutes"
DEFAULT_AUTO_MIN_PV = 1.5
DEFAULT_AUTO_MINUTES = 10

CONF_SESSION = "session"

SOFORTLADEN = "Sofortladen"
SOFORTLADEN_JSON = {
                "locked": False,
                "surplus_charging": False
                }
UEBERSCHUSS = "reines Überschussladen"
UEBERSCHUSS_JSON = {
                "locked": False,
                "surplus_charging": True,
                "hybrid_charging_current": None
                }
HYBRID = "Hybridladen"
HYBRID_JSON =  {
                "locked": False,
                "surplus_charging": True,
                "hybrid_charging_current": 6
                }
NICHTLADEN = "nicht laden"
NICHTLADEN_JSON =  {
            "locked": True
            }
ERROR = "Fehler"

PAYLOADS = {
            HYBRID: HYBRID_JSON,
            NICHTLADEN: NICHTLADEN_JSON,
            SOFORTLADEN: SOFORTLADEN_JSON,
            UEBERSCHUSS: UEBERSCHUSS_JSON
        }


# Automatiklabel
AM_SOFORTLADEN = SOFORTLADEN
AM_UEBERSCHUSS = UEBERSCHUSS
AM_HYBRIDAUTOMATIK = "Hybridautomatik"
AM_UEBERSCHUSS_NACHT = "Überschuss, über Nacht voll"
AM_HYBRIDAUTOMATIK_NACHT = "Hybrid, über Nacht voll"
AM_MANUAL = "Manuell"
