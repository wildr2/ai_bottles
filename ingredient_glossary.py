import copy
from item import *

class IngredientGlossary():
	def __init__(self):
		items = [
			Bottle(),
			Item("Violet", 3),			
			Item("Dragonfly Wings", 10),
			Item("Salt", 1),
			Item("Pepper", 1),
			Item("Red Berries", 3),
			Item("Yellow Berries", 4),
			Item("Ginger", 2),
			Item("Garlic", 2),
			Item("Fire Salts", 4),
			Item("Chlorabloom", 9),
			Item("Glowstool", 5),
		]
		self.items = {item.name: item for item in items}
	
	def instantiate_by_name(self, name: str):
		return self.instantiate_by_def(self.items[name])
	
	def instantiate_by_def(self, item: Item):
		return copy.deepcopy(item)
	
	def instantiate_n(self, n):
		items = random.choices(list(self.items.values()), k=n)
		return [self.instantiate_by_def(item) for item in items]
