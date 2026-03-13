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
# on the Sunday evening, so we need to knock our date back one day. Because we
# start work (albeit for two hours) on the Sunday, we don't want to add a
# downday to our pattern
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

ten_six.build()
ten_six_pattern = ShiftPattern(ten_six)

# Note now that the machine will be working 10-6 and 6-2 shifts throughout the
# problem span. The shifts do not overlap on hours but will work to form
# complete 16 hour blocks of production.
machine.add_shift(ten_six_pattern)

# The first question now is what happens if there is a factory shutdown period?
# We can cover that by instead choosing set dates.

# We need to be careful here now, though, because we originally set the shift
# patterns to cover all weeks. So, whilst the below is valid code it will not
# avail you unless you clear the shift list first. Normally you wouldn't need
# to do this as you can layer shifts up, but it's provided as a convenience.
# Shifts are applied in the order that they are defined, so this sets a new
# base shift pattern for our machine.
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

six_two.build()

machine.clear_shifts()
machine.add_shift(ShiftPattern(six_two))

# We could combine the two shifts though to make our life easier. We can also
# account for reduced production during shift handovers if we wanted to. This
# is going to be LONG (hence why you might want to save pre-mades as JSON).
# You could loop this but we'll do it piece-by-piece here though to
# demonstrate.
combined = ShiftBuilder(ref_start_date="2000-02-06", name="Ten-Six, Six-Two")

combined.add_work_period(
    start_time="2000-02-06 22:00:00",
    end_time="2000-02-06 22:30:00",
    productivity=50,
)  # Night shift ramp up time
combined.add_work_period(
    start_time="2000-02-06 22:30:00",
    breaks=[
        ShiftBreak("2000-02-07 02:00:00", "2000-02-07 02:30:00"),
        ShiftBreak("2000-02-07 04:00:00", "2000-02-07 04:15:00"),
    ],
    end_time="2000-02-07 06:00:00",
)  # Main night shift assuming 100% productivity, but zero during breaks
combined.add_work_period(
    start_time="2000-02-07 06:00:00",
    end_time="2000-02-07 06:30:00",
    productivity=50,
)  # Morning shift ramp up time
combined.add_work_period(
    start_time="2000-02-07 06:30:00",
    breaks=[
        ShiftBreak("2000-02-07 10:00:00", "2000-02-07 10:30:00"),
        ShiftBreak("2000-02-07 12:00:00", "2000-02-07 12:15:00"),
    ],
    end_time="2000-02-07 14:00:00",
)  # Main morning shift assuming 100% productivity, but zero during breaks
combined.add_work_period(
    start_time="2000-02-07 22:00:00",
    end_time="2000-02-07 22:30:00",
    productivity=50,
)  # Night shift again
combined.add_work_period(
    start_time="2000-02-07 22:30:00",
    breaks=[
        ShiftBreak("2000-02-08 02:00:00", "2000-02-08 02:30:00"),
        ShiftBreak("2000-02-08 04:00:00", "2000-02-08 04:15:00"),
    ],
    end_time="2000-02-08 06:00:00",
)
combined.add_work_period(
    start_time="2000-02-08 06:00:00",
    end_time="2000-02-08 06:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-08 06:30:00",
    breaks=[
        ShiftBreak("2000-02-08 10:00:00", "2000-02-08 10:30:00"),
        ShiftBreak("2000-02-08 12:00:00", "2000-02-08 12:15:00"),
    ],
    end_time="2000-02-08 14:00:00",
)
combined.add_work_period(
    start_time="2000-02-08 22:00:00",
    end_time="2000-02-08 22:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-08 22:30:00",
    breaks=[
        ShiftBreak("2000-02-09 02:00:00", "2000-02-09 02:30:00"),
        ShiftBreak("2000-02-09 04:00:00", "2000-02-09 04:15:00"),
    ],
    end_time="2000-02-09 06:00:00",
)
combined.add_work_period(
    start_time="2000-02-09 06:00:00",
    end_time="2000-02-09 06:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-09 06:30:00",
    breaks=[
        ShiftBreak("2000-02-09 10:00:00", "2000-02-09 10:30:00"),
        ShiftBreak("2000-02-09 12:00:00", "2000-02-09 12:15:00"),
    ],
    end_time="2000-02-09 14:00:00",
)
combined.add_work_period(
    start_time="2000-02-09 22:00:00",
    end_time="2000-02-09 22:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-09 22:30:00",
    breaks=[
        ShiftBreak("2000-02-10 02:00:00", "2000-02-10 02:30:00"),
        ShiftBreak("2000-02-10 04:00:00", "2000-02-10 04:15:00"),
    ],
    end_time="2000-02-10 06:00:00",
)
combined.add_work_period(
    start_time="2000-02-10 06:00:00",
    end_time="2000-02-10 06:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-10 06:30:00",
    breaks=[
        ShiftBreak("2000-02-10 10:00:00", "2000-02-10 10:30:00"),
        ShiftBreak("2000-02-10 12:00:00", "2000-02-10 12:15:00"),
    ],
    end_time="2000-02-10 14:00:00",
)
combined.add_work_period(
    start_time="2000-02-10 22:00:00",
    end_time="2000-02-10 22:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-10 22:30:00",
    breaks=[
        ShiftBreak("2000-02-11 02:00:00", "2000-02-11 02:30:00"),
        ShiftBreak("2000-02-11 04:00:00", "2000-02-11 04:15:00"),
    ],
    end_time="2000-02-11 06:00:00",
)
combined.add_work_period(
    start_time="2000-02-11 06:00:00",
    end_time="2000-02-11 06:30:00",
    productivity=50,
)
combined.add_work_period(
    start_time="2000-02-11 06:30:00",
    breaks=[
        ShiftBreak("2000-02-11 10:00:00", "2000-02-11 10:30:00"),
        ShiftBreak("2000-02-11 12:00:00", "2000-02-11 12:15:00"),
    ],
    end_time="2000-02-11 14:00:00",
)

# Just add the Saturday as a downday
combined.add_downday(date="2000-02-12")

combined.build()

# Since this is quite complicated and repetitive in terms of code, we can
# inspect what the built shift pattern looks like in the terminal.
combined.inspect()
print()
print("********************")
print()

# The last thing to cover are pattens that don't follow a regular weekly
# rotation like Continental shift patterns. Since these are irregular
# week-on-week, it's important to ensure that the start date chosen (although
# still somewhat arbitrary) actually aligns with the rotation itself.
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

sb.build()
sb.inspect()
