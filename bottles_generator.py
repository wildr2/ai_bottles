from __future__ import annotations
import random
import pickle
from typing import List
import asyncio
import generator as gen
import item as itm
import util

use_dummy_ingredient_data = True
use_dummy_potion_data = False
use_dummy_request_data = False
write_dummy_ingredient_data = False
dummy_ingredient_data_path = util.resource_path("data/dummy_ingredient_data.pkl")

async def generate_ingredient_defs():
	await asyncio.sleep(1)
	if use_dummy_ingredient_data:
		with open(dummy_ingredient_data_path, "rb") as file:
			defs = pickle.load(file)
			await asyncio.sleep(1)
			return defs

	examples = []
	with open("ingredient_examples.txt", "r") as file:
		lines = file.readlines()
		for line in lines:
			examples.append(line.strip().capitalize())
	
	defs = []
	options = gen.Options(
		temperature=0.1,
	)
	for example in examples:
		desc_prompt = f"Generate a one sentence description for a potion ingredient named \"{example}\"."
		desc, elapsed = await generator.generate(desc_prompt, options)
		ing = itm.IngredientDef(example, desc=desc, cost=random.randint(2, 10), shop_weight=1)
		defs.append(ing)

	if write_dummy_ingredient_data:
		with open(dummy_ingredient_data_path, "wb") as file:
			pickle.dump(defs, file)

	return defs

async def generate_potion(ingredients: List[itm.Ingredient]):
	if use_dummy_potion_data:
		await asyncio.sleep(3)
		return "Elixir of Life", "Heals any wound!"
	
	seed = 42
	
	ingredients_str = "".join(f"- {ing.desc}\n" for ing in ingredients)
	desc_prompt = f"{ingredients_str}Write a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book."
	options = gen.Options(
		seed=seed,
		temperature=0.5,
	)
	desc, elapsed = await generator.generate(desc_prompt, options)
	
	name_prompt = f"Generate a name for a magical potion. Provide only the name and only one name. It should be of the form \"Potion of...\". The name should describe the effects of the potion which are as follows:\n{desc}"
	options = gen.Options(
		seed=seed,
		temperature=1.0,
	)
	name, elapsed = await generator.generate(name_prompt, options)

	return name, desc

async def generate_request():
	if use_dummy_request_data:
		await asyncio.sleep(3)
		request = itm.Request("Emma")
		request.desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
		return request
	
	
	desc_prompt = "You are a customer at a magic shop in a fantasy land. In one sentence, describe the problem you are trying to solve, for which you are seeking a magical solution (for example perhaps you are about to attempt to fight a dragon, or perhaps it is taking too long to paint your house). Don't mention what you want (e.g. a spell or a potion), and don't prescribe the solution, just describe your problem."
	options = gen.Options(
		temperature=1.0,
	)
	desc, elapsed = await generator.generate(desc_prompt, options)

	name_prompt = "Give me a first name for a fictional character. Respond with the name only."
	options = gen.Options(
		temperature=1.0,
	)
	name, elapsed = await generator.generate(name_prompt, options)

	request = itm.Request(name)
	request.desc = f"\"{desc}\""
	return request

async def generate_request_outcome(request_desc, potion_desc):
	if use_dummy_request_data:
		await asyncio.sleep(3)
		return "\"That worked great!\"", True

	predict_prompt = f"Sam: {request_desc}\nPredict what will happen when Sam attempts to solve their problem using the following magic potion. Will the potion help to resolve the problem? Answer simply yes or no.\n\"{potion_desc}\""
	options = gen.Options(
		temperature=0.01,
	)
	prediction, elapsed = await generator.generate(predict_prompt, options)
	outcome_success = "yes" in prediction.lower()
	
	outcome_desc_prompt = f"Sam: {request_desc}\nSam {'successfully resolved' if outcome_success else 'failed to resolve'} their problem using the following potion:\n\"{potion_desc}\"\nRole-playing as Sam, in one short sentence and using past tense, relate what happened."
	options = gen.Options(
		temperature=0.01,
	)
	outcome_desc, elapsed = await generator.generate(outcome_desc_prompt, options)

	return outcome_desc, outcome_success

generator = gen.create_generator()