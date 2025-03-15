import random
import asyncio
import generator as gen

generator = gen.create_generator()

async def ingredient():
	topics = [
		"time",
		"language",
		"elements",
		"weather",
		"mind",
		"body",
		"spirit",
		"gravity",
		"nature",
		"destruction",
		"light",
		"sound",
		"dark",
		"manipulation",
		"creation",
		"transformation",
		"chaos",
		"order",
		"poison",
		"protection",
		"divination",
		"divinity",
		"illusion",
		"luck",
		"sex",
		"technology",
		"life",
		"death",
		"concealment",
		"emotion",
	]
	examples = [
		"parsley",
		"sage",
		"rosemary",
		"thyme",
		"mint",
		"lavender",
		"rose petals",
		"gold dust",
		"silver dust",
		"copper dust",
		"owl feather",
		"raven feather",
		"ink",
		"holly berries",
		"orange peel",
		"deer antler velvet",
		"pearl",
		"birch bark",
		"fulgurite",
		"bear fat",
		"chameleon scales",
		"coral dust",
		"eagle eye",
		"frog's leg",
		"obsidian",
		"pumice",
		"salt",
		"spider silk",
		"wolf fur",
		"bees' royal jelly",
		"human tears",
		"dew",
		"pollen",
		"mercury",
		"juice of juniper berries",
		"safflower oil",
		"bat wings",
		"beetle carapace",
		"crawler venom",
		"bone dust",
		"rat tail",
		"flax seed oil",
		"pig foot",
		"burdock root",
		"wild ginger",
		"bluetts",
		"elderberry leaves",
		"red trillium",
		"salamander eggs",
		"poison ivy leaves",
		"discarded snake skin",
		"cinnamon",
		"chamomile",
		"mugwort",
		"frankincense",
		"sulfur",
		"pine sap",
		"valerian",
		"garlic",
		"nightshade",
		"fermented raspberries",
		"white gooseberries",
		"black sand",
		"fresh moss",
		"crushed rutile",
		"flakes of pyrite",
		"skin of toad",
		"serpent's egg",
		"eye of newt",
		"tongue of dog",
		"lizard tail",
		"root of mandrake",
		"slip of yew",
		"twig of fern",
		"oak acorns",
		"hart's blood",
		"goat's milk",
		"sheep's wool",
		"driftwood",
	]

	options = gen.Options(
		temperature=0.5,
		# top_p=1.0,
	)
	examples = random.sample(examples, k=10)
	descs = []
	other_topics = []
	for example in examples:
		# topic_n = random.randint(1, 2)
		# topics_str = "".join(f"- {topic}\n" for topic in chosen_topics)
		# chosen_topics = random.sample(topics, k=topic_n)
		# print(f"{name} ({''.join(topic + ', ' for topic in chosen_topics)})")

		# chosen_examples = random.sample(examples, k=3)
		# examples_str = "".join(f"- {example}\n" for example in chosen_examples)
		# name_prompt = f"Predict the next ingredient in the list (it won't be a repeat). Provide only the name and only one name.\n{examples_str}"
		# name, elapsed = await generator.generate(name_prompt, options)
		# print(f"{name} ({''.join(example + ', ' for example in chosen_examples)})")
		
		# example = random.sample(examples, k=1)[0]
		# topic = random.sample(topics, k=1)[0]
		# name_prompt = f"Suppose the ingredient \"{example}\" is used to create a potion with a \"{topic}\" related effect. Tweak the name of the ingredient to better match the effect. Provide only the new name."
		# name, elapsed = await generator.generate(name_prompt, options)
		# print(f"{name} ({example}, {topic})")

		other_topics_str = "".join(f"{topic}," for topic in other_topics[-10:])
		other_topics_str = other_topics_str[:-1]
		ex_topics = random.sample(topics, k=2)
		ex_topics_str = "".join(f"{topic}," for topic in ex_topics)
		ex_topics_str = ex_topics_str[:-1]
		# topic_prompt = f"Already used effect types: {other_topics_str}\nHelp me develop a fantasy setting. Give me two new magical effect types (one word each) that a potion ingredient named \"{example}\" would have, for instance \"{ex_topics_str}\". Respond with just the two comma separated words."
		topic_prompt = f"Already used effect types: {other_topics_str}\nHelp me develop a fantasy setting. Give me two new magical effect types (one word each) that a potion ingredient named \"{example}\" would have. Respond with just the two comma separated words."
		topic, elapsed = await generator.generate(topic_prompt, options)
		other_topics.append(topic)
		# print(f"- {example}, \"{ex_topics_str}\": {topic}")
		print(f"- {example}: {topic}")

		# others_str = "".join(f"- {desc}\n" for desc in descs[-5:])
		# desc_prompt = f"Other ingredients:\n{others_str}\nGenerate a one sentence description for a potion ingredient named \"{example}\"."
		desc_prompt = f"Generate a one sentence description for a potion ingredient named \"{example}\". Note the categories of effects it can produce, which should relate to: \"{topic}\"."
		desc, elapsed = await generator.generate(desc_prompt, options)
		descs.append(desc)
		print(f"- {desc}")

async def potion():
	ingredients = [
		"Crawler venom is a highly toxic, viscous liquid extracted from the fangs of giant, subterranean crawlers, known for its paralyzing and hallucinogenic effects.",
		"Copper dust is a finely ground, shimmering metallic powder, often used in potions for its conductive and transformative properties.",
		"Fresh moss is a vibrant, earthy ingredient, often used in potions for its rejuvenating and healing properties.",
		"Deer antler velvet is a soft, cartilaginous tissue found on the growing antlers of male deer, often used in traditional medicine for its purported health benefits.",
		"Flakes of pyrite are small, shiny, and brittle pieces of fool's gold, often used in potions for their reflective and heat-conducting properties.",
	]

	chosen_ingredients = random.sample(ingredients, k=2)
	ingredients_str = "".join(f"- {ing}\n" for ing in chosen_ingredients)
	print(ingredients_str)
	# ingredients_str = "- Dragonfly Wings\n- Fire Salts\n"
	
	potion_desc_prompt = f"{ingredients_str}\nWrite a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book."
	options = gen.Options(
		temperature=0.01,
	)
	desc, elapsed = await generator.generate(potion_desc_prompt, options)
	# desc = "This potion grants the drinker the ability to glide through the air for a short duration."
	print(desc)

	options = gen.Options(
		temperature=1.0,
		# top_p=20.0,
	)
	for i in range(1):
		name_prompt = f"Generate a name for a magical potion. Provide only the name and only one name. It should be of the form \"Potion of...\". The name should describe the effects of the potion which are as follows:\n{desc}"
		name, elapsed = await generator.generate(name_prompt, options)
		print(name)

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