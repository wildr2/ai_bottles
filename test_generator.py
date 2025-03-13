import asyncio
import generator as gen
from generator import Generator

generator = gen.create_generator()

desc_prompt = '''
- Dragonfly Wings
- Fire Salts
Write a one sentence description of the effects of the magical potion brewed from the above ingredients. Don't mention the ingredients in the description. This description will appear next to the name of the potion in an alchemical recipe book.
'''.strip()

async def main():
	options = Generator.Options(
		temperature=0.01,
		# seed = 42,
	)
	# desc, elapsed = await generator.generate(desc_prompt, options)
	desc = "This potion grants the drinker the ability to glide through the air for a short duration."
	print(desc)

	for i in range(3):
		name_prompt = "Generate a name for a magical potion. Provide only the name and only one name. It could be a Potion, Elixir, Draught, Tonic... The name should describe the effects of the potion which are as follows:\n{desc}"
		options.temperature = 1.0
		options.top_p = 20.0
		name, elapsed = await generator.generate(name_prompt.format(desc), options)
		print(name)

asyncio.run(main())