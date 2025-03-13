import generator as gen
from generator import Generator
from item import IngredientDef, Ingredient, Request, Bottle
import pickle
from typing import List
import asyncio

use_dummy_data = False
write_dummy_data = False
dummy_data_path = "dummy_data/dummy_data.pkl"

def generate_ingredient_defs():
	if use_dummy_data:
		with open(dummy_data_path, "rb") as file:
			defs = pickle.load(file)

	defs = [
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

	if write_dummy_data:
		with open(dummy_data_path, "wb") as file:
			pickle.dump(defs, file)

	return defs

async def generate_potion(ingredients: List[Ingredient]):
	if use_dummy_data:
		await asyncio.sleep(3)
		return "Elixir of Life", "Heals any wound!"
	
	options = Generator.Options(
		temperature=0.01,
		seed = 42,
	)
	
	ingredient_list = "".join(f"- {ingredient.name}\n" for ingredient in ingredients)
	desc_prompt = f"{ingredient_list}Write a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book."
	desc, elapsed = await generator.generate(desc_prompt, options)
	
	name_prompt = f"Generate a name for a magical potion. Provide only the name and only one name. It could be a Potion, Elixir, Draught, Tonic... The name should describe the effects of the potion which are as follows:\n{desc}"
	options.temperature = 1.0
	options.top_p = 20.0
	name, elapsed = await generator.generate(name_prompt, options)

	return name, desc

def generate_request():
	request = Request("Emma")
	request.desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
	return request

def generate_request_response(request_desc, potion: Bottle):
	return "\"That worked great!\""

generator = gen.create_generator()