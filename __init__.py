import functools
import itertools
import operator
import railroads_hillclimber.prefab as prefab
import railroads_hillclimber.prepper as prepper
import railroads_hillclimber.splitter as splitter
import railroads_hillclimber.stock as stock
import typing

def compute_climb(
        train: stock.Train,
        grade: float,
        *,
        power_ratio: float = 1.0,
        collect_net: bool = False) -> typing.Sequence[
                 typing.Tuple[stock.Train, typing.Optional[stock.Train]]]:
    """Compute a sequence for climbing grade.

    Given a train, this function computes an optimal sequence of operations
    that can be used to climb up grade. This will require a siding at the
    top of the grade, unless it can be taken as a single trip.

    train -- The train that needs to be moved up the grade.
    grade -- The gradient that needs to be climbed, as a ratio (e.g.  0.10
    for a 10% grade)
    power_ratio -- Maximum throttle to require for the grade.
    collect_net -- If True, then every time we encounter a unit that's
    powerful enough to make the grade on its own, we add it to the
    collection of units used for power. This will technically result in
    rearrangement of the train.

    The return value is a sequence of pairs, such that for every pair, the
    first element is the train that's making it up the grade and the second
    element is the train that's heading back down. Note that, once the
    entire train is at the top, the second element will be None.
    """
    power_len = prepper.collect_front_len(train, grade, power_ratio)
    power = stock.Train(train[:power_len])
    cut = stock.Train(train[power_len:])
    splits = splitter.compute_split(power, cut, grade,
            power_ratio=power_ratio,
            collect_net=collect_net)
    subcuts = splitter.split_to_subcuts(cut, splits)
    subcuts, add_power = itertools.tee(subcuts)
    add_power = (filter(operator.methodcaller(
        'can_climb', grade=grade, power_ratio=power_ratio), x)
        for x in add_power)
    add_power = (functools.reduce(operator.add, x, stock.Train(()))
            for x in add_power)
    trip_power = itertools.accumulate(add_power, initial=power)
    up_power, down_power = itertools.tee(trip_power)
    down_power = itertools.islice(down_power, 1, None)
    up = map(operator.add, up_power, subcuts)
    down = down_power
    trips = list(zip(up, down))
    trips[-1] = (trips[-1][0], None)
    return trips
