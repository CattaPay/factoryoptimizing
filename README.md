# Satisfactory Optimizing

This project uses linear programming to optimize the use of resources in a Satisfactory world. Specifically, 
it maximizes the sink points per minute that can be produced indefinitely. The 1.2 update introduced settings that allow 
for the randomization of nodes, scaling of recipe ingredients, and scaling power use. These have been implemented here. 
Additionally, alien power augmenters can be included, either unpowered or powered. 

### Files
- utils.py: contains the functions that compute optimal solutions
- calculations.py: calls the functions in utils.py with given settings

### Settings
The following settings can be adjusted to 
- nodes: the number of impure, normal, and pure nodes of each type (
- max_sloops: the number of usable somersloops (two ignored for research)
- recipe_ingredient_factor: new setting that scales recipe difficulty
- power_use_factor: new setting that scales power used by machines
- power_excess: amount of excess power to generate (for trains, hoverpacks, and such)
- force_overclock: ensures all machines are overclocked
