"""
In this example, we're just going to demonstrate how to define shift patterns
without trying to solve any optimisation problem. That's because the methods
are somewhat complex but it's a crucial feature that has a large impact on the
solutions.
"""

from pro_machina import (
    ContinuousMachine,
    ShiftBreak,
    ShiftBuilder,
    ShiftPattern,
)

# Until now, we've just been using a basic six-two example shift so it would be
# easiest to show how that was designed using the pro_machina API. The first
# thing we need to do is to set an example start date THAT IS IN THE PAST. Here
# we only need some date that represents a Monday to get started, so we can
# pick one in the year 2000 just to be safe. The goal is just to make a
# representative week.
six_two = ShiftBuilder(ref_start_date="2000-02-07", name="Standard Six-Two")

# Now we just add some dates during that week to represent each day
six_two.add_work_period(
    start_time="2000-02-07 06:00:00",
    end_time="2000-02-07 14:00:00",
)  # Monday
six_two.add_work_period(
    start_time="2000-02-08 06:00:00",
    end_time="2000-02-08 14:00:00",
)  # Tuesday
six_two.add_work_period(
    start_time="2000-02-09 06:00:00",
    end_time="2000-02-09 14:00:00",
)  # Wednesday
six_two.add_work_period(
    start_time="2000-02-10 06:00:00",
    end_time="2000-02-10 14:00:00",
)  # Thursday
six_two.add_work_period(
    start_time="2000-02-11 06:00:00",
    end_time="2000-02-11 14:00:00",
)  # Friday

# There is not going to be any work on Saturday and Sunday but we want to
# reflect that in the pattern itself so that we cover the whole week. That's
# because the pattern is (potentially) going to be tessellated to cover the
# entire problem duration
six_two.add_downday(date="2000-02-12")
six_two.add_downday(date="2000-02-13")

# We're done adding days, so we can finalise the pattern
six_two.build()

# If we want to save this for future, we can now export this as a JSON template
# six_two.save_pattern("<SOME PATH HERE>")

# And now we can create a Shift Pattern for use on a machine
six_two_pattern = ShiftPattern(six_two)

# If we want to load directly from a saved pattern in future, we could instead
# use:
# six_two = ShiftPattern.load_from_file("<SOME PATH HERE>")

# The simplest use of the shift pattern is just to set a machine to use it
# indiscriminantly throughout the problem duration, covering every week
machine = ContinuousMachine("Some Machine")
machine.add_shift(six_two_pattern)

# We can do the same to define a 10-6 shift rotation. Note here that it starts
# on the Sunday evening, so we need to knock our date back one day
ten_six = ShiftBuilder(ref_start_date="2000-02-06", name="Stanbdard Ten-Six")

ten_six.add_work_period(
    start_time="2000-02-06 22:00:00",
    end_time="2000-02-07 06:00:00",
)  # Sunday - Monday
ten_six.add_work_period(
    start_time="2000-02-07 22:00:00",
    end_time="2000-02-08 06:00:00",
)  # Monday - Tuesday
ten_six.add_work_period(
    start_time="2000-02-08 22:00:00",
    end_time="2000-02-09 06:00:00",
)  # Tuesday - Wednesday
ten_six.add_work_period(
    start_time="2000-02-09 22:00:00",
    end_time="2000-02-10 06:00:00",
)  # Wednesday - Thursday
ten_six.add_work_period(
    start_time="2000-02-10 22:00:00",
    end_time="2000-02-11 06:00:00",
)  # Thursday - Friday

ten_six.add_downday(date="2000-02-12")
ten_six.add_downday(date="2000-02-13")

ten_six.build()
ten_six_pattern = ShiftPattern(ten_six)

# Note now that the machine will be working 10-6 and 6-2 shifts throughout the
# problem span. The shifts do not overlap on hours but will work to form
# complete 16 hour blocks of production
machine.add_shift(ten_six_pattern)

# The first question now is what happens if there is a factory shutdown period?
# We can cover that by instead choosing set dates
# We need to be careful here now, though, because we originally set the shift
# patterns to cover all weeks. So whilst the below is valid code it will not
# avail you unless you clear the shift list first. Normally you wouldn't need
# to do this as you can layer shifts up, but it's provided as a convenience
machine.clear_shifts()

