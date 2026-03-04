from enum import Enum

import u


class WEEKDAY(Enum):
    SUN: 0
    MON: 1
    TUE: 2
    WED: 3
    THU: 4
    FRI: 5
    SAT: 6


print(u.hour(3).to_number(u.min))  # What I wanted
print(u.h(3).to_number(u.min))  # Also what I wanted
print(u.h(3).to_number(u.m))  # Nonsense
# print(u.minute(3).)
# print(u.m)

SECONDS = u.seconds(1)
MINUTES = u.minutes(1)
print((u.hour(5) + u.min(23)).to_number(u.sec))
print((u.hours(24) / u.min(17)).to_number(u.sec))
print((u.sec(4) - u.sec(1)).to_number(u.sec))

# print(HOURS)


# print(MINUTES)
# unit = u.
# unit = u.units(5)
# print(unit)
