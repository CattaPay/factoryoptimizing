
import json
import numpy as np
import pandas as pd
from scipy.optimize import linprog, Bounds, milp, LinearConstraint


with open("data/en-CA.json", "r", encoding = "utf-16") as f:
    dat = json.load(f)

# for i in range(len(dat)):
#     print(i, dat[i]["NativeClass"])

## get items
all_items = []

# all items
item_dat = dat[0]["Classes"]
resource_dat = dat[1]["Classes"]
bio_dat = dat[9]["Classes"]
ammo_dat = dat[14]["Classes"]
ammo2_dat = dat[18]["Classes"]
ammo3_dat = dat[19]["Classes"]
nuclear_dat = dat[61]["Classes"]
powershard_dat = dat[79]["Classes"]
equipment_dat = dat[6]["Classes"] # included for portable miner
matrix_dat = dat[98]["Classes"] # included for  alien power matrix

all_item_dat = item_dat + resource_dat + bio_dat + ammo_dat + ammo2_dat + ammo3_dat + nuclear_dat + powershard_dat + equipment_dat + matrix_dat

for item in all_item_dat:
    current_item = []
    current_item.append(item["mDisplayName"])
    current_item.append(item["ClassName"])
    current_item.append(item["mCanBeDiscarded"])
    current_item.append(item["mForm"])

    if "mResourceSinkPoints" in item.keys():
        current_item.append(item["mResourceSinkPoints"])
    else:
        current_item.append(0)

    all_items.append(current_item)

item_info = pd.DataFrame(all_items, columns = ["Name", "GameName", "Destroyable", "Form", "SinkPoints"])


## get buildings
all_buildings = []

# basic
building_dat = dat[41]["Classes"]

for building in building_dat:
    current_building = []
    current_building.append(building["mDisplayName"])
    current_building.append(building["ClassName"])
    current_building.append(building["mPowerConsumption"])
    current_building.append(building["mProductionShardSlotSize"])
    # current_building.append(building["mProductionBoostPowerConsumptionExponent"])

    all_buildings.append(current_building)


# variable power
variable_dat = dat[77]["Classes"]
# print(variable_dat[0].keys())
for building in variable_dat:
    current_building = []
    current_building.append(building["mDisplayName"])
    current_building.append(building["ClassName"])

    # take power as the average of the max and min

    min_power = building["mEstimatedMininumPowerConsumption"]
    max_power = building["mEstimatedMaximumPowerConsumption"]
    current_building.append(0)
    current_building.append(building["mProductionShardSlotSize"])

    all_buildings.append(current_building)


building_info = pd.DataFrame(all_buildings, columns = ["Name", "GameName", "PowerUse", "SloopSlots"])


## get recipes
recipe_dat = dat[3]["Classes"]

