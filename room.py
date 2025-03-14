import asyncio
import random
import game as gm
import item as itm
import util
import bottles_generator as generator

class Room():
	def	__init__(self, name, key, max_items=10):
		self.name = name
		self.key = key
		self.max_items = max_items
		self.items = [None] * max_items

	def tick(self):
		for item in self.items:
			if item:
				item.tick()

	def on_leave(self):
		self.select(-1)

	def get_first_item_index(self):
		return next((i for i, x in enumerate(self.items) if x), -1)

	def select(self, i):
		selected_i = self.get_selected_item_index()
		if selected_i >= 0:
			self.items[selected_i].selected = False

		if i >= 0 and i < len(self.items) and self.items[i]:
			self.items[i].selected = True
	
	def toggle_select(self, i):
		selected_i = self.get_selected_item_index()
		if i == selected_i:
			self.select(-1)
		else:
			self.select(i)

	def add_item(self, item):
		index = next((i for i, x in enumerate(self.items) if not x), -1)
		if index < 0:
			return False

		self.items[index] = item
		item.selected = False
		item.room = self
		return True

	def remove_item(self, i):
		self.items[i] = None
		
	def get_selected_item_index(self):
		return next((i for i, x in enumerate(self.items) if x and x.selected), -1)

	def get_selected_item(self):
		index = self.get_selected_item_index()
		return self.items[index] if index >= 0 else None
	
	def count_items(self):
		return sum(1 for item in self.items if item)

	def draw_header(self, game):
		game.stdscr.addstr(0, 0, self.name.upper().center(gm.Game.width,"-"))

		# Go to room actions.
		actions_str = "".join(f"{room.key}: {room.name.lower()}  " for room in game.rooms).rstrip()
		state_str = f"Gold: {game.gold}{gm.Game.gold_chr}  {gm.Game.score_name}: {game.score}{gm.Game.score_chr}"
		str = state_str
		str += actions_str.rjust(gm.Game.width - len(str), " ")
		game.stdscr.addstr(1, 0, str)

	def draw_item_list_entry(self, game, item, index):
		str = f"{index+1}."
		if item:
			str += f" {'>> ' if item.selected else ''} {item.name} {item.cost}{gm.Game.gold_chr}"
			str += f"{' + ...' if item.selected and game.combining else ''}"
		game.stdscr.addstr(4+index, 0, str)

	def draw_selected_desc(self, game):
		selected_i = self.get_selected_item_index()
		if selected_i >= 0:
			selected = self.items[selected_i]
			game.stdscr.addstr(4 + 10 + 1, 0, f"{util.wraptext(selected.get_display_desc(), gm.Game.width)}")

	def draw_actions(self, game):
		# Contextual actions.
		y = 4 + 10 + 5
		for action in game.actions:
			if action.is_available(game):
				y += 1
				game.stdscr.addstr(y, 0, action.get_display_name(game))

	def draw(self, game):
		self.draw_header(game)
		self.draw_selected_desc(game)
		for i, item in enumerate(self.items):
			self.draw_item_list_entry(game, item, i)
		self.draw_actions(game)

class DeskRoom(Room):
	def __init__(self, ingredientGlossary):
		super().__init__("Workshop", "w")
		items = [
			ingredientGlossary.instantiate_by_name("Bottle"),
		]
		for item in items:
			self.add_item(item)

	def draw_item_list_entry(self, game, item, index):
		str = f"{index+1}."
		if item:
			str += f" {'>> ' if item.selected else ''} {item.get_display_name()}"
			str += f"{' + ...' if item.selected and game.combining else ''}"
		game.stdscr.addstr(4+index, 0, str)

class ShopRoom(Room):
	reroll_cost = 1
	
	def __init__(self, ingredientGlossary):
		super().__init__("Market", "e", max_items=6)
		self.glossary = ingredientGlossary
		self._populate()

	def _populate(self):
		for i in range(self.max_items):
			self.remove_item(i)
		new_items = self.glossary.instantiate_n(self.max_items)
		for item in new_items:
			self.add_item(item)

	def reroll(self):
		self._populate()

class RequestRoom(Room):
	def __init__(self):
		super().__init__("Requests", "q", max_items=3)
		self.generate_request_tasks = []
		self.populate()
			
	def select(self, i):
		if i < 0 or i >= self.max_items or not self.items[i]:
			# Don't deselect.
			return
		super().select(i)

	def add_item(self, item):
		super().add_item(item)
		# Always keep some request selected if there are any.
		if self.get_selected_item_index() < 0:
			self.select(self.get_first_item_index())

	def add_request(self):
		self.generate_request_tasks = [t for t in self.generate_request_tasks if not t.done()]
		self.generate_request_tasks.append(asyncio.create_task(self._generate_request()))
	
	def populate(self):
		max = self.max_items - self.count_items()
		if max == 0:
			return
		n = random.randint(1, max)
		for i in range(n):
			self.add_request()

	async def _generate_request(self):
		request = await generator.generate_request()
		self.add_item(request)
	
	def on_leave(self):
		# Don't deselect on leave (don't call super).

		# Replace completed requests.
		for i, request in enumerate(self.items):
			if request and request.is_complete:
				self.remove_item(i)
				if self.count_items() == 0:
					self.populate()

	def draw_item_list_entry(self, game, item, index):
		str = f"{index+1}."
		if item:
			str += f" {'>> ' if item.selected else ''} {item.get_display_name()}"
		game.stdscr.addstr(4+index, 0, str)