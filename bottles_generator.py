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

def get_ingredient_examples():
	examples = []
	with open(util.resource_path("data/ingredient_examples.txt"), "r") as file:
		lines = file.readlines()
		for line in lines:
			examples.append(line.strip().capitalize())
	return examples

def get_effect_topics():
	topics = []
	with open(util.resource_path("data/effect_topics2.txt"), "r") as file:
		lines = file.readlines()
		for line in lines:
			line = line.strip()
			topics.append(line)
	return topics

def get_potion_name_examples():
	examples = []
	with open(util.resource_path("data/potion_name_examples.txt"), "r") as file:
		lines = file.readlines()
		for line in lines:
			examples.append("Potion of " + line.strip())
	return examples

async def generate_ingredient_defs():
	await asyncio.sleep(1)
	if use_dummy_ingredient_data:
		with open(dummy_ingredient_data_path, "rb") as file:
			defs = pickle.load(file)
			await asyncio.sleep(1)
			return defs
		
	examples = get_ingredient_examples()
	# examples = random.sample(examples, k=5)
	ex_embeddings_list = gen.create_embeddings(examples)
	ex_embeddings = {examples[i]: embedding for i, embedding in enumerate(ex_embeddings_list)}

	topics = get_effect_topics()
	topic_embeddings_list = gen.create_embeddings(topics)
	topic_embeddings = {topics[i]: embedding for i, embedding in enumerate(topic_embeddings_list)}

	comps = []
	for example in examples:
		ee = ex_embeddings[example]
		for i in range(len(topics)):
			topic = topics[i]
			te = topic_embeddings[topic]
			similarity = gen.compare_embeddings(te, ee)
			comps.append((example, topic, similarity))
	
	comps = sorted(comps, key=lambda x: x[2], reverse=True)
	ex_topics = {}
	while len(ex_topics) < len(examples):
		seen_topics = set()
		for comp in comps:
			ex = comp[0]
			topic = comp[1]
			if ex in ex_topics or topic in seen_topics:
				continue

			ex_topics[ex] = topic
			seen_topics.add(topic)

	defs = []
	options = gen.Options(
		temperature=0.1,
	)
	for example, topic in ex_topics.items():
		desc_prompt = f"Write a short one sentence description of the fictional magic potion ingredient \"{example}\". Give the impression that it is associated with {topic} magic without saying so directly."
		desc, elapsed = await generator.generate(desc_prompt, options)
		ing = itm.IngredientDef(example, desc=desc, cost=random.randint(2, 10), shop_weight=1)
		ing.affinity = topic
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
	
	ingredients_str = "".join(f"- {ing.name} (affinity for {ing.affinity} magic): {ing.desc}\n" for ing in ingredients)
	desc_prompt = f"{ingredients_str}Imagine a fictional magic potion with the above ingredients. It should have a single effect. Describe it in one short sentence."
	options = gen.Options(
		seed=seed,
		temperature=0.01,
	)
	desc, elapsed = await generator.generate(desc_prompt, options)
	
	name_prompt = f"Generate a simple name for a potion with the following description. Provide only the name and only one name. It should be of the form \"Potion of...\" and should simply describe what the potion does, for example \"Potion of Invisibility\".\n{desc}"
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
		top_p=1.0,
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