machine.add_shift(
    six_two_pattern, start_date="2026-03-02", end_date="2026-08-05"
)
machine.add_shift(
    six_two_pattern, start_date="2026-03-20", end_date="2026-12-31"
)
machine.add_shift(
    ten_six_pattern, start_date="2026-03-02", end_date="2026-08-04"
)
machine.add_shift(
    ten_six_pattern, start_date="2026-03-19", end_date="2026-12-31"
)

# Next, we'll run foul of working time regulations if we don't include breaks
# so we can add them too. You get to choose the production during the break
# period as not all machines will stop completely if you have staggered breaks.
# This is specified as a percentage of the machine's typical output (by default
# zero).
six_two = ShiftBuilder(ref_start_date="2000-02-07", name="Standard Six-Two")

# Now we just add some dates during that week to represent each day
six_two.add_work_period(
    start_time="2000-02-07 06:00:00",
    breaks=[
        ShiftBreak(
            "2000-02-07 10:00:00", "2000-02-07 10:30:00", productivity=25
        )
    ],
    end_time="2000-02-07 14:00:00",
)  # Monday
six_two.add_work_period(
    start_time="2000-02-08 06:00:00",
    breaks=[
        ShiftBreak(
            "2000-02-08 10:00:00", "2000-02-08 10:30:00", productivity=25
        )
    ],
    end_time="2000-02-08 14:00:00",
)  # Tuesday
six_two.add_work_period(
    start_time="2000-02-09 06:00:00",
    breaks=[
        ShiftBreak(
            "2000-02-09 10:00:00", "2000-02-09 10:30:00", productivity=25
        )
    ],
    end_time="2000-02-09 14:00:00",
)  # Wednesday
six_two.add_work_period(
    start_time="2000-02-10 06:00:00",
    breaks=[
        ShiftBreak(
            "2000-02-10 10:00:00", "2000-02-10 10:30:00", productivity=25
        )
    ],
    end_time="2000-02-10 14:00:00",
)  # Thursday
six_two.add_work_period(
    start_time="2000-02-11 06:00:00",
    breaks=[
        ShiftBreak(
            "2000-02-11 10:00:00", "2000-02-11 10:30:00", productivity=25
        )
    ],
    end_time="2000-02-11 14:00:00",
)  # Friday

six_two.add_downday(date="2000-02-12")
six_two.add_downday(date="2000-02-13")

# We're done adding days, so we can finalise the pattern
six_two.build()

machine.clear_shifts()
machine.add_shift(ShiftPattern(six_two))

# We could combine the two shifts, though to make our life easier. We can also
# account for reduced production during shift handovers if we wanted to.
combined = ShiftBuilder(ref_start_date="2000-02-06", name="Ten-Six, Six-Two")

# combined.add_work_period(
#     start_time="2000-02-06 22:00:00",
#     end_time="2000-02-06 22:30:00",
#     productivity=50,
# )  # Night shift ramp up time
combined.add_work_period(
    start_time="2000-02-06 22:30:00",
    breaks=[
        ShiftBreak("2000-02-07 02:00:00", "2000-02-07 02:30:00"),
        ShiftBreak("2000-02-07 04:00:00", "2000-02-07 04:15:00"),
    ],
    end_time="2000-02-07 06:00:00",
)  # Main night shift assuming 100% poroductivity, but zero during breaks
# combined.add_work_period(
#     start_time="2000-02-07 06:00:00",
#     end_time="2000-02-07 06:30:00",
#     productivity=50,
# )  # Morning shift ramp up time
# combined.add_work_period(
#     start_time="2000-02-07 06:30:00",
#     breaks=[
#         ShiftBreak("2000-02-07 10:00:00", "2000-02-07 10:30:00"),
#         ShiftBreak("2000-02-07 12:00:00", "2000-02-07 12:15:00"),
#     ],
#     end_time="2000-02-07 14:00:00",
# )  # Main morning shift assuming 100% poroductivity, but zero during breaks
combined.build()


sp = ShiftPattern.load_example_pattern("six_two_example")


sb = ShiftBuilder(ref_start_date="2026-02-23", name="Single day")
sb.add_work_period(
    start_time="2026-02-23 06:00:00",
    end_time="2026-02-23 06:30:00",
    productivity=25,
)
sb.add_work_period(
    start_time="2026-02-23 06:30:00",
    end_time="2026-02-23 13:30:00",
    productivity=100,
)
sb.add_work_period(
    start_time="2026-02-23 13:30:00",
    end_time="2026-02-23 14:00:00",
    productivity=60,
)

