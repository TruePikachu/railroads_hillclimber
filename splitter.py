import functools
import itertools
import operator
from railroads_hillclimber.stock import Calculative, Train
from typing import Iterable, Iterator, Sequence, Tuple

def quicksplit(
        capacity: float,
        cut: Sequence[float]) -> Tuple[int]:
    """Run the Quicksplit algorithm.

    Strictly O(n), optimal when cut is strictly nonpositive.

    capacity -- Amount of head force capacity available.
    cut -- Forces for each unit in the cut.
    """
    splits = []
    assert capacity > 0
    while len(cut) > 0:
        remaining_capacity = capacity
        for take_len, next_force in zip(
                itertools.count(),
                itertools.chain(cut, (0.0,))):
            remaining_capacity += next_force
            if remaining_capacity < 0:
                break
        if take_len==0:
            return None
        else:
            splits.append(take_len)
            cut = cut[take_len:]
    return tuple(splits)

def fastsplit(
        capacity: float,
        cut: Sequence[float],
        collect_net: bool = False) -> Tuple[int]:
    """Run the Fastsplit algorithm.

    Worst case O(n²), optimal when cut is strictly nonpositive or when
    collect_net is True.

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

def smartsplit(
        capacity: float,
        cut: Sequence[float]) -> Tuple[int]:
    """Run the Smartsplit algorithm.

    Worst case O(n²), optimal in all cases.

    capacity -- Amount of head force capacity available.
    cut -- Forces for each unit in the cut.
    """
    assert capacity > 0
    cache = [0] * len(cut)
    # cache[N-1] holds, for the last N cars, either the optimal splits or a
    # lower bound on the number of splits required. This allows for quickly
    # resolving tail configurations when backtracking force providers.

    def f(cut, max_parts):
        if len(cut) == 0:
            return ()
        def r(result):
            if result is not None:
                cache[len(cut)-1] = result
            else:
                cache[len(cut)-1] = max_parts
            return result
        cached = cache[len(cut)-1]
        if isinstance(cached, tuple):
            if len(cached) <= max_parts:
                return cached
            else:
                return None
        elif cached >= max_parts:
            return None

        if max_parts == 1:
            if capacity + sum(cut) > 0:
                return r((len(cut),))
            else:
                return r(None)
        else:
            best_split = None
            best_split_len = max_parts+1
            this_len = len(cut)
            while this_len > 0:
                this_cut = cut[:this_len]
                if capacity + sum(this_cut) > 0:
                    # subcut is valid
                    split = f(cut[this_len:], best_split_len-2)
                    if split is not None:
                        # split is valid
                        split = (this_len,) + split
                        if len(split) < best_split_len:
                            best_split_len = len(split)
                            if best_split_len == 1:
                                return r(split)
                            best_split = split
                        # Check remove units from subcut to get rid of a force
                        # provider
                        for removed in reversed(this_cut):
                            this_len -= 1
                            if removed > 0:
                                break
                    else:
                        # split was not valid
                        this_len -= 1
                else:
                    # subcut was not valid
                    this_len -= 1
            return r(best_split)

    return f(cut, len(cut))

def compute_split(
        power: Calculative,
        cut: Train,
        grade: float,
        *,
        power_ratio: float = 1.0,
        collect_net: bool = False) -> Tuple[int]:
    """Compute splits for the given cut such that each subcut can be pulled up
    grade by power.

    The result is guaranteed to use the fewest number of subcuts possible.
    In the worst case, this will be an O(n²) operation on the train length.

    power -- Unit(s) used for the hillclimbing operation.
    cut -- Units that need to be brought up the hill.
    grade -- The gradient of the hill.
    power_ratio -- Maximum power ratio to use.
    collect_net -- After a subcut is brought up the hill, should units in it
    that are capable of making the grade under their own power be added to
    the power for future subcuts?
    """
    p = power.net_force(grade=grade, power_ratio=power_ratio)
    c = tuple(map(
        operator.methodcaller('net_force', grade=grade, power_ratio=power_ratio),
        cut))
    if max(c) <= 0.0:
        return quicksplit(p, c)
    elif collect_net is True:
        return fastsplit(p, c, collect_net=True)
    else:
        return smartsplit(p, c)

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
