from __future__ import annotations 
import util
import random
import time
from typing import Type

class Item():
	def __init__(self, item_def: ItemDef):
		self.item_def = item_def
		self.name = item_def.name if item_def else ""
		self.desc = item_def.desc if item_def else ""
		self.selected = False
		self.room = None
	
	def get_resale_cost(self):
		return int(self.cost * 0.5)
	
	def get_fill_request_cost(self):
		return self.cost + 5
	
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
		self.brewing_start_time = -1

	def tick(self):
		super().tick()	
		if self.brewing and time.time() - self.brewing_start_time > 2:
			self.brewing = False
			self.desc = "A potion."
	
	def get_display_name(self):
		return f"{self.name}{' ' + util.get_spinner() if self.brewing else '' }"
	
	def is_potion(self):
		return len(self.ingredients) > 1
	
	def is_brewed_potion(self):
		return self.is_potion() and not self.brewing

	def get_resale_cost(self):
		return int(self.cost * 0.5) + self.get_contents_resale_cost()
	
	def get_contents_resale_cost(self):
		return int(sum(item.cost for item in self.ingredients) * 0.5)
	
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
			self.name = "A bottle of brewing potion"
			self.desc = f"A bottle containing a brewing potion."
			self.brewing = True
			self.brewing_start_time = time.time()
			
		super().combine(other)

class Request(Item):
	def __init__(self, name):
		super().__init__(item_def=None)
		self.name = name
		self.desc = "\"I'm preparing to host a grand midnight feast for the fae, but the enchanted banquet table keeps vanishing whenever I look away!\""
		self.potion = None
		self.pending_response = False
		self.pending_response_start_time = -1
		
	def fill(self, potion: Bottle, on_response):
		assert(not self.potion)
		self.potion = potion
		self.desc += "\n\n\"I'll give this a go.\""
		self.pending_response = True
		self.pending_response_start_time = time.time()
		self.on_response = on_response

	def is_complete(self):
		return self.potion and not self.pending_response

	def tick(self):
		super().tick()	
		if self.pending_response:
			if time.time() - self.pending_response_start_time > 2:
				self.pending_response = False
				self.desc += "\n\n\"That worked great!\""
				self.on_response(request=self, success=True)

	def get_display_desc(self):
		spinner = "\n\n" + util.get_spinner() if self.pending_response else ""
		return f"{self.desc}{spinner}"
	
from room import *