from pro_machina import ShiftBreak, ShiftBuilder, ShiftPattern

sp = ShiftPattern.load_from_file("test_out.json")
print(sp._builder)

sb1 = ShiftBuilder(ref_start_date="2026-02-23", name="6-2")
sb1.add_work_period(
    start_time="2026-02-23 06:00:00",
    breaks=ShiftBreak("2026-02-23 10:00:00", "2026-02-23 10:30:00", 50),
    end_time="2026-02-23 14:00:00",
)
sb1.add_work_period(
    start_time="2026-02-24 06:00:00",
    breaks=ShiftBreak("2026-02-24 10:00:00", "2026-02-24 10:30:00", 50),
    end_time="2026-02-24 14:00:00",
)
sb1.add_work_period(
    start_time="2026-02-25 06:00:00",
    breaks=ShiftBreak("2026-02-25 10:00:00", "2026-02-25 10:30:00", 50),
    end_time="2026-02-25 14:00:00",
)
sb1.add_work_period(
    start_time="2026-02-26 06:00:00",
    breaks=ShiftBreak("2026-02-26 10:00:00", "2026-02-26 10:30:00", 50),
    end_time="2026-02-23 14:00:00",
)
sb1.add_work_period(
    start_time="2026-02-27 06:00:00",
    breaks=ShiftBreak("2026-02-27 10:00:00", "2026-02-27 10:30:00", 50),
    end_time="2026-02-27 13:30:00",
)
sb1.add_downday(date="2026-02-28")
sb1.add_downday(date="2026-03-01 10:00:00")

sb1.build()
s = ShiftPattern(sb1)
# sb1._save_pattern("test_pattern.json")

############################################

sb2 = ShiftBuilder(ref_start_date="2026-02-22", name="10-6")
sb2.add_work_period(
    start_time="2026-02-22 22:00:00",
    breaks=ShiftBreak("2026-02-23 02:00:00", "2026-02-23 02:30:00", 50),
    end_time="2026-02-23 06:00:00",
)
sb2.add_work_period(
    start_time="2026-02-23 22:00:00",
    breaks=ShiftBreak("2026-02-24 02:00:00", "2026-02-24 02:30:00", 50),
    end_time="2026-02-24 06:00:00",
)
sb2.add_work_period(
    start_time="2026-02-24 22:00:00",
    breaks=ShiftBreak("2026-02-25 02:00:00", "2026-02-25 02:30:00", 50),
    end_time="2026-02-25 06:00:00",
)
sb2.add_work_period(
    start_time="2026-02-25 22:00:00",
    breaks=ShiftBreak("2026-02-26 02:00:00", "2026-02-26 02:30:00", 50),
    end_time="2026-02-26 06:00:00",
)
sb2.add_work_period(
    start_time="2026-02-26 22:00:00",
    breaks=ShiftBreak("2026-02-27 02:00:00", "2026-02-27 02:30:00", 50),
    end_time="2026-02-27 06:00:00",
)
sb2.add_downday("2026-02-28")
sb2.add_downday("2026-03-01")

# sb2.build()
############################################

sb3 = ShiftBuilder("2026-02-23 00:00:00", name="Cont Rot 1")
sb3.add_work_period(
    start_time="2026-02-23 00:06:00",
    breaks=[
        ShiftBreak("2026-02-23 10:00:00", "2026-02-23 10:30:00"),
        ShiftBreak("2026-02-23 14:00:00", "2026-02-23 14:15:00"),
    ],
    end_time="2026-02-23 18:00:00",
)
sb3.add_work_period(
    start_time="2026-02-24 00:06:00",
    breaks=[
        ShiftBreak("2026-02-24 10:00:00", "2026-02-24 10:30:00"),
        ShiftBreak("2026-02-24 14:00:00", "2026-02-24 14:15:00"),
    ],
    end_time="2026-02-24 18:00:00",
)
sb3.add_work_period(
    start_time="2026-02-25 00:06:00",
    breaks=[
        ShiftBreak("2026-02-25 10:00:00", "2026-02-25 10:30:00"),
        ShiftBreak("2026-02-25 14:00:00", "2026-02-25 14:15:00"),
    ],
    end_time="2026-02-25 18:00:00",
)
sb3.add_work_period(
    start_time="2026-02-26 00:06:00",
    breaks=[
        ShiftBreak("2026-02-26 10:00:00", "2026-02-26 10:30:00"),
        ShiftBreak("2026-02-26 14:00:00", "2026-02-26 14:15:00"),
    ],
    end_time="2026-02-26 18:00:00",
)
sb3.add_downday(date="2026-02-27")
sb3.add_downday(date="2026-02-28")
sb3.add_downday(date="2026-03-01")
sb3.add_downday(date="2026-03-02")
