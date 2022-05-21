from railroads_hillclimber import stock as stock

def SoloLocomotiveFactory(
        default_name: str,
        mass: float,
        tractive_effort: float):
    def inner(name: str = default_name):
        return stock.TractiveCar(
                name=name,
                mass=mass,
                tractive_effort=tractive_effort,
            )
    inner.__doc__ = f"""Make a {default_name} locomotive.

    name -- Name to assign the locomotive.
    """
    return inner

def TenderLocomotiveFactory(
        default_name: str,
        locomotive_mass: float,
        tender_mass: float,
        tractive_effort: float):
    def inner(name: str = default_name):
        locomotive = stock.TractiveCar(
                name=name,
                mass=locomotive_mass,
                tractive_effort=tractive_effort,
            )
        tender = stock.Car(
                name=name+' (Tender)',
                mass=tender_mass,
            )
        return CarGroup(
                name=name,
                train=(locomotive, tender),
            )
    inner.__doc__ = f"""Make a {default_name} locomotive and tender.

    name -- Name to assign the locomotive and group.
    """
    return inner

class CargoHelper:
    """Helper class representing cargo information.

    Use the unmodified instance directly to represent the maximum amount of cargo
    the car can hold, or use __mul__ to specify the quantity.
    """
    def __init__(self, name, each_mass, count = None):
        self._name = name
        self._each_mass = each_mass
        self._count = count

    @property
    def name(self):
        """Name of the cargo."""
        return self._name

    @property
    def each_mass(self):
        """Mass of one unit of the cargo at Realistic difficulty."""
        return self._each_mass

    @property
    def count(self):
        """Amount of cargo, or None to use a full car."""
        return self._count

    def __mul__(self, n):
        if self._count is None:
            return CargoHelper(self._name, self._each_mass, n)
        else:
            return CargoHelper(self._name, self._each_mass, n * self._count)

    def compute(self, max_quantity):
        if self._count is None:
            count = max_quantity
        else:
            count = self._count

        deco_name = f"{self._name} x{count}"

        if count > max_quantity:
            raise ValueError(f"{deco_name} exceeds limit of {max_quantity}")

        return deco_name, count * self._each_mass

class difficulty:
    """Singleton class responsible for difficulty setting.

    difficulty.multiplier is the mass multiplier for cargo. Difficulties are
    available as difficulty.CASUAL through difficulty.REALISTIC.
    """
    multiplier = 1.0

    CASUAL = 0.0
    EASY = 0.25
    MEDIUM = 0.5
    HARD = 0.75
    REALISTIC = 1.0

def CarFactory(
        default_name: str,
        empty_mass: float,
        permitted_cargo: dict = {}):
    permitted_base_names = {x.name: a for x,a in permitted_cargo.items()}
    def inner(name=None, cargo=None):
        global cargo_mass_multiplier
        used_name = name if name else default_name
        mass = empty_mass
        if cargo is not None:
            permitted = permitted_base_names.get(cargo.name, 0)
            cargo_desc, cargo_mass = cargo.compute(permitted)
            if name is None:
                used_name = f"{used_name} ({cargo_desc})"
            mass += cargo_mass * difficulty.multiplier
        return stock.Car(name=used_name, mass=mass)
    if len(permitted_cargo)>0:
        inner.__doc__ = f"""Create a {default_name} cargo car.

        name -- Name to assign the car.
        cargo -- CargoHelper instance representing the car contents. See
        factory.cargo.
        """
    else:
        inner.__doc__ = f"""Create a {default_name} car.

        name -- Name to assign the car.
        cargo -- Unused, leave as the default value.
        """
    return inner
