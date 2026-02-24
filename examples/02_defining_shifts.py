from pro_machina import ShiftBreak, ShiftBuilder

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

############################################

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
sb = ShiftBuilder(ref_start_date="2026-02-23", name="6-2")
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
print("6-2 SHIFT WITH 1 BREAK")
sb.build()
for item in sb._shift_days:
    print(item)

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
    end_time="2026-02-25 06:00:00",
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
