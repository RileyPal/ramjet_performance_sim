# ramjet_performance_sim
# This is a simplified simulation for lifting body aircraft powered by RAM/SCRAM jet engines(super and hypersonic
# air breathing engine designs). The fact that these kinds of engines can achieve thrust outputs on par with traditional
# rocket propulsion technology while also not requiring onboard oxidizer makes them a possibly more efficient option for
# the ascent stage of a spacecraft's launch. The combined advantages of a lifting body aircraft's superior lift to drag
# ratio and the elimination of oxidizer needs on the ascent stage(the stage that chews up the majority of a traditional
# rocket's fuel and oxidizer) makes getting a payload up and out of the atmosphere a lot easier. It's genius really,
# when you consider the fact that atmospheric drag makes it so the longer a rocket stays in the atmosphere less and less
# payload could be put in orbit, meaning we opted for faster ascent stages to minimize time spent in the atmosphere. The
# problem there is drag scales quadratically with velocity meaning we get diminishing returns, so why not take advantage
# of the atmosphere, with air breathing engines like RAM and SCRAM jet engines we essentially turn that square term of
# drag into something closer to a power of 1.5 or maybe even lower since these engines allow us to get increasing
# output for every bit faster we go in the atmosphere.
#
# While I was unable to encapsulate the entirety of the nuance to this kind of engine, this is merely meant to be a
# way to visualize the viability and efficacy of such propulsion methods. In truth the biggest inaccuracy in terms of
# the simulation is my inability to model the effect of intake design on the efficiency of these engines, instead I
# opted to assume an ideal intake for the mass flow rate calculations. For this to be a valid approximation, aircraft
# in question would have to in some way have a variable intake design. i.e. The intakes structure would need to
# morph mid-flight in order to account for the differences in the fluid dynamics at higher mach numbers for this 
# simulation to be fully applicable. I can conceive of ways that would work, but practically I have never heard of 
# any such designs being used or even developed. 
