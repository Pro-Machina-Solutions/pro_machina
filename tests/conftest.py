import datetime as dt

import pytest

from pro_machina import (
    BatchMachine,
    BatchProduct,
    ContinuousMachine,
    ContinuousProduct,
    Problem,
    ShiftBreak,
    ShiftBuilder,
    ShiftPattern,
)
from pro_machina.config import Config
from pro_machina.durations import Mins, Weeks
from pro_machina.measures import Weight
from pro_machina.util import as_day_end, as_day_start, parse_datetime


@pytest.fixture(scope="function", autouse=True)
def base_problem():
    conf = Config()
    conf.timebucket = Mins(15)
    problem = Problem(
        start_time="2026-03-02 00:00:00", length=Weeks(1), config=conf
    )

    return problem


@pytest.fixture(scope="function")
def batch_prod():
    return BatchProduct("test batch", base_dimension=Weight)


@pytest.fixture(scope="function")
def cont_prod():
    return ContinuousProduct("test continuous", base_dimension=Weight)


@pytest.fixture(scope="function")
def batch_machine():
    return BatchMachine("test batch machine")


@pytest.fixture(scope="function")
def cont_machine():
    machine = ContinuousMachine("test continuous machine")
    machine.clear_shifts()
    machine._id = 0
    return machine


@pytest.fixture(scope="function")
def simple_shift():
    start_date = as_day_start(parse_datetime("2000-02-07"))

    six_two = ShiftBuilder(ref_start_date=start_date, name="Standard Six-Two")
    for _ in range(5):
        break_1_start = start_date + dt.timedelta(minutes=600)
        break_1_end = start_date + dt.timedelta(minutes=630)
        six_two.add_work_period(
            start_time=start_date + dt.timedelta(minutes=360),
            breaks=ShiftBreak(break_1_start, break_1_end),
            end_time=start_date + dt.timedelta(minutes=840),
        )
        start_date = as_day_end(start_date)

    six_two.add_downday(date="2000-02-12")
    six_two.add_downday(date="2000-02-13")

    six_two.build()
    return ShiftPattern(six_two)


@pytest.fixture(scope="function")
def irregular_shift_pattern():
    start_date = as_day_start(parse_datetime("2000-02-07"))

    sb = ShiftBuilder(start_date, name="Continental Rotation 1")
    for _ in range(4):
        start = start_date + dt.timedelta(minutes=360)
        break_1_start = start_date + dt.timedelta(minutes=600)
        break_1_end = start_date + dt.timedelta(minutes=630)
        break_2_start = start_date + dt.timedelta(minutes=840)
        break_2_end = start_date + dt.timedelta(minutes=855)

        sb.add_work_period(
            start_time=start,
            breaks=[
                ShiftBreak(break_1_start, break_1_end),
                ShiftBreak(break_2_start, break_2_end),
            ],
            end_time=start_date + dt.timedelta(minutes=1080),
        )
        start_date = as_day_end(start_date)

    sb.add_downday(date="2000-02-11")
    sb.add_downday(date="2000-02-12")
    sb.add_downday(date="2000-02-13")
    sb.add_downday(date="2000-02-14")

    sb.build()
    return ShiftPattern(sb)
