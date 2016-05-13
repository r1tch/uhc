#!env python
"""
Original by Michel Anders
http://michelanders.blogspot.fr/2010/12/calulating-sunrise-and-sunset-in-python.html

...adjusted for returning timestamps as seconds, using UTC always
"""

from datetime import datetime, time, timezone
from math import cos, sin, acos, asin, tan
from math import degrees as deg, radians as rad


class SunCalc:
    """
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
    """

    def __init__(self, lat=52.8948846, lon=10.4468234):
        """
        Instanciate class, by default set Suderburg, Germany as base
        """
        self.coord = (lat, lon)
        self.day = None
        self.time = None

    def sunrise(self, when=datetime.now()):
        """
        return the time of sunrise as a datetime.time object
        when is a datetime.datetime object. If none is given
        a local time zone is assumed (including daylight saving
        if present)
        """
        self.__preptime(when)
        self.__calc()
        return SunCalc.__timefromdecimalday(self.sunrise_t)

    def sunset(self, when=datetime.now()):
        """
        returns datetime when sun will set
        """
        self.__preptime(when)
        self.__calc()
        return SunCalc.__timefromdecimalday(self.sunset_t)

    def solarnoon(self, when=datetime.now()):
        """
        datetime of solar noon
        """
        self.__preptime(when)
        self.__calc()
        return SunCalc.__timefromdecimalday(self.solarnoon_t)

    @staticmethod
    def __timefromdecimalday(day):
        """
        returns a seconds from epoch
        """
        return int(day*60*60*24)

    def __preptime(self, when):
        """
        Extract information in a suitable format from when,
        a datetime.datetime object.
        """
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distibuted as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for
        # 18/12/2010
        self.day = when.toordinal() - (734124 - 40528)

    def __calc(self):
        """
        Perform the actual calculations for sunrise, sunset and
        a number of related quantities.
        The results are stored in the instance variables
        sunrise_t, sunset_t and solarnoon_t
        """
        # in hours, east is positive
        latitude = self.coord[0]
        longitude = self.coord[1]

        # daynumber 1=1/1/1900
        some_day = self.day

        # Julian day
        jday = some_day + 2415020.5
        # Julian century
        jcent = (jday - 2451545) / 36525

        Manom = 357.52911 + jcent * (35999.05029 - 0.0001537 * jcent)
        Mlong = 280.46646 + jcent * (36000.76983 + jcent * 0.0003032) % 360
        Eccent = 0.016708634 - jcent * (0.000042037 + 0.0001537 * jcent)
        Mobliq = 23 + (26 + ((21.448 - jcent * (46.815 + jcent * (0.00059 - jcent * 0.001813)))) / 60) / 60
        obliq = Mobliq + 0.00256 * cos(rad(125.04 - 1934.136 * jcent))
        vary = tan(rad(obliq / 2)) * tan(rad(obliq / 2))
        Seqcent = sin(rad(Manom)) * (1.914602 - jcent * (0.004817 + 0.000014 * jcent)) + sin(rad(2 * Manom)) * (0.019993 - 0.000101 * jcent) + sin(rad(3 * Manom)) * 0.000289
        Struelong = Mlong + Seqcent
        Sapplong = Struelong - 0.00569 - 0.00478 * sin(rad(125.04 - (1934.136 * jcent)))
        declination = deg(asin(sin(rad(obliq)) * sin(rad(Sapplong))))

        eqtime = 4 * deg(
            vary * sin(2 * rad(Mlong)) - 2 * Eccent * sin(rad(Manom)) + 4 * Eccent * vary * sin(rad(Manom)) * cos(
                2 * rad(Mlong)) - 0.5 * vary * vary * sin(4 * rad(Mlong)) - 1.25 * Eccent * Eccent * sin(
                2 * rad(Manom)))

        hourangle = deg(acos(cos(rad(90.833)) / (cos(rad(latitude)) * cos(rad(declination))) - tan(rad(latitude)) * tan(
            rad(declination))))

        self.solarnoon_t = (720 - 4 * longitude - eqtime) / 1440 + some_day - 25567
        self.sunrise_t = self.solarnoon_t - hourangle * 4 / 1440
        self.sunset_t = self.solarnoon_t + hourangle * 4 / 1440


if __name__ == "__main__":
    sun = SunCalc(lat=47.48094, lon=19.01664)   # Budapest, Hungary
    when = datetime.now()
    print("x:{}".format(repr(when)))
    when = datetime(2016,3,27,1,2,3, tzinfo=timezone.utc)
    print("x:{}".format(repr(when)))
    print(datetime.fromtimestamp(sun.sunrise(when)), datetime.fromtimestamp(sun.solarnoon(when)), datetime.fromtimestamp(sun.sunset(when)))
