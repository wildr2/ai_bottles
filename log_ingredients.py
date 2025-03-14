import asyncio
import ingredient_glossary as ig

async def main():
	glossary = ig.IngredientGlossary()
	await glossary.load()

	for ing in glossary.ingredient_defs.values():
		print(f"- {ing.name} ({ing.cost}): {ing.desc}")

try:
	asyncio.run(main())
except KeyboardInterrupt:
	pass