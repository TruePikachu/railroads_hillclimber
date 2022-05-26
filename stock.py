from abc import ABC, abstractmethod
import collections.abc
import math
import operator

class Calculative(ABC):
    """Abstract base class that provides grade-related calculations.

    The equations are based on:

         M⋅(α + μ)
    F = ───────────
           ________
          ╱  2
        ╲╱  α  + 1

    α = grade (as slope)
    μ = coefficient of friction (0.004)
    M = total mass (pounds)
    F = total force (pounds of force)
    """

    @property
    @abstractmethod
    def mass(self):
        """Total mass of the rolling stock, in pounds."""
        pass

    @property
    @abstractmethod
    def tractive_effort(self):
        """Total tractive effort of the rolling stock, in pounds of force."""
        pass

    def starting_force(self, grade):
        """The amount of force needed to move the rolling stock upwards on the
        given grade, in pounds of force."""
        return self.mass * (grade + 0.004) / math.sqrt(grade * grade + 1)

    def starting_power(self, grade):
        """The percentage of the total tractive effort needed to move the
        rolling stock upwards on the given grade."""
        if self.tractive_effort > 0:
            return self.starting_force(grade) / self.tractive_effort
        else:
            return math.nan

    def spare_capacity(self, grade, power_ratio=1.0):
        """The amount of spare mass capacity on the given grade, in pounds."""
        return (self.tractive_effort * power_ratio
                * math.sqrt(grade * grade + 1) / (grade + 0.004) - self.mass)

    def maximum_grade(self, power_ratio=1.0):
        """The maximum grade this rolling stock can climb under its own power."""
        F = self.tractive_effort * power_ratio
        if F==0:
            return math.nan
        else:
            M = self.mass
            return ((M**2 * 0.004 - F * math.sqrt(
                    M**2 * (0.004**2 + 1) - F**2))
                / (F**2 - M**2))

    def net_force(self, grade, power_ratio=1.0):
        """Compute the net force applied by this rolling stock on grade with
        the provided power setting.

        This is positive iff the rolling stock can climb the grade from a
        standstill under its own power.
        """
        return self.tractive_effort * power_ratio - self.starting_force(grade)

class RollingStock(Calculative, ABC):
    """Abstract base class for everything that's treated as rolling stock."""

    @property
    @abstractmethod
    def name(self):
        """Name assigned to the rolling stock."""
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<{type(self).__name__} {self.name}>'

    def __add__(self, other):
        """Attach this piece of rolling stock to others, forming a Train."""
        if isinstance(other, RollingStock):
            return Train((self, other))
        elif isinstance(other, Train):
            return Train((self,) + tuple(other))
        else:
            return NotImplemented

    def __radd__(self, other):
        """Attach this piece of rolling stock to others, forming a Train."""
        if isinstance(other, RollingStock):
            return Train((other, self))
        elif isinstance(other, Train):
            return Train(tuple(other) + (self,))
        else:
            return NotImplemented

    def __mul__(self, n):
        """Make a Train composed of multiples of this piece of rolling stock."""
        return Train((self,) * n)
    __rmul__ = __mul__

class Car(RollingStock):
    """Base class for individual pieces of rolling stock."""

    def __init__(self, *, name, mass):
        """Create an individual piece of rolling stock.

        name -- The name to assign to the entity.
        mass -- The mass of the entity, in pounds.
        """
        self._name = name
        self._mass = mass

    @property
    def name(self):
        """Name assigned to the rolling stock."""
        return self._name

    @property
    def mass(self):
        """Mass of the rolling stock, in pounds."""
        return self._mass

    @property
    def tractive_effort(self):
        """Tractive effort of the rolling stock, in pounds of force."""
        return 0