print()
print("###############")
print("SAME DAY RAMP UP AND DOWN")
sb.build()
for item in sb._shift_days:
    print(item)

############################################

# Simplest shift with no breaks
sb = ShiftBuilder(ref_start_date="2026-02-23", name="6-2")
sb.add_work_period(
    start_time="2026-02-23 06:00:00",
    end_time="2026-02-23 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 06:00:00",
    end_time="2026-02-24 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 06:00:00",
    end_time="2026-02-25 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 06:00:00",
    end_time="2026-02-26 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-27 06:00:00",
    end_time="2026-02-27 13:30:00",
)
sb.add_downday(date="2026-02-28")
sb.add_downday(date="2026-03-01 10:00:00")

print()
print("###############")
print("6-2 SHIFT WITH NO BREAKS")
sb.build()
for item in sb._shift_days:
    print(item)

pattern = ShiftPattern(sb)
# sb.save_pattern("six_two_example.json")

############################################

# Simplest shift with no breaks
sb = ShiftBuilder(ref_start_date="2026-02-23", name="two_ten")
sb.add_work_period(
    start_time="2026-02-23 14:00:00",
    # breaks=ShiftBreak("2026-02-23 18:00:00", "2026-02-23 18:30:00", 50),
    end_time="2026-02-23 22:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 14:00:00",
    # breaks=ShiftBreak("2026-02-24 18:00:00", "2026-02-24 18:30:00", 50),
    end_time="2026-02-24 22:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 14:00:00",
    # breaks=ShiftBreak("2026-02-25 18:00:00", "2026-02-25 18:30:00", 50),
    end_time="2026-02-25 22:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 14:00:00",
    # breaks=ShiftBreak("2026-02-26 18:00:00", "2026-02-26 18:30:00", 50),
    end_time="2026-02-26 22:00:00",
)
sb.add_work_period(
    start_time="2026-02-27 14:00:00",
    # breaks=ShiftBreak("2026-02-27 18:00:00", "2026-02-27 18:30:00", 50),
    end_time="2026-02-27 21:30:00",
)
sb.add_downday(date="2026-02-28")
sb.add_downday(date="2026-03-01 10:00:00")
sb.build()
# sb.save_pattern("two_ten_example.json")

# Shift goes beyond midnight, with no breaks
sb = ShiftBuilder(ref_start_date="2026-02-22", name="10-6")
sb.add_work_period(
    start_time="2026-02-22 22:00:00",
    end_time="2026-02-23 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-23 22:00:00",
    end_time="2026-02-24 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 22:00:00",
    end_time="2026-02-25 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 22:00:00",
    end_time="2026-02-26 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 22:00:00",
    end_time="2026-02-27 06:00:00",
)
sb.add_downday("2026-02-28")
sb.add_downday("2026-03-01")

sb.build()
print()
print("###############")
print("10-6 SHIFT NO BREAKS")
for item in sb._shift_days:
    print(item)

#########################

# Simplest shift with breaks
sb = ShiftBuilder(
    ref_start_date="2026-02-23", name="6am-2pm break 10am-10:30am"
)
sb.add_work_period(
    start_time="2026-02-23 06:00:00",
    breaks=ShiftBreak("2026-02-23 10:00:00", "2026-02-23 10:30:00", 50),
    end_time="2026-02-23 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 06:00:00",
    breaks=ShiftBreak("2026-02-24 10:00:00", "2026-02-24 10:30:00", 50),
    end_time="2026-02-24 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 06:00:00",
    breaks=ShiftBreak("2026-02-25 10:00:00", "2026-02-25 10:30:00", 50),
    end_time="2026-02-25 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 06:00:00",
    breaks=ShiftBreak("2026-02-26 10:00:00", "2026-02-26 10:30:00", 50),
    end_time="2026-02-26 14:00:00",
)
sb.add_work_period(
    start_time="2026-02-27 06:00:00",
    breaks=ShiftBreak("2026-02-27 10:00:00", "2026-02-27 10:30:00", 50),
    end_time="2026-02-27 13:30:00",
)
sb.add_downday(date="2026-02-28")
sb.add_downday(date="2026-03-01 10:00:00")

print()
print("###############")
print("6am-2 SHIFT WITH 1 BREAK")
sb.build()
for item in sb._shift_days:
    print(item)

# sb.save_pattern("six_two_break_example.json")

############################################

