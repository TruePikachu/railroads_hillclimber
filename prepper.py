import itertools
import operator
from railroads_hillclimber.stock import Train
from typing import Generator, Tuple

def cluster_forces(
        train: Train,
        grade: float,
        power_ratio: float = 1.0) -> Generator[Tuple[int, float], None, None]:
    """Group train into an ordering of pairs of lengths and net forces.

    Each pair represents a group of contiguous units where either all the
    units have a strictly positive net force, or they all have zero or
    negative net force. This has the effect of grouping apart stuff that
    positively effects the train from that which negatively effects the
    train.

    In each pair, the first element is the length of the subgroup, while the
    second element is the total net force within the subgroup.
    """
    forces = map(
            operator.methodcaller(
                'net_force',
                grade=grade, 
                power_ratio=power_ratio),
            train)
    groups = map(tuple, map(
        operator.itemgetter(1),
        itertools.groupby(forces, lambda x: x>0)))
    for group in groups:
        yield (len(group), sum(group))

def collect_front_len(
        train: Train,
        grade: float,
        power_ratio: float = 1.0) -> int:
    """Determine how much of the front of train has the best net force."""
    if len(train)==0:
        return 0
    clusters = cluster_forces(train, grade, power_ratio)
    accum_clusters = itertools.accumulate(
            clusters,
            lambda a, b: (a[0]+b[0], a[1]+b[1]))
    best_cluster = max(accum_clusters, key=operator.itemgetter(1))
    return best_cluster[0]

def collect_front_slice(
        train: Train,
        grade: float,
        power_ratio: float = 1.0) -> slice:
    """Get the slice from the front of train that has the best net force."""
    return slice(None, collect_front_len(train, grade, power_ratio))

def collect_back_slice(
        train: Train,
        grade: float,
        power_ratio: float = 1.0) -> slice:
    """Get the slice from the back of train that has the best net force."""
    rev_train = Train(reversed(train))
    len_rev_train = collect_front_len(rev_train, grade, power_ratio)
    return slice(len(train)-len_rev_train, None)

def collect_mid_slice(
        train: Train,
        grade: float,
        power_ratio: float = 1.0) -> slice:
    """Get the slice from the middle of train that has the best net force."""
    if len(train)==0:
        return slice(None, None)
    clusters = cluster_forces(train, grade, power_ratio)
    accum_clusters = itertools.chain(
            ((0, 0.0),),
            itertools.accumulate(
                clusters,
                lambda a, b: (a[0]+b[0], a[1]+b[1])))
    accum_cluster_pairs = itertools.combinations(accum_clusters, 2)
    slice_pairs = map(
            lambda x: (slice(x[0][0], x[1][0]), x[1][1]-x[0][1]),
            accum_cluster_pairs)
    best_pair = max(slice_pairs, key=operator.itemgetter(1))
    return best_pair[0]

