from __future__ import annotations
import asyncio
import random
import item as itm
import bottles_generator as gen

class IngredientGlossary():
	def __init__(self):
		self.ingredient_defs = {}
				
	async def load(self):
		ingredient_defs = [
			itm.IngredientDef("Bottle", itm.Bottle, "An empty bottle.", cost=4, shop_weight=10)
		]
		generated = await gen.generate_ingredient_defs()
		ingredient_defs.extend(generated)
		self.ingredient_defs = {ingredient_def.name: ingredient_def for ingredient_def in ingredient_defs}
	
	def instantiate_by_name(self, name: str):
		return self.instantiate_by_def(self.ingredient_defs[name])
	
	def instantiate_by_def(self, ingredient_def: itm.IngredientDef):
		return ingredient_def.item_type(ingredient_def)
	
	def instantiate_n(self, n):
		pop = list(self.ingredient_defs.values())
		weights = [d.shop_weight for d in pop]
		ingredient_defs = random.choices(pop, weights=weights, k=n)
		return [self.instantiate_by_def(ingredient_def) for ingredient_def in ingredient_defs]