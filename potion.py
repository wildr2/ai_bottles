import curses
import random
import time
import copy
import textwrap

class Util():
	spinner_chrs = "|/-\\"

	def get_spinner():
		interval = 0.1
		i = int(time.time() / interval) % len(Util.spinner_chrs)
		return Util.spinner_chrs[i]

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
		return f"{self.name}{' ' + Util.get_spinner() if self.brewing else '' }"
	
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
		spinner = "\n\n" + Util.get_spinner() if self.pending_response else ""
		return f"{self.desc}{spinner}"

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

class Action():
	def __init__(self):
		self.name = "jump"
		self.key = ord("j")
		self.room_types = [Room]
		self.requires_selected_item = False
	
	def get_display_name(self, game):
		return f"{chr(self.key)}: {self.name}"

	def is_available(self, game):
		if type(game.room) not in self.room_types:
			return False
		if self.requires_selected_item and game.room.get_selected_item_index() < 0:
			return False
		return True

	def do(self, game):
		pass

class BuyAction(Action):
	def __init__(self):
		self.name = "buy"
		self.key = ord("W")
		self.room_types = [ShopRoom]
		self.requires_selected_item = True

	def get_display_name(self, game):
		selected = game.room.get_selected_item()
		return f"{chr(self.key)}: {self.name} {selected.cost}{Game.gold_chr}"
	
	def do(self, game):
		super().do(game)
		game.buy_item(game.room, game.room.get_selected_item_index())

class SellAction(Action):
	def __init__(self):
		self.name = "discard"
		self.key = ord("x")
		self.room_types = [DeskRoom]
		self.requires_selected_item = True

	def get_display_name(self, game):
		selected = game.room.get_selected_item()
		if type(selected) == Bottle and len(selected.ingredients) > 0:
			return f"{chr(self.key)}: discard contents +{selected.get_contents_resale_cost()}{Game.gold_chr}"
		else:
			return f"{chr(self.key)}: discard +{selected.get_resale_cost()}{Game.gold_chr}"

	def do(self, game):
		super().do(game)
		selected_i = game.room.get_selected_item_index()
		game.sell_item(game.room, selected_i)

class CombineItemsAction(Action):
	def __init__(self):
		self.name = "combine with..."
		self.key = ord("+")
		self.room_types = [DeskRoom]
		self.requires_selected_item = True

	def is_available(self, game):
		if not super().is_available(game):
			return False
		item = game.room.get_selected_item()
		if type(item) == Bottle:
			return not item.is_potion()
		return True

	def do(self, game):
		super().do(game)
		game.start_combining_items()

class FillRequestAction(Action):
	def __init__(self):
		self.name = "sell"
		self.key = ord("Q")
		self.room_types = [DeskRoom]
		self.requires_selected_item = True

	def get_display_name(self, game):
		selected = game.room.get_selected_item()
		request = game.request_room.get_selected_item()
		return f"{chr(self.key)}: {self.name} to {request.name} +{selected.get_fill_request_cost()}{Game.gold_chr}"

	def is_available(self, game):
		if not super().is_available(game):
			return False
		item = game.room.get_selected_item()
		if not (type(item) == Bottle and item.is_brewed_potion()):
			return False
		request = game.request_room.get_selected_item()
		return bool(request)

	def do(self, game):
		super().do(game)
		game.fill_request(game.room, game.room.get_selected_item_index())

class RerollShopAction(Action):
	def __init__(self):
		self.name = f"reroll {ShopRoom.reroll_cost}{Game.gold_chr}"
		self.key = ord("r")
		self.room_types = [ShopRoom]
		self.requires_selected_item = False

	def do(self, game):
		super().do(game)
		game.reroll_shop()
		
class Room():
	def	__init__(self, name, key):
		self.name = name
		self.key = ord(key)
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
		game.stdscr.addstr(0, 0, self.name.upper().center(Game.width,"-"))

		# Go to room actions.
		actions_str = "".join(f"{chr(room.key)}: {room.name.lower()}  " for room in game.rooms).rstrip()
		state_str = f"Gold: {game.gold}●  Score: {game.score}"
		str = state_str
		str += actions_str.rjust(Game.width - len(str), " ")
		game.stdscr.addstr(1, 0, str)

	def draw_item_list_entry(self, game, item, index):
		game.stdscr.addstr(4+index, 0,\
			f"{index+1}. {'>> ' if item.selected else ''} {item.name} {item.cost}{Game.gold_chr}" +\
			f"{' + ...' if item.selected and game.combining else ''}")

	def draw_selected_desc(self, game):
		selected_i = self.get_selected_item_index()
		if selected_i >= 0:
			selected = self.items[selected_i]
			game.stdscr.addstr(4 + 10 + 1, 0, f"{textwrap.fill(selected.get_display_desc(), Game.width, break_long_words=False, replace_whitespace=False)}")

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
		self.populate_n(self.shop_length)

	def populate(self):
		if len(self.item_pool) == 0:
			return
		if self.item_pool_i < 0:
			random.shuffle(self.item_pool)
			self.item_pool_i = len(self.item_pool) - 1
		self.add_item(self.item_pool.pop(self.item_pool_i))
		self.item_pool_i -= 1
		
	def populate_n(self, n):
		for i in range(self.shop_length):
			self.populate()

	def reroll(self):
		for i in range(len(self.items)-1, -1, -1):
			item = self.items[i]
			self.remove_item(i)
			self.item_pool.append(item)
			item.selected = False
		self.populate_n(self.shop_length)

