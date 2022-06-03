# railroads_hillclimber -- Railroads Online hill-climbing calculator

`railroads_hillclimber` is an answer to a question that seems simple on the surface: how do I bring my train up this slope? While we don't deal with the question of how the track is laid out, once the track is laid, we can determine how to split up a train to make the climb.

As an example, consider a Heisler pulling 5 cars of rails, 5 cars of beams, and a caboose.

    In [1]: import railroads_hillclimber
    
    In [2]: from railroads_hillclimber.prefab import *
    
    In [3]: train = (
       ...:     heisler()
       ...:     + 5 * flatcar_stakes(name='Rails', cargo=cargo.rails)
       ...:     + 5 * flatcar_stakes(name='Beams', cargo=cargo.beams)
       ...:     + caboose()
       ...: )

How steep can we climb at 95% throttle?

    In [4]: train.maximum_grade(power_ratio=0.95)
    Out[4]: 0.03634838508605576

If we need to climb up a 7% grade to get to the iron mine, how do we split up the train?

    In [5]: railroads_hillclimber.compute_climb(train, grade=0.07, power_ratio=0.95)
    Out[5]:
    [(Train((<TractiveCar Heisler>, <Car Rails>, <Car Rails>, <Car Rails>)),
      Train((<TractiveCar Heisler>,))),
     (Train((<TractiveCar Heisler>, <Car Rails>, <Car Rails>, <Car Beams>, <Car Beams>)),
      Train((<TractiveCar Heisler>,))),
     (Train((<TractiveCar Heisler>, <Car Beams>, <Car Beams>, <Car Beams>, <Car Bobber Caboose>)),
      None)]

Note this supports grouping the power together to handle later cars in the consist. If we had another Heisler between the cuts of cars, but twice as many cars, what then?

    In [8]: train = (
       ...:     heisler()
       ...:     + 10 * flatcar_stakes(name='Rails', cargo=cargo.rails)
       ...:     + heisler()
       ...:     + 10 * flatcar_stakes(name='Beams', cargo=cargo.beams)
       ...:     + caboose()
       ...: )
    
    In [9]: railroads_hillclimber.compute_climb(train, grade=0.07, power_ratio=0.95)
    Out[9]:
    [(Train((<TractiveCar Heisler>, <Car Rails>, <Car Rails>, <Car Rails>)),
      Train((<TractiveCar Heisler>,))),
     (Train((<TractiveCar Heisler>, <Car Rails>, <Car Rails>, <Car Rails>, <Car Rails>, <Car Rails>, <Car Rails>, <Car Rails>, <TractiveCar Heisler>)),
      Train((<TractiveCar Heisler>, <TractiveCar Heisler>))),
     (Train((<TractiveCar Heisler>, <TractiveCar Heisler>, <Car Beams>, <Car Beams>, <Car Beams>, <Car Beams>, <Car Beams>)),
      Train((<TractiveCar Heisler>, <TractiveCar Heisler>))),
     (Train((<TractiveCar Heisler>, <TractiveCar Heisler>, <Car Beams>, <Car Beams>, <Car Beams>, <Car Beams>, <Car Beams>, <Car Bobber Caboose>)),
      None)]

Note that after we bring the second Heisler to the top of the grade, it's available for bringing up the beams as well.
