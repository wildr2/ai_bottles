import util
import random
import time

class Item():
	def __init__(self, name, cost):
		self.name = name
		self.cost = cost
		self.selected = False
		self.desc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
		self.desc = self.desc[random.randint(0, int(len(self.desc)*0.5)):].lstrip().capitalize()
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
		
class Bottle(Item):
	def __init__(self):
		super().__init__("Bottle", 4)
		self.ingredients = []
		self.desc = "An empty bottle."
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
		self.__init__()
	
	def combine(self, other):
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
		super().__init__(name, 0)
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