class RequestRoom(Room):
	def __init__(self):
		super().__init__("Requests", "q")
		self.max_requests = 3
		request = Request("Sam")
		items = [
			request
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
			if request.is_complete():
				self.remove_item(i)

	def draw_item_list_entry(self, game, item, index):
		game.stdscr.addstr(4+index, 0,\
			f"{index+1}. {'>> ' if item.selected else ''} {item.get_display_name()}")

class Game():
	width = 100
	gold_chr = "●"

	def __init__(self, stdscr):
		self.stdscr = stdscr
		self.input_key = -1
		self.quit = False

		self.ingredientGlossary = IngredientGlossary()
		self.desk_room = DeskRoom(self.ingredientGlossary)
		self.shop_room = ShopRoom(self.ingredientGlossary)
		self.request_room = RequestRoom()
		self.rooms = [
			self.request_room,
			self.desk_room,
			self.shop_room,
		]
		self.actions = [
			RerollShopAction(),
			BuyAction(),
			CombineItemsAction(),
			SellAction(),
			FillRequestAction(),
		]

		self.room = self.desk_room
		self.prev_room = None
		self.gold = 5
		self.score = 0
		self.combining = False

	def tick(self):
		for room in self.rooms:
			room.tick()

		# Switch room.
		for room in self.rooms:
			if self.input_key == room.key:
				if room == self.room:
					if self.prev_room:
						self.set_room(self.prev_room)
				else:
					self.set_room(room)

		# Item combining.
		self.combining = self.combining if type(self.room) == DeskRoom else False
		combining_i = self.room.get_selected_item_index() if self.combining else -1
		self.combining = combining_i >= 0
	
		# Item selection.
		for i in range(10):
			key = ord(str(i))
			if self.input_key == key:
				index = 9 if i == 0 else i-1
				self.room.toggle_select(index)
				if self.combining:
					selected_i = self.room.get_selected_item_index()
					if selected_i >= 0:
						self.combine_items(self.room.items[combining_i], self.room.items[selected_i])
		# Esc or space to deselect.
		if self.input_key == 27 or self.input_key == ord(" "):
			self.room.select(-1)

		# Contextual actions.
		for action in self.actions:
			if self.input_key == action.key and action.is_available(self):
				action.do(self)

		# Draw.
		try:
			self.room.draw(self)
		except:
			pass

	def set_room(self, room):
		if self.room:
			self.room.on_leave()
			self.prev_room = self.room
		self.room = room
			
	def buy_item(self, shop, item_i):
		if item_i < 0:
			return False

		item = shop.items[item_i]
		if self.gold < item.cost:
			shop.select(-1)
			return False

		if not self.desk_room.add_item(item):
			return False

		self.gold -= item.cost
		shop.remove_item(item_i)
		return True
	
	def sell_item(self, room, item_i):
		item = room.items[item_i]
		if type(item) == Bottle and len(item.ingredients) > 0:
			self.gold += item.get_contents_resale_cost()
			item.empty()
		else:
			self.gold += item.get_resale_cost()
			room.remove_item(item_i)
	
	def start_combining_items(self):
		self.combining = True
	
	def combine_items(self, item1, item2):
		self.combining = False
		self.room.select(-1)
		item1.combine(item2)
		item2.combine(item1)

	def reroll_shop(self):
		if self.gold >= ShopRoom.reroll_cost:
			self.room.reroll()
			self.gold -= ShopRoom.reroll_cost

	def fill_request(self, room, item_i):
		item = room.items[item_i]
		room.remove_item(item_i)
		self.set_room(self.request_room)
		request = self.request_room.get_selected_item()
		request.fill(item, self.on_request_response)

	def on_request_response(self, request, success):
		if success:
			self.gold += request.potion.get_fill_request_cost()
		

def main(stdscr):
	curses.curs_set(0) # Hide cursor
	stdscr.nodelay(1) # Non-blocking input
	
	game = Game(stdscr)

	try:
		while True:
			stdscr.clear()
			game.tick()

			game.input_key = stdscr.getch()
			if game.quit:
				break
			stdscr.refresh()
	except KeyboardInterrupt:
		pass

curses.wrapper(main)