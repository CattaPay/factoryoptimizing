

from utils import *

## resource inputs
# impure, normal, pure
resource_nodes = {"Iron Ore": [39, 42, 46],
                  "Copper Ore": [13,29,13],
                  "Caterium Ore": [0, 9, 8],
                  "Limestone": [15, 50, 29],
                  "Coal": [15, 31, 16],
                  "Raw Quartz": [3,7,7],
                  "Sulfur": [6,5,5],
                  "Bauxite": [5,6,6],
                  "Uranium": [3,2,0],
                  "SAM": [10,6,3]}

# impure, normal, pure
oil_nodes = [10,12,8]

# [number of nodes, impure, normal, pure]
fracking_nodes = {"Crude Oil": [3, 8, 6, 4],
                  "Nitrogen Gas": [6, 2, 7, 36]}

# impure, normal, pure
geysers = [9, 13, 9]


### impure nodes
impure_nodes = {"Iron Ore": [127,0,0],
                  "Copper Ore": [55,0,0],
                  "Caterium Ore": [17,0,0],
                  "Limestone": [94,0,0],
                  "Coal": [62,0,0],
                  "Raw Quartz": [17,0,0],
                  "Sulfur": [16,0,0],
                  "Bauxite": [17,0,0],
                  "Uranium": [5,0,0],
                  "SAM": [19,0,0]}

impure_oil = [30,0,0]

impure_fracking = {"Crude Oil": [3, 18, 0, 0],
                  "Nitrogen Gas": [6, 45, 0, 0]}

impure_geysers = [31, 0, 0]


### pure nodes
pure_nodes = {"Iron Ore": [0,0,127],
                  "Copper Ore": [0,0,55],
                  "Caterium Ore": [0,0,17],
                  "Limestone": [0,0,94],
                  "Coal": [0,0,62],
                  "Raw Quartz": [0,0,17],
                  "Sulfur": [0,0,16],
                  "Bauxite": [0,0,17],
                  "Uranium": [0,0,5],
                  "SAM": [0,0,19]}

pure_oil = [0,0,30]

pure_fracking = {"Crude Oil": [3, 0, 0, 18],
                  "Nitrogen Gas": [6, 0, 0, 45]}

pure_geysers = [0, 0, 31]


## funny settings
force_overclock = True # ensures that all machines are overclocked

#
max_sloops = 104

# new settings
recipe_ingredient_factor = 1
power_use_factor = 1

# excess power
power_excess = 50000

### check all combos

def checkAllCombos(n_augmenters,
                    powered_augmenters,
                    resource_nodes,
                    oil_nodes,
                    fracking_nodes,
                    geysers,
                    max_sloops,
                    recipe_ingredient_factor,
                    power_use_factor,
                    force_overclock):
    score_table = {}
    for n_augmenters in range(11):
        for powered_augmenters in range(n_augmenters + 1):

            res, recipe_matrix, recipe_order_full, base_score = checkAugmenters(n_augmenters,
                                                                                powered_augmenters,
                                                                                resource_nodes,
                                                                                oil_nodes,
                                                                                fracking_nodes,
                                                                                geysers,
                                                                                max_sloops,
                                                                                recipe_ingredient_factor,
                                                                                power_use_factor,
                                                                                force_overclock)

            score_table[(n_augmenters, powered_augmenters)] = -res["fun"] - base_score

            # print((n_augmenters, powered_augmenters), -res["fun"] - base_score)


    max_augs = max(score_table, key = score_table.get)
    return max_augs

# n_augmenters, powered_augmenters = (0,0)


n_augmenters, powered_augmenters = (0,0)

out = checkAugmenters(n_augmenters,
                        powered_augmenters,
                        resource_nodes,
                        oil_nodes,
                        fracking_nodes,
                        geysers,
                        max_sloops,
                        recipe_ingredient_factor,
                        power_use_factor,
                        force_overclock,
                        power_excess = power_excess)

res, recipe_matrix, recipe_order_full, base_score, item_df = out

# print(recipe_order_full)
# print(len(res["x"]))

# print(item_df)
# print(out)
def outputData(out, itemsPath = "results/items.csv", recipesPath = "results/recipes.csv", usefulPath = "results/useful.csv"):
    res, recipe_matrix, recipe_order_full, base_score, item_df = out
    recipes_used = res["x"]
    items_ended = recipe_matrix.T @ recipes_used

    power_use = np.multiply(recipes_used, recipe_matrix[:,-2])
    # print(power_use)

    # value = np.dot(items_ended, item_values)
    # print(value)

    recipe_output = []
    items_output = item_info.drop(["GameName", "Form", "Destroyable", "SinkPoints"], axis = 1)
    items_output.loc[len(items_output)] = {"Name": "Power", "SinkPoints": 0}
    items_output.loc[len(items_output)] = {"Name": "Sloop", "SinkPoints": 0}

    items_output["Amount_Sunk"] = items_ended

    running_count = 0

    recipe_order_full["Count"] = recipes_used
    recipe_order_full["Power Used"] = power_use

    # drop any zeros
    recipe_order_full = recipe_order_full[recipe_order_full["Count"] >= 1e-8]

    items_output.to_csv(itemsPath, index = False)
    recipe_order_full.to_csv(recipesPath, index = False)
    item_df.to_csv(usefulPath, index = False)

    return res["fun"] + base_score


# print(all_recipes)

print(outputData(out))