class TractiveCar(Car):
    """Base class for individual pieces of rolling stock that apply tractive
    effort.
    """

    def __init__(self, name, mass, tractive_effort):
        """Create a piece of rolling stock that applies a tractive effort.

        name -- The name to assign to the entity.
        mass -- The mass of the entity, in pounds.
        tractive_effort -- The amount of tractive effort provided, in pounds
        of force.
        """
        super().__init__(name=name, mass=mass)
        self._tractive_effort = tractive_effort

    @property
    def tractive_effort(self):
        """Tractive effort of the rolling stock, in pounds of force."""
        return self._tractive_effort

class Train(collections.abc.Sequence, Calculative):
    """Container holding rolling stock in a specified order.

    This class is also the backbone of most computations related to rolling
    stock.
    """

    def __init__(self, rolling_stock):
        """Create a Train from rolling stock.

        Note this can be invoked with an iterable e.g.

            Train((locomotive, car, car, car, caboose))
            Train(another_train)
        
        or with a single RollingStock instance e.g.

            Train(locomotive)
            Train(caboose)
        """
        if isinstance(rolling_stock, RollingStock):
            self._elems = (rolling_stock,)
        else:
            self._elems = tuple(rolling_stock)

    def __getitem__(self, x):
        return self._elems[x]

    def __iter__(self):
        return iter(self._elems)

    def __len__(self):
        return len(self._elems)

    def __add__(self, other):
        """Attach this train to other rolling stock, making a longer train.

        other can be either a Train or RollingStock.
        """
        if isinstance(other, RollingStock):
            return Train(self._elems + (other,))
        elif isinstance(other, Train):
            return Train(self._elems + tuple(other))
        else:
            return NotImplemented

    def __radd__(self, other):
        """Attach this train to other rolling stock, making a longer train.

        other can be either a Train or RollingStock.
        """
        if isinstance(other, RollingStock):
            return Train((other,) + self._elems)
        elif isinstance(other, Train):
            return Train(tuple(other) + self._elems)
        else:
            return NotImplemented

    def __mul__(self, n):
        """Duplicate the cars in this train a number of times.

        Note this works the same as multiplying e.g. a list or tuple; cars will
        not be grouped together.
        """
        return Train(self._elems * n)
    __rmul__ = __mul__

    @property
    def mass(self):
        """Total mass of the rolling stock, in pounds."""
        return sum(map(operator.attrgetter('mass'), self))

    @property
    def tractive_effort(self):
        """Total tractive effort of the rolling stock, in pounds of force."""
        return sum(map(operator.attrgetter('tractive_effort'), self))

    def tractive_units(self):
        """Iterate over units in the train that provide tractive effort."""
        for x in self:
            if x.tractive_effort > 0:
                yield x

    def passive_units(self):
        """Iterate over units in the train that don't provide tractive
        effort.
        """
        for x in self:
            if x.tractive_effort == 0:
                yield x

    def flat_iter(self):
        """Iterate over all Car instances in the train.

        Note this differs from iter(Train) in that CarGroup instances are
        decomposed here.
        """
        for x in self:
            if isinstance(x, CarGroup):
                yield from x.train
            else:
                yield x

    def __repr__(self):
        return f'Train({repr(self._elems)})'


class CarGroup(RollingStock):
    """Class treating a Train of rolling stock as an indivisible entity for
    another Train.

    This class is important when dealing with things such as tendered
    locomotives, where in some ways you want to treat the locomotive as
    separate from the tender (e.g. train car length) but in others you want
    to treat them as a single car (e.g. computing splits for hillclimbing).
    """

    def __init__(self, name, train):
        """Construct a CarGroup from a Train, iterable, or (generally not
        recommended) single piece of rolling stock.

        name -- The name to assign the composite entity.
        train -- The train composing the entity. Note this argument is passed
        directly to Train.__init__().
        """
        self._name = name
        self._train = Train(train)

    @property
    def name(self):
        """Name assigned to the rolling stock."""
        return self._name

    @property
    def train(self):
        """Train comprising the CarGroup."""
        return self._train

    @property
    def mass(self):
        """Mass of the rolling stock, in pounds."""
        return self._train.mass

    @property
    def tractive_effort(self):
        """Tractive effort of the rolling stock, in pounds of force."""
        return self._train.tractive_effort
