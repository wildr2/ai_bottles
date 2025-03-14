from __future__ import annotations
import generator as gen
import item as itm
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
		itm.IngredientDef("Violet", cost=3),			
		itm.IngredientDef("Dragonfly Wings", cost=10),
		itm.IngredientDef("Chlorabloom", cost=9),
		itm.IngredientDef("Glowstool", cost=5),
		itm.IngredientDef("Salt", cost=1),
		itm.IngredientDef("Pepper", cost=1),
		itm.IngredientDef("Red Berries", cost=3),
		itm.IngredientDef("Yellow Berries", cost=4),
		itm.IngredientDef("Ginger", cost=2),
		itm.IngredientDef("Garlic", cost=2),
		itm.IngredientDef("Fire Salts", cost=4),
		itm.IngredientDef("Chlorabloom", cost=9),
		itm.IngredientDef("Glowstool", cost=5),
	]

	if write_dummy_data:
		with open(dummy_data_path, "wb") as file:
			pickle.dump(defs, file)

	return defs

async def generate_potion(ingredients: List[itm.Ingredient]):
	if use_dummy_data:
		await asyncio.sleep(3)
		return "Elixir of Life", "Heals any wound!"
	
	options = gen.Options(
		seed = 42,
	)
	
	ingredient_list = "".join(f"- {ingredient.name}\n" for ingredient in ingredients)
	desc_prompt = f"{ingredient_list}Write a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book."
	options.temperature = 0.5
	desc, elapsed = await generator.generate(desc_prompt, options)
	
	name_prompt = f"Generate a name for a magical potion. Provide only the name and only one name. It should be of the form \"Potion of...\". The name should describe the effects of the potion which are as follows:\n{desc}"
	options.temperature = 1.0
	options.top_p = 20.0
	name, elapsed = await generator.generate(name_prompt, options)

	return name, desc

def generate_request():
	request = itm.Request("Emma")
	request.desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
	return request

async def generate_request_outcome(request_desc, potion_desc):
	if use_dummy_data:
		await asyncio.sleep(3)
		return "\"That worked great!\"", True

	options = gen.Options(
		seed = 42,
	)
	
	outcome_desc_prompt = f"Sam: {request_desc}\nDetermine what happens when Sam attempts to solve their problem using the following magic potion:\n\"{potion_desc}\"\nRole-playing as Sam, in one short sentence and using past tense, relate what happened."
	options.temperature = 0.5
	options.top_p = 20.0
	outcome_desc, elapsed = await generator.generate(outcome_desc_prompt, options)

	outcome_success_prompt = f"The problem: {request_desc}\nWhat happened next: {outcome_desc}\nWas the problem resolved? Reply with \"yes\" or \"no\"."
	options.temperature = 0.01
	options.top_p = None
	yes_no, elapsed = await generator.generate(outcome_success_prompt, options)
	outcome_success = "yes" in yes_no.lower()

	return outcome_desc, outcome_success

generator = gen.create_generator()