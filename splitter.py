import functools
import itertools
import operator
from railroads_hillclimber.stock import Calculative, Train
from typing import Iterable, Iterator, Sequence, Tuple

def net_force_capacity(
        x: Calculative,
        grade: float,
        max_power: float = 1.0) -> float:
    """Compute the net force capacity of x.

    x -- Entity to measure.
    grade -- Grade to measure x on.
    max_power -- Maximum power ratio to apply.
    """
    return x.tractive_effort * max_power - x.starting_force(grade)

def fastsplit(
        capacity: float,
        cut: Sequence[float],
        collect_net: bool = False) -> Tuple[int]:
    """Run the Fastsplit algorithm.

    capacity -- Amount of head force capacity available.
    cut -- Forces for each unit in the cut.
    collect_net -- If True, when a subcut has a positive force, it is added
    to power for future subcuts.
    """
    splits = []
    assert capacity > 0
    while len(cut) > 0:
        for this_len in range(len(cut), 0, -1):
            if capacity + sum(cut[:this_len]) > 0:
                splits.append(this_len)
                if collect_net:
                    capacity += sum(x for x in cut[:this_len] if x>0)
                cut = cut[this_len:]
                break
        else:
            return None
    return tuple(splits)

def compute_split(
        power: Calculative,
        cut: Train,
        grade: float,
        max_power: float = 1.0,
        collect_net: bool = False) -> Tuple[int]:
    """
    Compute splits for the given cut such that each subcut can be pulled up
    grade by power.

    power -- Unit(s) used for the hillclimbing operation.
    cut -- Units that need to be brought up the hill.
    grade -- The gradient of the hill.
    max_power -- Maximum power ratio to use.
    collect_net -- After a subcut is brought up the hill, should units in it
    that are capable of making the grade under their own power be added to
    the power for future subcuts?
    """
    f = functools.partial(
            net_force_capacity,
            grade=grade,
            max_power=max_power,
        )
    return fastsplit(
            f(power),
            tuple(map(f, cut)),
            collect_net=collect_net,
        )

def split_to_slices(split: Iterable[int]) -> Iterator[slice]:
    """Convert a splitting sequence into an iterator of slices."""
    l1, l2 = itertools.tee(split)
    e = itertools.accumulate(l2)
    e1, e2 = itertools.tee(e)
    s = map(operator.sub, e2, l1)
    return map(slice, s, e1)

def split_to_subcuts(
        cut: Train,
        split: Iterable[int]) -> Iterator[Train]:
    """Convert a splitting sequence into an iterator of subcut trains."""
    return map(Train, map(cut.__getitem__, split_to_slices(split)))

def split_to_trips(
        power: Calculative,
        cut: Train,
        split: Iterable[int],
        collect_tractive: bool = False) -> Iterator[Train]:
    """Convert a splitting sequence into an iterator of trip trains."""
    sc = split_to_subcuts(cut, split)
    if collect_tractive:
        sc, sc2 = itertools.tee(sc)
        tu = map(Train, map(operator.methodcaller('tractive_units'), sc2))
        pw = itertools.accumulate(tu, initial=power)
    else:
        pw = itertools.repeat(power)
    return map(operator.add, pw, sc)
