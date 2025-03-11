import generator as gen
from item import IngredientDef

use_dummy_data = False
dummy_data_path = "dummy_data/dummy_data.pkl"

prompt_fight = """{0}The above {1} characters will now be forced to fight to the death in the arena. Do not assume they are skilled fighters or that there abilities will be useful, rely only on the above descriptions. In present tense, give a very short account of what happens and who survives. Assume the reader is not familiar with the characters."""

# ingredient (name, desc, cost, properties)
# potion (name, desc)
# request (name, desc)

generator = gen.create_generator()

def generate_ingredient_defs():
	return [
		IngredientDef("Violet", cost=3),			
		IngredientDef("Dragonfly Wings", cost=10),
		IngredientDef("Chlorabloom", cost=9),
		IngredientDef("Glowstool", cost=5),
		IngredientDef("Salt", cost=1),
		IngredientDef("Pepper", cost=1),
		IngredientDef("Red Berries", cost=3),
		IngredientDef("Yellow Berries", cost=4),
		IngredientDef("Ginger", cost=2),
		IngredientDef("Garlic", cost=2),
		IngredientDef("Fire Salts", cost=4),
		IngredientDef("Chlorabloom", cost=9),
		IngredientDef("Glowstool", cost=5),
	]