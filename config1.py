# This program looks up and uses the Airnow AQI PM2.5 data. The AQI number is a yardstick that runs
# from 0 to 500. The higher the AQI value, the greater the level of air pollution and the
# greater the health concern. For example, an AQI value of 50 or below represents
# good air quality, while an AQI value over 300 represents hazardous air quality.
#
# hi_act is the PM2.5 AQI level where the economizer goes into "Outdoor air smoke limiting mode"
#
# low_act is the PM2.5 AQI level where the economizer returns to it's "normal mode of operation"
#
# distanace: If no reporting area is associated with the Zip code, current observations from a
# nearby reporting area within this distance (in miles) will be returned, if available.

CONFIG = {
    "token": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "zipcode": "12345",
    "hi_act": 40,
    "low_act": 30,
    "distance":60, # moniitor distance should be used to "see" similar outdoor air to zipcode location.
}