# gets the materials or output in usable format
def getIngredients(ingredients):
    split_ingredients = ingredients.split(",")
    current_ingredients = []
    for i in range(len(split_ingredients) // 2):
        item_bits = split_ingredients[i * 2].split(".")
        item_name = item_bits[-1].strip('\'"')

        amount_bits = split_ingredients[i * 2 + 1].split("=")
        amount = int(amount_bits[-1].strip('\'"()'))

        current_ingredients.append([item_name, amount])

    return current_ingredients
    
all_recipes = []
for recipe in recipe_dat:

    current_recipe = []
    current_recipe.append(recipe["mDisplayName"])
    current_recipe.append(recipe["ClassName"])
    current_recipe.append(recipe["mManufactoringDuration"])

    # machines
    machines = recipe["mProducedIn"].split(",")
    automachines = []
    for machine in machines:
        full = machine.split(".")
        short = full[-1].replace('"', '').strip("()")
        if (building_info['GameName'] == short).any():
            automachines.append(short)

    if len(automachines) == 1:
        current_recipe.append(automachines[0])

        # ingredients
        ingredients = recipe["mIngredients"]
        current_ingredients = getIngredients(ingredients)

        current_recipe.append(current_ingredients)

        # product
        product = recipe["mProduct"]
        current_product = getIngredients(product)

        current_recipe.append(current_product)

        if "mVariablePowerConsumptionConstant" in recipe.keys():
            base_power = float(recipe["mVariablePowerConsumptionConstant"])
            var_power = float(recipe["mVariablePowerConsumptionFactor"])
            power = base_power + var_power / 2
        else:
            power = 0

        current_recipe.append(power)

        all_recipes.append(current_recipe)


## list of all power stations and their specs...
power_stations =   [["Coal-Powered Generator - Coal", [["Desc_Coal_C", 15], ["Desc_Water_C", 45000]], [], 75, "Coal-Powered Generator"],
                    ["Coal-Powered Generator - Coal", [["Desc_Coal_C", 15], ["Desc_Water_C", 45000]], [], 75, "Coal-Powered Generator"],
                    ["Coal-Powered Generator - Compacted Coal", [["Desc_CompactedCoal_C", 7.142857], ["Desc_Water_C", 45000]], [], 75, "Coal-Powered Generator"],
                    ["Coal-Powered Generator - Petroleum Coke", [["Desc_PetroleumCoke_C", 25], ["Desc_Water_C", 45000]], [], 75, "Coal-Powered Generator"],
                    ["Fuel-Powered Generator - Fuel", [["Desc_LiquidFuel_C", 20000]], [], 250, "Fuel-Powered Generator"],
                    ["Fuel-Powered Generator - Turbofuel", [["Desc_LiquidTurboFuel_C", 7500]], [], 250, "Fuel-Powered Generator"],
                    ["Fuel-Powered Generator - Liquid BioFuel", [["Desc_LiquidBiofuel_C", 20000]], [], 250, "Fuel-Powered Generator"],
                    ["Fuel-Powered Generator - Rocket Fuel", [["Desc_RocketFuel_C", 4166.666666]], [], 250, "Fuel-Powered Generator"],
                    ["Fuel-Powered Generator - Ionized Fuel", [["Desc_IonizedFuel_C", 3000]], [], 250, "Fuel-Powered Generator"],
                    ["Nuclear Power Plant - Uranium", [["Desc_NuclearFuelRod_C", 0.2], ["Desc_Water_C", 240000]], [["Desc_NuclearWaste_C", 10]], 2500, "Nuclear Power Plant"],
                    ["Nuclear Power Plant - Plutonium", [["Desc_PlutoniumFuelRod_C", 0.1], ["Desc_Water_C", 240000]], [["Desc_PlutoniumWaste_C", 1]], 2500, "Nuclear Power Plant"],
                    ["Nuclear Power Plant - Ficsonium", [["Desc_FicsoniumFuelRod_C", 1], ["Desc_Water_C", 240000]], [], 2500, "Nuclear Power Plant"]]

## list of all extractors and their specs
# will maybe expand to include miners... but is there ever a situation where it's optimal to miss some resources?
extractors = [["Water Extractor", [["Desc_Water_C", 120000]], 20, "Water Extractor"]]


def getIngredientCount(count, factor):
    val = np.round(count * factor, 0)
    if val < 1:
        val = 1
    return val

### algorithm

def runProgram(resource_nodes,
               oil_nodes,
               fracking_nodes,
               geysers,
               additional_items = {},
               bonus_power = 0,
               augmenter_factor = 1,
               max_sloops = 104,
               recipe_ingredient_factor = 1,
               power_use_factor = 1,
               force_overclock = False):

    ## get recipe and item indices
    M = item_info.shape[0] # number of items
    N = len(all_recipes) + len(extractors) +len(power_stations) # number of recipes + power stations

    # print(N, M)
    overclock_factor = 2.5 ** 1.321928

    # initialize matrix
    # extra spot for power
    # extra spot for sloops
    # start with it way too big then cut down later
    recipe_matrix = np.zeros(shape = (10*N, M + 2))

    running_count = 0 # keeps track of the matrix rows

    # print(all_recipes[0][3])
    # build matrix for recipes
    # currently ignoring, sloops, etc.

    recipe_order_info = []

    dummy_pairs = [] # pairs of normal, dummy variable indices, with dummies the integer greater than normal

    for i in range(len(all_recipes)):
        recipe = all_recipes[i]
        machine_id = recipe[3]

        possible_sloops = int(building_info[building_info["GameName"] == machine_id]["SloopSlots"].item())
        building_name = building_info[building_info["GameName"] == machine_id]["Name"].item()
        prod_per_minute = 60 / float(recipe[2])
        ingredients = recipe[4]
        products = recipe[5]

        sloop_factor = 1
        item_multiplier = 1
        overclock_power_factor = 1

        for sloops in range(possible_sloops + 1):
            if force_overclock or sloops > 0:
                item_multiplier = 2.5
                overclock_power_factor = overclock_factor

            if sloops > 0:
                sloop_factor = 1 + sloops / possible_sloops

            power_multiplier = sloop_factor ** 2 * overclock_power_factor
        
            for item, amount in ingredients:

                item_index = item_info.index[item_info["GameName"] == item]

                # fuck with amounts here for the new settings
                # don't change amount if it's a packager recipe
                if machine_id == "Build_Packager_C":
                    new_amount = amount
                else:
                    new_amount = getIngredientCount(amount, recipe_ingredient_factor)

                per_minute = prod_per_minute * new_amount * item_multiplier

                # negative for ingredients
                recipe_matrix[running_count, item_index] = -per_minute

            for item, amount in products:

                item_index = item_info.index[item_info["GameName"] == item]

                # fuck with amounts here for the new settings
                per_minute = prod_per_minute * amount * sloop_factor * item_multiplier # included sloop factor

                # positive for products
                recipe_matrix[running_count, item_index] += per_minute

        
            machine_power = float(building_info[building_info["GameName"] == machine_id]["PowerUse"].item())
            if machine_power == 0:
                power = recipe[6]
            else:
                power = machine_power

            power *= power_multiplier * power_use_factor # included sloop factor

            # add to recipe thing
            recipe.append(power)
            # negative as it's used up
            recipe_matrix[running_count, M] = -float(power)

            # # add sloops used
            # recipe_matrix[running_count, M + 1] = -sloops

            # update count
            running_count += 1

            # add to recipe order info
            if sloops == 0:
                recipe_name = recipe[0]
            else:
                recipe_name = recipe[0] + "_" + str(sloops)
                
            recipe_order_info.append([recipe_name, building_name])

            # if it contains a sloop, add dummy integer that is greater than it
            if sloops > 0:
                recipe_matrix[running_count, M + 1] = -sloops
                recipe_order_info.append([recipe_name + "_dummy", "NA"])
                dummy_pairs.append([running_count-1, running_count])
                running_count += 1

    ## add to matrix for extractors
    for i in range(len(extractors)):
        overclock_power_factor = 1
        item_multiplier = 1
        if force_overclock:
            item_multiplier = 2.5
            overclock_power_factor = overclock_factor

        extractor_specs = extractors[i]
        matrix_row = i + running_count

        products = extractor_specs[1]
        for item, amount in products:
            item_index = item_info.index[item_info["GameName"] == item]
            per_minute = amount

            # positive for products
            recipe_matrix[matrix_row, item_index] = per_minute * item_multiplier

        power = extractor_specs[2] * overclock_power_factor
        recipe_matrix[matrix_row, M] = -float(power)

        recipe_order_info.append([extractor_specs[0], "NA"])

    running_count += len(extractors)

    ## add to matrix for power stations
    for i in range(len(power_stations)):

        # can overclock power stations with no consequence

        power_specs = power_stations[i]
        matrix_row = i + running_count

        ingredients = power_specs[1]
        for item, amount in ingredients:
            item_index = item_info.index[item_info["GameName"] == item]
            per_minute = amount

            # negative for ingredients
            recipe_matrix[matrix_row, item_index] = -per_minute * 2.5

        products = power_specs[2]
        for item, amount in products:
            item_index = item_info.index[item_info["GameName"] == item]
            per_minute = amount

            # positive for products
            recipe_matrix[matrix_row, item_index] = per_minute * 2.5

        power = power_specs[3] * 2.5 * augmenter_factor
        recipe_matrix[matrix_row, M] = float(power)

        recipe_order_info.append([power_specs[0], "NA"])

    running_count += len(power_stations)
    # print(running_count)

    recipe_order_full = pd.DataFrame(recipe_order_info, columns = ["Name", "Building"])

    recipe_matrix = recipe_matrix[0:running_count,:] # pare down the matrix to what was actually used
    # print(recipe_matrix[:,M])
        

    # print(item_info)
    # fix sink points
    item_info["TrueSinkPoints"] = item_info.apply(lambda x: (x.Form == "RF_SOLID") * int(x.SinkPoints), axis = 1)
    item_values = np.array(item_info["TrueSinkPoints"]).astype(int)
    item_values = np.append(item_values, [0, 0]) # 

    # print(item_values)
    # objective function by recipe
    objective = -recipe_matrix @ item_values

    # constraint matrix

    # recipe_matrix' @ x >= vector of zeros (with resources at the negative of their actual values)
    # take the negative of both sides
    constraint = -recipe_matrix.T

    # add dummy constraints and integrality
    integrality = np.zeros(shape = (running_count))
    dummy_constraints = np.zeros(shape = (len(dummy_pairs), constraint.shape[1]))
    count = 0
    for real, dummy in dummy_pairs:
        dummy_constraints[count, real] = 1
        dummy_constraints[count, dummy] = -1

        integrality[dummy] = 1

        count += 1

    full_constraint = np.concat([constraint, dummy_constraints])
    # dummy_constraints = 


    miner_power = 0
    start_resources = {}
    for res in resource_nodes:
        start_resources[res] = np.dot(resource_nodes[res], [300, 600, 1200])
        power = 45 * sum(resource_nodes[res])
        miner_power -= power

    for res in fracking_nodes:
        start_resources[res] = np.dot(fracking_nodes[res], [0, 75000, 150000, 300000])
        power = 150 * fracking_nodes[res][0]
        miner_power -= power

    start_resources["Crude Oil"] += np.dot(oil_nodes, [150000, 300000, 600000])
    miner_power -= sum(oil_nodes) * 40

    # increase power due to overclocking miners
    miner_power *= (2.5 ** 1.321928)

    # geyser power
    miner_power += np.dot(geysers, [100, 200, 400])

    # sink running
    start_power = miner_power - 30

    # add power from alien augmenters
    start_power += augmenter_factor * bonus_power

    start_resources = start_resources | additional_items

    # start_resources = {"Iron Ore": 92100,
    #                    "Caterium Ore": 15000,
    #                    "Copper Ore": 36900,
    #                    "Limestone": 69300,
    #                    "Coal": 42300,
    #                    "Raw Quartz": 13500,
    #                    "Sulfur": 10800,
    #                    "Uranium": 2100,
    #                    "Bauxite": 12300,
    #                    "SAM": 10800,
    #                    "Nitrogen Gas": 12000 * 1000,
    #                    "Crude Oil": 12600 * 1000,


    # start_resources["Alien Power Matrix"] = -100

    start_resources
    base_score = 0
    for res in start_resources:
        points = item_info[item_info["Name"] == res]["TrueSinkPoints"].item()
        val = start_resources[res]
        base_score -= val * points

    upper_bound = np.zeros(shape = (full_constraint.shape[0]))

    for item in start_resources:
        item_index = int(item_info.index[item_info["Name"] == item][0])
        upper_bound[item_index] = start_resources[item]

    upper_bound[M] = start_power
    upper_bound[M+1] = max_sloops

    can_sink = item_info.apply(lambda x: x.Destroyable == "True" and x.Form == "RF_SOLID", axis = 1)
    # print(can_sink)

    lower_bound = np.full(shape = (full_constraint.shape[0]), fill_value = -np.inf)
    for i in range(len(can_sink)):
        if not can_sink[i]:
            lower_bound[i] = 0

    # print(lower_bound)


    # print(upper_bound)


    # res = linprog(c = objective, 
    #               A_ub = full_constraint,
    #               b_ub = upper_bound)

    res = milp(c = objective,
            constraints=LinearConstraint(full_constraint, ub = upper_bound, lb = lower_bound),
            integrality=integrality)
    return res, recipe_matrix, recipe_order_full, base_score


def runProgramNoDummy(resource_nodes,
               oil_nodes,
               fracking_nodes,
               geysers,
               additional_items = {},
               bonus_power = 0,
               augmenter_factor = 1,
               max_sloops = 104,
               recipe_ingredient_factor = 1,
               power_use_factor = 1,
               force_overclock = False,
               power_excess = 0):

    ## get recipe and item indices
    M = item_info.shape[0] # number of items
    N = len(all_recipes) + len(extractors) +len(power_stations) # number of recipes + power stations

    # print(N, M)
    overclock_factor = 2.5 ** 1.321928

    # initialize matrix
    # extra spot for power
    # extra spot for sloops
    # start with it way too big then cut down later
    recipe_matrix = np.zeros(shape = (10*N, M + 2))

    running_count = 0 # keeps track of the matrix rows

    # print(all_recipes[0][3])
    # build matrix for recipes
    # currently ignoring, sloops, etc.

    recipe_order_info = []

    force_integers = []

    for i in range(len(all_recipes)):
        recipe = all_recipes[i]
        machine_id = recipe[3]

        possible_sloops = int(building_info[building_info["GameName"] == machine_id]["SloopSlots"].item())
        building_name = building_info[building_info["GameName"] == machine_id]["Name"].item()
        prod_per_minute = 60 / float(recipe[2])
        ingredients = recipe[4]
        products = recipe[5]

        sloop_factor = 1
        item_multiplier = 1
        overclock_power_factor = 1

        for sloops in range(possible_sloops + 1):
            if force_overclock or sloops > 0:
                item_multiplier = 2.5
                overclock_power_factor = overclock_factor

            if sloops > 0:
                sloop_factor = 1 + sloops / possible_sloops

            power_multiplier = sloop_factor ** 2 * overclock_power_factor
        
            for item, amount in ingredients:

                item_index = item_info.index[item_info["GameName"] == item]

                # fuck with amounts here for the new settings
                # don't change amount if it's a packager recipe
                if machine_id == "Build_Packager_C":
                    new_amount = amount
                else:
                    new_amount = getIngredientCount(amount, recipe_ingredient_factor)

                per_minute = prod_per_minute * new_amount * item_multiplier

                # negative for ingredients
                recipe_matrix[running_count, item_index] = -per_minute

            for item, amount in products:

                item_index = item_info.index[item_info["GameName"] == item]

                # fuck with amounts here for the new settings
                per_minute = prod_per_minute * amount * sloop_factor * item_multiplier # included sloop factor

                # positive for products
                recipe_matrix[running_count, item_index] += per_minute

        
            machine_power = float(building_info[building_info["GameName"] == machine_id]["PowerUse"].item())
            if machine_power == 0:
                power = recipe[6]
            else:
                power = machine_power

            power *= power_multiplier * power_use_factor # included sloop factor

            # add to recipe thing
            recipe.append(power)
            # negative as it's used up
            recipe_matrix[running_count, M] = -float(power)

            # add sloops used
            recipe_matrix[running_count, M + 1] = -sloops
            if sloops >= 1:
                force_integers.append(running_count)

            # update count
            running_count += 1

            # add to recipe order info
            if sloops == 0:
                recipe_name = recipe[0]
            else:
                recipe_name = recipe[0] + "_" + str(sloops)
                
            recipe_order_info.append([recipe_name, building_name])

            

    ## add to matrix for extractors
    for i in range(len(extractors)):
        overclock_power_factor = 1
        item_multiplier = 1
        if force_overclock:
            item_multiplier = 2.5
            overclock_power_factor = overclock_factor

        extractor_specs = extractors[i]
        matrix_row = i + running_count

        products = extractor_specs[1]
        for item, amount in products:
            item_index = item_info.index[item_info["GameName"] == item]
            per_minute = amount

            # positive for products
            recipe_matrix[matrix_row, item_index] = per_minute * item_multiplier

        power = extractor_specs[2] * overclock_power_factor
        recipe_matrix[matrix_row, M] = -float(power)

        recipe_order_info.append([extractor_specs[0], extractor_specs[3]])

    running_count += len(extractors)

    ## add to matrix for power stations
    for i in range(len(power_stations)):

        # can overclock power stations with no consequence

        power_specs = power_stations[i]
        matrix_row = i + running_count

        ingredients = power_specs[1]
        for item, amount in ingredients:
            item_index = item_info.index[item_info["GameName"] == item]
            per_minute = amount

            # negative for ingredients
            recipe_matrix[matrix_row, item_index] = -per_minute * 2.5

        products = power_specs[2]
        for item, amount in products:
            item_index = item_info.index[item_info["GameName"] == item]
            per_minute = amount

            # positive for products
            recipe_matrix[matrix_row, item_index] = per_minute * 2.5

        power = power_specs[3] * 2.5 * augmenter_factor
        recipe_matrix[matrix_row, M] = float(power)

        recipe_order_info.append([power_specs[0], power_specs[4]])

    running_count += len(power_stations)
    # print(running_count)

    recipe_order_full = pd.DataFrame(recipe_order_info, columns = ["Name", "Building"])

    recipe_matrix = recipe_matrix[0:running_count,:] # pare down the matrix to what was actually used
    # print(recipe_matrix[:,M])
        

    # print(item_info)
    # fix sink points
    item_info["TrueSinkPoints"] = item_info.apply(lambda x: (x.Form == "RF_SOLID") * int(x.SinkPoints), axis = 1)
    item_values = np.array(item_info["TrueSinkPoints"]).astype(int)
    item_values = np.append(item_values, [0, 0]) # 

    # print(item_values)
    # objective function by recipe
    objective = -recipe_matrix @ item_values

    # constraint matrix

    # recipe_matrix' @ x >= vector of zeros (with resources at the negative of their actual values)
    # take the negative of both sides
    constraint = -recipe_matrix.T

    # add dummy constraints and integrality
    integrality = np.zeros(shape = (running_count))
    count = 0
    for ind in force_integers:
        integrality[ind] = 1
        count += 1

    full_constraint = constraint
    # dummy_constraints = 


    miner_power = 0
    start_resources = {}
    for res in resource_nodes:
        start_resources[res] = np.dot(resource_nodes[res], [300, 600, 1200])
        power = 45 * sum(resource_nodes[res])
        miner_power -= power

    for res in fracking_nodes:
        start_resources[res] = np.dot(fracking_nodes[res], [0, 75000, 150000, 300000])
        power = 150 * fracking_nodes[res][0]
        miner_power -= power

    start_resources["Crude Oil"] += np.dot(oil_nodes, [150000, 300000, 600000])
    miner_power -= sum(oil_nodes) * 40

    # increase power due to overclocking miners
    miner_power *= (2.5 ** 1.321928)

    # geyser power
    miner_power += np.dot(geysers, [100, 200, 400])

    # sink running
    start_power = miner_power - 30

    # add power from alien augmenters
    start_power += augmenter_factor * bonus_power

    start_resources = start_resources | additional_items

    # start_resources = {"Iron Ore": 92100,
    #                    "Caterium Ore": 15000,
    #                    "Copper Ore": 36900,
    #                    "Limestone": 69300,
    #                    "Coal": 42300,
    #                    "Raw Quartz": 13500,
    #                    "Sulfur": 10800,
    #                    "Uranium": 2100,
    #                    "Bauxite": 12300,
    #                    "SAM": 10800,
    #                    "Nitrogen Gas": 12000 * 1000,
    #                    "Crude Oil": 12600 * 1000,


    # start_resources["Alien Power Matrix"] = -100

    start_resources
    base_score = 0
    for res in start_resources:
        points = item_info[item_info["Name"] == res]["TrueSinkPoints"].item()
        val = start_resources[res]
        base_score -= val * points

    upper_bound = np.zeros(shape = (full_constraint.shape[0]))

    for item in start_resources:
        item_index = int(item_info.index[item_info["Name"] == item][0])
        upper_bound[item_index] = start_resources[item]

    upper_bound[M] = start_power - power_excess
    upper_bound[M+1] = max_sloops

    can_sink = item_info.apply(lambda x: x.Destroyable == "True" and x.Form == "RF_SOLID", axis = 1)
    # print(can_sink)

    lower_bound = np.full(shape = (full_constraint.shape[0]), fill_value = -np.inf)
    for i in range(len(can_sink)):
        if not can_sink[i]:
            lower_bound[i] = 0

    # print(lower_bound)


    # print(upper_bound)


    # res = linprog(c = objective, 
    #               A_ub = full_constraint,
    #               b_ub = upper_bound)

    res = milp(c = objective,
            constraints=LinearConstraint(full_constraint, ub = upper_bound, lb = lower_bound),
            integrality=integrality)

    ### create item directory
    item_dir = []
    for i in range(len(res["x"])):
        # if the result is non-zero, loop over the 
        n_machines = res["x"][i]
        if abs(n_machines) > 1e-10:
            # get recipe
            recipe_name = recipe_order_full["Name"][i]

            # item
            for j in range(M):
                if recipe_matrix[i,j] != 0:
                    # if item is in the recipe
                    item_name = item_info["Name"][j]
                    item_amount = recipe_matrix[i,j] 
                    scaled_amount = item_amount * n_machines

                    item_dir.append([recipe_name, n_machines, item_name, item_amount, scaled_amount])

            # power
            power_use = recipe_matrix[i,M]
            scaled_power = power_use * n_machines
            item_dir.append([recipe_name, n_machines, "Power", power_use, scaled_power])


    item_df = pd.DataFrame(item_dir, columns = ["Recipe", "Count", "Item", "Count per Recipe", "Item Count"])

    # columns should be recipe name, item, amt per recipe, number of recipe uses, amt total

    return res, recipe_matrix, recipe_order_full, base_score, item_df


def checkAugmenters(n_augmenters,
                    powered_augmenters,
                    resource_nodes,
                    oil_nodes,
                    fracking_nodes,
                    geysers,
                    max_sloops,
                    recipe_ingredient_factor = 1,
                    power_use_factor = 1,
                    force_overclock = False,
                    power_excess = 0): 
    bonus_power = n_augmenters * 500
    augmenter_factor = 1 + 0.1 * n_augmenters + 0.2 * powered_augmenters

    n_sloops = max_sloops - 1 - n_augmenters * 10
    if n_augmenters == 0:
        n_sloops += 1

    additional_items = {"Alien Power Matrix": -5 * powered_augmenters}

    out = runProgramNoDummy(resource_nodes,
                    oil_nodes,
                    fracking_nodes,
                    geysers,
                    additional_items,
                    bonus_power, 
                    augmenter_factor,
                    n_sloops,
                    recipe_ingredient_factor,
                    power_use_factor,
                force_overclock,
                power_excess)

    return out



# Ax <= b

# print(building_info)



#### TO DO LIST ####

# get 





# ## useful stuff
# for i in range(len(dat)):
#     print(i, dat[i]["NativeClass"])

# # check an index
# for i in dat[37]["Classes"]:
#     print(i["ClassName"])

