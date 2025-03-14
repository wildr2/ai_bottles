import curses
import asyncio
import action as act
import room as rm
import item as itm
import ingredient_glossary as ig

class Game():
	width = 100
	gold_chr = "●"

	def __init__(self, stdscr):
		self.stdscr = stdscr
		self.input_key = -1
		self.quit = False

		self.ingredientGlossary = ig.IngredientGlossary()
		self.desk_room = rm.DeskRoom(self.ingredientGlossary)
		self.shop_room = rm.ShopRoom(self.ingredientGlossary)
		self.request_room = rm.RequestRoom()
		self.rooms = [
			self.request_room,
			self.desk_room,
			self.shop_room,
		]
		self.actions = [
			act.RerollShopAction(),
			act.BuyAction(),
			act.CombineItemsAction(),
			act.SellAction(),
			act.FillRequestAction(),
		]

		self.room = self.desk_room
		self.prev_room = None
		self.gold = 100
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
		self.combining = self.combining if type(self.room) == rm.DeskRoom else False
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

		self._draw()

	def _draw(self):
		self.room.draw(self)

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
		if type(item) == itm.Bottle and len(item.ingredients) > 0:
			self.gold += item.get_contents_discard_value()
			item.empty()
		else:
			self.gold += item.get_discard_value()
			room.remove_item(item_i)
	
	def start_combining_items(self):
		self.combining = True
	
	def combine_items(self, item1, item2):
		self.combining = False
		self.room.select(-1)
		item1.combine(item2)
		item2.combine(item1)

	def reroll_shop(self):
		if self.gold >= rm.ShopRoom.reroll_cost:
			self.room.reroll()
			self.gold -= rm.ShopRoom.reroll_cost

	def fill_request(self, room, item_i):
		item = room.items[item_i]
		room.remove_item(item_i)
		self.set_room(self.request_room)
		request = self.request_room.get_selected_item()
		request.fill(item, self._on_request_outcome)

	def _on_request_outcome(self, request, success):
		if success:
			self.gold += request.potion.get_fill_request_value()
		
async def main(stdscr):
	curses.curs_set(0) # Hide cursor
	stdscr.nodelay(1) # Non-blocking input
	
	game = Game(stdscr)

	while True:
		stdscr.clear()
		game.tick()

		game.input_key = stdscr.getch()
		if game.quit:
			break

		stdscr.refresh()
		curses.curs_set(0) # Hide cursor
		await asyncio.sleep(0)

if __name__ == "__main__":
	try:
		asyncio.run(curses.wrapper(main))
	except KeyboardInterrupt:
		pass