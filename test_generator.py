import random
import asyncio
import generator as gen
import bottles_generator as bg
import util

generator = gen.create_generator()


async def ingredient():
	examples = bg.get_ingredient_examples()
	examples = random.sample(examples, k=15)
	ex_embeddings_list = gen.create_embeddings(examples)
	ex_embeddings = {examples[i]: embedding for i, embedding in enumerate(ex_embeddings_list)}

	topics = bg.get_effect_topics()
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

			label = f"{ex}:"
			print(f"{label:<25}{topic:<15}")
			
	options = gen.Options(
		temperature=0.1,
	)
	for example, topic in ex_topics.items():
		desc_prompt = f"Write a short one sentence description of the fictional magic potion ingredient \"{example}\". Give the impression that it is associated with {topic} magic without saying so directly."
		desc, elapsed = await generator.generate(desc_prompt, options)
		print(f"- {desc}")
	

async def potion():
	ingredients = [
		"Crawler venom is a highly toxic, viscous liquid extracted from the fangs of giant, subterranean crawlers, known for its paralyzing and hallucinogenic effects.",
		"Copper dust is a finely ground, shimmering metallic powder, often used in potions for its conductive and transformative properties.",
		"Fresh moss is a vibrant, earthy ingredient, often used in potions for its rejuvenating and healing properties.",
		"Deer antler velvet is a soft, cartilaginous tissue found on the growing antlers of male deer, often used in traditional medicine for its purported health benefits.",
		"Flakes of pyrite are small, shiny, and brittle pieces of fool's gold, often used in potions for their reflective and heat-conducting properties.",
	]
	ingredients = bg.get_ingredient_examples()
	topics = bg.get_effect_topics()

	# chosen_ingredients = random.sample(ingredients, k=2)
	# for i in range(len(chosen_ingredients)):
	# 	topic = random.sample(topics, 1)[0]
	# 	chosen_ingredients[i] += f" (effect topic: {topic})"
	# ingredients_str = "".join(f"- {ing}\n" for ing in chosen_ingredients)
	# ingredients_str = "- Dragonfly Wings\n- Fire Salts\n"
	# ingredients_str = "- Black sand (affinity: darkness)\n- Crawler venom (affinity: barrier)"
	# ingredients_str = "- Dragonfly Wings (effect category: flight)\n- Fire Salts (effect category: transformation)\n"
	a = "Driftwood, weathered by time and tides, carries an ember-like essence within its grain."
	a_affinity = "Driftwood (affinity for fire magic): "
	b = "Sheep's wool, when harvested under a full moon, carries an ethereal softness that whispers of distant pastures."
	b_affinity = "Sheep's wool (affinity for animal magic): "
	ingredients_str = f"- {a_affinity}{a}\n- {b_affinity}{b}\n"
	print(ingredients_str)
	
	# potion_desc_prompt = f"{ingredients_str}\nWrite a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book."
	# potion_desc_prompt = f"{ingredients_str}Invent a creative magical effect for the potion brewed from the above ingredients. Write a short and snappy one sentence description of the potion."
	desc_prompt = f"{ingredients_str}Imagine a fictional magic potion with the above ingredients. It should have a single effect. Describe it in one short sentence."
	options = gen.Options(
		temperature=0.01,
	)
	desc, elapsed = await generator.generate(desc_prompt, options)
	# desc = "This potion grants the drinker the ability to glide through the air for a short duration."
	print(desc)

	# options = gen.Options(
	# 	temperature=1.0,
	# 	# top_p=20.0,
	# )
	# for i in range(1):
		# name_prompt = f"Generate a simple name for a magical potion with the following description. Provide only the name and only one name. It should be of the form \"Potion of...\".\n{desc}"
	# 	name, elapsed = await generator.generate(name_prompt, options)
	# 	print(name)

async def request_outcome():
	request_desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
	# potion_desc = "This potion grants the drinker the ability to glide through the air for a short duration."
	potion_desc = "This potion gives the drinker eyes in the back of their head for an hour."
	
	predict_prompt = f"Sam: {request_desc}\nPredict what will happen when Sam attempts to solve their problem using the following magic potion. Will the potion help to resolve the problem? Answer simply yes or no.\n\"{potion_desc}\""
	options = gen.Options(
		temperature=0.01,
	)
	# prediction, elapsed = await generator.generate(predict_prompt, options)
	prediction = "yes"
	print(prediction)
	outcome_success = "yes" in prediction.lower()

	outcome_desc_prompt = f"Sam: {request_desc}\nSam {'successfully resolved' if outcome_success else 'failed to resolve'} their problem using the following potion:\n\"{potion_desc}\"\nRole-playing as Sam, in one short sentence and using past tense, relate what happened."
	options = gen.Options(
		temperature=0.01,
		# temperature=0.5,
		# top_p=20,
	)
	outcome_desc, elapsed = await generator.generate(outcome_desc_prompt, options)
	print(outcome_desc)
	

async def main():
	await ingredient()
	# await potion()
	# await request_outcome()

asyncio.run(main())