import railroads_hillclimber.prefab.factory as factory
import railroads_hillclimber.prefab.cargo as cargo

from railroads_hillclimber.prefab.factory import difficulty

climax = factory.SoloLocomotiveFactory("Climax", 55678.0, 17486.0)
class70 = factory.TenderLocomotiveFactory("D&RG Class 70", 74260.0, 53000.0, 15716.0)
heisler = factory.SoloLocomotiveFactory("Heisler", 65731.0, 13219.0)
mogul = factory.TenderLocomotiveFactory("Cooke Mogul", 58300.0, 45000.0, 12063.0)
eureka = factory.TenderLocomotiveFactory("Eureka", 37919.0, 27573.0, 5620.0)
porter040 = factory.SoloLocomotiveFactory("Porter (0-4-0)", 14236.0, 2916.0)
porter042 = factory.SoloLocomotiveFactory("Porter (0-4-2)", 16236.0, 2916.0)
handcar = factory.SoloLocomotiveFactory("Handcar", 2205.0, 112.0)

flatcar_round = factory.CarFactory("Flatcar - Rounds", 8360.0, {
    cargo.logs: 6, cargo.pipes: 9})
flatcar_stakes = factory.CarFactory("Flatcar - Stakes", 8800.0, {
    cargo.lumber: 6, cargo.beams: 3, cargo.raw_iron: 3, cargo.rails: 10})
flatcar_bulkhead = factory.CarFactory("Flatcar - Bulkhead", 9020.0, {
    cargo.cordwood: 8, cargo.oil_barrels: 46})
hopper = factory.CarFactory("Hopper", 13200.0, {
    cargo.iron_ore: 10, cargo.coal: 10})
tanker = factory.CarFactory("Tanker", 30135.0, {
    cargo.crude_oil: 12})
boxcar = factory.CarFactory("Box Car", 17463.0, {
    cargo.tools: 32})
caboose = factory.CarFactory("Bobber Caboose", 11880.0)

del factory # Clean namespace for star-import
