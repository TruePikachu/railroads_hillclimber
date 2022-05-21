from railroads_hillclimber.prefab.factory import CargoHelper

logs = CargoHelper("Logs", 4409.0)
cordwood = CargoHelper("Cordwood", 2646.0)
lumber = CargoHelper("Lumber", 2976.0)
beams = CargoHelper("Beams", 3109.0)
raw_iron = CargoHelper("Raw Iron", 3285.0)
rails = CargoHelper("Rails", 1984.0)
pipes = CargoHelper("Steel Pipes", 3968.0)
oil_barrels = CargoHelper("Oil Barrels", 302.0)
iron_ore = CargoHelper("Iron Ore", 2205.0)
coal = CargoHelper("Coal", 2205.0)
crude_oil = CargoHelper("Crude Oil", 2205.0)
tools = CargoHelper("Crate Tools", 220.0)

del CargoHelper # Clean namespace for star-import
