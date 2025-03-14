import game as gm
import room as rm
import item as itm

class Action():
	def __init__(self):
		self.name = "jump"
		self.key = ord("j")
		self.room_types = [rm.Room]
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
		self.room_types = [rm.ShopRoom]
		self.requires_selected_item = True

	def get_display_name(self, game):
		selected = game.room.get_selected_item()
		return f"{chr(self.key)}: {self.name} {selected.cost}{gm.Game.gold_chr}"
	
	def do(self, game):
		super().do(game)
		game.buy_item(game.room, game.room.get_selected_item_index())

class SellAction(Action):
	def __init__(self):
		self.name = "discard"
		self.key = ord("x")
		self.room_types = [rm.DeskRoom]
		self.requires_selected_item = True

	def get_display_name(self, game):
		selected = game.room.get_selected_item()
		if type(selected) == itm.Bottle and len(selected.ingredients) > 0:
			return f"{chr(self.key)}: discard contents +{selected.get_contents_discard_value()}{gm.Game.gold_chr}"
		else:
			return f"{chr(self.key)}: discard +{selected.get_discard_value()}{gm.Game.gold_chr}"

	def do(self, game):
		super().do(game)
		selected_i = game.room.get_selected_item_index()
		game.sell_item(game.room, selected_i)

class CombineItemsAction(Action):
	def __init__(self):
		self.name = "combine with..."
		self.key = ord("+")
		self.room_types = [rm.DeskRoom]
		self.requires_selected_item = True

	def is_available(self, game):
		if not super().is_available(game):
			return False
		item = game.room.get_selected_item()
		if type(item) == itm.Bottle:
			return not item.is_potion()
		return True

	def do(self, game):
		super().do(game)
		game.start_combining_items()

class FillRequestAction(Action):
	def __init__(self):
		self.name = "sell"
		self.key = ord("Q")
		self.room_types = [rm.DeskRoom]
		self.requires_selected_item = True

	def get_display_name(self, game):
		selected = game.room.get_selected_item()
		request = game.request_room.get_selected_item()
		return f"{chr(self.key)}: {self.name} to {request.name} +{selected.get_fill_request_value()}{gm.Game.gold_chr}"

	def is_available(self, game):
		if not super().is_available(game):
			return False
		item = game.room.get_selected_item()
		if not (type(item) == itm.Bottle and item.is_brewed_potion()):
			return False
		request = game.request_room.get_selected_item()
		return bool(request)

	def do(self, game):
		super().do(game)
		game.fill_request(game.room, game.room.get_selected_item_index())

class RerollShopAction(Action):
	def __init__(self):
		self.name = f"reroll {rm.ShopRoom.reroll_cost}{gm.Game.gold_chr}"
		self.key = ord("r")
		self.room_types = [rm.ShopRoom]
		self.requires_selected_item = False

	def do(self, game):
		super().do(game)
		game.reroll_shop()