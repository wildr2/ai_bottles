import random
import game as gm
import item as itm
import util

class Room():
	def	__init__(self, name, key):
		self.name = name
		self.key = key
		self.items = []

	def tick(self):
		for item in self.items:
			item.tick()

	def on_leave(self):
		self.select(-1)

	def select(self, i):
		selected_i = self.get_selected_item_index()
		if selected_i >= 0:
			self.items[selected_i].selected = False

		if i >= 0 and i < len(self.items):
			self.items[i].selected = True
	
	def toggle_select(self, i):
		selected_i = self.get_selected_item_index()
		if i == selected_i:
			self.select(-1)
		else:
			self.select(i)

	def add_item(self, item):
		if len(self.items) >= 10:
			return False
		self.items.append(item)
		item.selected = False
		item.room = self
		return True

	def remove_item(self, i):
		self.items.pop(i)
		
	def get_selected_item_index(self):
		return next((i for i, x in enumerate(self.items) if x.selected), -1)

	def get_selected_item(self):
		index = self.get_selected_item_index()
		return self.items[index] if index >= 0 else None

	def draw_header(self, game):
		game.stdscr.addstr(0, 0, self.name.upper().center(gm.Game.width,"-"))

		# Go to room actions.
		actions_str = "".join(f"{room.key}: {room.name.lower()}  " for room in game.rooms).rstrip()
		state_str = f"Gold: {game.gold}●  Score: {game.score}"
		str = state_str
		str += actions_str.rjust(gm.Game.width - len(str), " ")
		game.stdscr.addstr(1, 0, str)

	def draw_item_list_entry(self, game, item, index):
		game.stdscr.addstr(4+index, 0,\
			f"{index+1}. {'>> ' if item.selected else ''} {item.name} {item.cost}{gm.Game.gold_chr}" +\
			f"{' + ...' if item.selected and game.combining else ''}")

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
			ingredientGlossary.instantiate_by_name("Salt"),
		]
		for item in items:
			self.add_item(item)

	def draw_item_list_entry(self, game, item, index):
		game.stdscr.addstr(4+index, 0,\
			f"{index+1}. {'>> ' if item.selected else ''} {item.get_display_name()}" +\
			f"{' + ...' if item.selected and game.combining else ''}")

class ShopRoom(Room):
	reroll_cost = 1
	
	def __init__(self, ingredientGlossary):
		super().__init__("Market", "e")
		self.shop_length = 6
		self.item_pool = ingredientGlossary.instantiate_n(50)
		self.item_pool_i = -1
		self._populate_n(self.shop_length)

	def _populate(self):
		if len(self.item_pool) == 0:
			return
		if self.item_pool_i < 0:
			random.shuffle(self.item_pool)
			self.item_pool_i = len(self.item_pool) - 1
		self.add_item(self.item_pool.pop(self.item_pool_i))
		self.item_pool_i -= 1
		
	def _populate_n(self, n):
		for i in range(self.shop_length):
			self._populate()

	def reroll(self):
		for i in range(len(self.items)-1, -1, -1):
			item = self.items[i]
			self.remove_item(i)
			self.item_pool.append(item)
			item.selected = False
		self._populate_n(self.shop_length)

class RequestRoom(Room):
	def __init__(self):
		super().__init__("Requests", "q")
		self.max_requests = 3
		items = [
			itm.Request("Sam")
		]
		for item in items:
			self.add_item(item)
			
	def select(self, i):
		if i < 0 or i >= len(self.items):
			return
		super().select(i)

	def add_item(self, item):
		super().add_item(item)
		# Always keep some request selected if there are any.
		if self.get_selected_item_index() < 0:
			self.select(0)
	
	def on_leave(self):
		# Don't deselect on leave (don't call super).
		# Remove completed requests.
		for i, request in enumerate(self.items):
			if request.complete:
				self.remove_item(i)

	def draw_item_list_entry(self, game, item, index):
		game.stdscr.addstr(4+index, 0,\
			f"{index+1}. {'>> ' if item.selected else ''} {item.get_display_name()}")