# Shift goes beyond midnight, with a break in the next day
sb = ShiftBuilder(ref_start_date="2026-02-22", name="10-6")
sb.add_work_period(
    start_time="2026-02-22 22:00:00",
    breaks=ShiftBreak("2026-02-23 02:00:00", "2026-02-23 02:30:00", 50),
    end_time="2026-02-23 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-23 22:00:00",
    breaks=ShiftBreak("2026-02-24 02:00:00", "2026-02-24 02:30:00", 50),
    end_time="2026-02-24 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 22:00:00",
    breaks=ShiftBreak("2026-02-25 02:00:00", "2026-02-25 02:30:00", 50),
    end_time="2026-02-25 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 22:00:00",
    breaks=ShiftBreak("2026-02-26 02:00:00", "2026-02-26 02:30:00", 50),
    end_time="2026-02-26 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 22:00:00",
    breaks=ShiftBreak("2026-02-27 02:00:00", "2026-02-27 02:30:00", 50),
    end_time="2026-02-27 06:00:00",
)
sb.add_downday("2026-02-28")
sb.add_downday("2026-03-01")

sb.build()
print()
print("###############")
print("10-6 SHIFT WITH 1 BREAK")
for item in sb._shift_days:
    print(item)

############################################

# A continental shift pattern where the repeating unit is 8 days, not 7
# Also multiple breaks
sb = ShiftBuilder("2026-02-23 00:00:00", name="Continental Rotation 1")
sb.add_work_period(
    start_time="2026-02-23 06:00:00",
    breaks=[
        ShiftBreak("2026-02-23 10:00:00", "2026-02-23 10:30:00"),
        ShiftBreak("2026-02-23 14:00:00", "2026-02-23 14:15:00"),
    ],
    end_time="2026-02-23 18:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 06:00:00",
    breaks=[
        ShiftBreak("2026-02-24 10:00:00", "2026-02-24 10:30:00"),
        ShiftBreak("2026-02-24 14:00:00", "2026-02-24 14:15:00"),
    ],
    end_time="2026-02-24 18:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 06:00:00",
    breaks=[
        ShiftBreak("2026-02-25 10:00:00", "2026-02-25 10:30:00"),
        ShiftBreak("2026-02-25 14:00:00", "2026-02-25 14:15:00"),
    ],
    end_time="2026-02-25 18:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 06:00:00",
    breaks=[
        ShiftBreak("2026-02-26 10:00:00", "2026-02-26 10:30:00"),
        ShiftBreak("2026-02-26 14:00:00", "2026-02-26 14:15:00"),
    ],
    end_time="2026-02-26 18:00:00",
)
sb.add_downday(date="2026-02-27")
sb.add_downday(date="2026-02-28")
sb.add_downday(date="2026-03-01")
sb.add_downday(date="2026-03-02")

print()
print("###############")
print("4 ON, 4 OFF CONTINENTAL, 2 BREAKS")
sb.build()
for item in sb._shift_days:
    print(item)

# sb.save_pattern("continental_example.json")

############################################

# Shift goes beyond midnight, with a break spanning midnight
sb = ShiftBuilder(ref_start_date="2026-02-22", name="10-6")
sb.add_work_period(
    start_time="2026-02-22 22:00:00",
    breaks=ShiftBreak("2026-02-22 23:45:00", "2026-02-23 00:15:00", 50),
    end_time="2026-02-23 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-23 22:00:00",
    breaks=ShiftBreak("2026-02-23 23:45:00", "2026-02-24 00:15:00", 50),
    end_time="2026-02-24 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-24 22:00:00",
    breaks=ShiftBreak("2026-02-24 23:45:00", "2026-02-25 00:15:00", 50),
    end_time="2026-02-25 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-25 22:00:00",
    breaks=ShiftBreak("2026-02-25 23:45:00", "2026-02-26 00:15:00", 50),
    end_time="2026-02-26 06:00:00",
)
sb.add_work_period(
    start_time="2026-02-26 22:00:00",
    breaks=ShiftBreak("2026-02-26 23:45:00", "2026-02-27 00:15:00", 50),
    end_time="2026-02-27 06:00:00",
)
sb.add_downday("2026-02-28")
sb.add_downday("2026-03-01")

sb.build()
print()
print("###############")
print("10-6 SHIFT WITH 1 BREAK SPANNING MIDNIGHT")
for item in sb._shift_days:
    print(item)

############################################
