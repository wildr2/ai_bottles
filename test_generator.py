import asyncio
import generator as gen

generator = gen.create_generator()

potion_desc_prompt = '''
- Dragonfly Wings
- Fire Salts
Write a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book.
'''.strip()

async def potion():
	options = gen.Options(
		temperature=0.01,
		# seed = 42,
	)
	# desc, elapsed = await generator.generate(potion_desc_prompt, options)
	desc = "This potion grants the drinker the ability to glide through the air for a short duration."
	print(desc)

	for i in range(3):
		name_prompt = f"Generate a name for a magical potion. Provide only the name and only one name. It should be of the form \"Potion of...\". The name should describe the effects of the potion which are as follows:\n{desc}"
		options.temperature = 1.0
		options.top_p = 20.0
		name, elapsed = await generator.generate(name_prompt, options)
		print(name)

async def request_outcome():
	request_desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
	potion_desc = "This potion grants the drinker the ability to glide through the air for a short duration."
	# potion_desc = "This potion gives the drinker eyes in the back of their head for an hour."

	options = gen.Options(
		temperature=0.5,
		# seed = 42,
	)
	
	outcome_desc_prompt = f"Sam: {request_desc}\nDetermine what happens when Sam attempts to solve their problem using the following magic potion:\n\"{potion_desc}\"\nRole-playing as Sam, in one short sentence and using past tense, relate what happened."
	# outcome_desc, elapsed = await generator.generate(outcome_desc_prompt, options)
	# outcome_desc = "As I drank the potion, I floated gently off the ground, but the enchanted banquet table remained stubbornly invisible."
	# outcome_desc = "I drank the potion and, with my new eyes in the back of my head, I finally caught the mischievous pixies who kept making the banquet table disappear!"
	outcome_desc = "As I drank the potion, I suddenly noticed the faint, shimmering traces of the table's movements, allowing me to keep track of it as it reappeared and disappeared."
	print(outcome_desc)
	
	outcome_success_prompt = f"The problem: {request_desc}\nWhat happened next: {outcome_desc}\nWas the problem resolved? Reply with \"yes\" or \"no\"."
	temperature=0.5,
	outcome_success, elapsed = await generator.generate(outcome_success_prompt, options)
	print(outcome_success)
	

async def main():
	# await potion()
	await request_outcome()

asyncio.run(main())