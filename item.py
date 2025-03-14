from __future__ import annotations 
import util
import random
from typing import Type
import asyncio
import bottles_generator as generator
import game as gm

class Item():
	def __init__(self, item_def: ItemDef):
		self.item_def = item_def
		self.name = item_def.name if item_def else ""
		self.desc = item_def.desc if item_def else ""
		self.selected = False
		self.room = None
	
	def get_discard_value(self):
		return int(self.cost * 0.5)
	
	def get_fill_request_value(self):
		return 0
	
	def tick(self):
		pass	
	
	def get_display_name(self):
		return self.name

	def get_display_desc(self):
		return self.desc

	def combine(self, other):
		pass

class ItemDef():
	def __init__(self, name, item_type: Type[Item]=Item, desc=""):
		self.name = name
		self.desc = desc
		self.item_type = item_type

class Ingredient(Item):
	def __init__(self, item_def: IngredientDef):
		super().__init__(item_def)
		self.cost = item_def.cost if item_def else 0

class IngredientDef(ItemDef):
	def __init__(self, name, item_type: Type[Ingredient]=Ingredient, desc="", cost=0):
		super().__init__(name, item_type, desc)
		self.desc = desc
		self.cost = cost

		if not self.desc:
			self.desc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
			self.desc = self.desc[random.randint(0, int(len(self.desc)*0.5)):].lstrip().capitalize()

class Bottle(Ingredient):
	def __init__(self, item_def):
		super().__init__(item_def)
		self.ingredients = []
		self.brewing = False

	def tick(self):
		super().tick()	
	
	def get_display_name(self):
		return f"{self.name}{' ' + util.get_spinner() if self.brewing else '' }"
	
	def is_potion(self):
		return len(self.ingredients) > 1
	
	def is_brewed_potion(self):
		return self.is_potion() and not self.brewing

	def get_discard_value(self):
		return super().get_discard_value() + self.get_contents_discard_value()
	
	def get_contents_discard_value(self):
		if self.is_potion():
			return 0
		return sum(item.get_discard_value() for item in self.ingredients)

	def get_fill_request_value(self):
		if not self.is_potion():
			return 0
		total_cost = self.cost + sum(item.cost for item in self.ingredients)
		return total_cost * 2
	
	def empty(self):
		self.__init__(self.item_def)
	
	def combine(self, other):
		if type(other) is not Ingredient:
			return
		if type(other) is Bottle:
			return
		if len(self.ingredients) > 1:
			return

		item_i = other.room.items.index(other)
		other.room.remove_item(item_i)
		other.selected = False
		self.ingredients.append(other)
		if len(self.ingredients) == 1:
			self.name = f"Bottle of {other.name}"
			self.desc = f"A bottle containing {other.name}."
		else:
			self.generate_potion_task = asyncio.create_task(self._generate_potion())
			
		super().combine(other)

	async def _generate_potion(self):
		self.name = "Potion of..."
		self.desc = f"A brewing potion."
		self.brewing = True
		self.name, self.desc = await generator.generate_potion(self.ingredients)	
		self.brewing = False

class Request(Item):
	def __init__(self, name):
		super().__init__(item_def=None)
		self.name = name
		self.desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
		self.potion = None
		self.is_awaiting_outcome = False
		self.is_complete = False
		self.success_score = 3
		self.fail_score = -2
		self.skip_score = -1
		
	def fill(self, potion: Bottle, on_outcome):
		assert(not self.potion)
		self.potion = potion
		self.desc += "\n\n\"I'll give this a go.\""
		self.generate_outcome_task = asyncio.create_task(self._generate_outcome(on_outcome))

	def skip(self):
		self.desc += "\n\n> \"Sorry I can't help with that!\""
		self.desc += f"\n\n{self.skip_score}{gm.Game.score_chr}"
		self.is_complete = True

	async def _generate_outcome(self, on_outcome):
		self.is_awaiting_outcome = True
		desc, success = await generator.generate_request_outcome(self.desc, self.potion.desc)

		self.desc += f"\n\n\"{desc}\""

		success_str = ""
		if success:
			self.desc += f"\n\nSUCCESS!"
			self.desc += f"\n\n+{self.potion.get_fill_request_value()}{gm.Game.gold_chr}"
			self.desc += f"\n+{self.success_score}{gm.Game.score_chr}"
		else:
			self.desc += f"\n\nREFUNDED"
			self.desc += f"\n\n{self.fail_score}{gm.Game.score_chr}"

		self.is_awaiting_outcome = False
		self.is_complete = True
		on_outcome(request=self, success=success)

	def get_display_desc(self):
		spinner = "\n\n" + util.get_spinner() if self.is_awaiting_outcome else ""
		return f"{self.desc}{spinner}"