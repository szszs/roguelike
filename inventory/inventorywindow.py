# -*- coding: utf-8 -*- 
from bearlibterminal import terminal
from window import windows
from window import message
import math

class item_option(object):
	def __init__(self, item, count):
		self.item = item
		self.count = count
		
		if self.count == 1:
			self.string = self.item.name
		else:
			self.string = self.item.plural + " (" + str(self.count) + ")"
		
		self.start_row = 0
		self.end_row = 0

class inventorywindow(windows.popup):
	def __init__(self, inventory, game):
		"""
				╔════════════════════════════════════════════════════════════════════════════════════╗
				║TITLE MESSAGE (inventory)                                                           ║
				║════════════════════════════════════════════════════════════════════════════════════║
				║Weapons:                                       ^   Equipped:                        ║
				║Option 17 Option 17 Option 17 Option 17 Option ▒   Primary weapon:                  ║
				║17  Option 17 Option 17  (highlighted)         ▒   sword                            ║
				║Option 18                                      ▒                                    ║
				║Armor:                                         █                                    ║
				║Option 20                                      ˅                                    ║
				╚════════════════════════════════════════════════════════════════════════════════════╝
		"""		
		self.inventory = inventory
		self.game = game

		self.game_y_len = game.preferences.w_ylen
		self.game_x_len = game.preferences.w_xlen

		self.selection_column = "items" # "items" or "equipped"

		self.row_width = 30
		self.max_rows = 30

		self.items_large_window = False
		self.equipped_items_large_window = False

		self.activepopups = game.activepopups

	def init(self):
		self.run_inventory = True
		while self.run_inventory:
			self.process_input(self.open_instance())
			self.close()

		# finished with inventory
		terminal.refresh()

	def process_input(self, item_option):
		if item_option is None:
			return

		# display information about the item
		title = item_option.string

		info = [(item_option.item.description, (200,200,200))]
		if item_option.item.description_long is not None:
			info.append((item_option.item.description_long, (200,200,200)))

		try:
			if len(item_option.item.actions) > 0:
				info.append(("\\n", (0,0,0)))
				info.append((("Equipping will allow you to perform the following actions: \\n"), (255,255,255)))
				if len(item_option.item.actions) == 1:
					info.append((item_option.item.actions[0].name, (200,200,200)))
				else:
					for action_index in range(len(item_option.item.actions)):
						if action_index < len(item_option.item.actions) - 1:
							info.append((action.name+",", (200,200,200)))
						else:
							info.append((action.name, (200,200,200)))
		except AttributeError:
			pass

		keybind_info = item_option.item.get_keybind_display_info(self.inventory) # dictionary: { 'keybind' : ["what it does", (color)] }

		item_info = windows.pure_text_popup(info, game=self.game, title=title, exit=keybind_info)

		# print keybinds for modifying the item
		keybind_display_info = []
		for keybind in keybind_info:
			keybind_display_info.append((keybind, keybind_info[keybind][1]))
			keybind_display_info.append((keybind_info[keybind][0] + ' \\n', keybind_info[keybind][1]))

		keybind_info_window = windows.text_popup_no_input(keybind_display_info, game=self.game, window_y=item_info.window.y, window_x=item_info.window.x+item_info.window.xlen)

		# get input from player
		input_ = item_info.init()
		if input_ is not None:
			item_option.item.process_modification(input_, self.inventory, self.game)

		keybind_info_window.close()

	def open_instance(self):
		self.item_option_index = 0
		self.equipped_option_index = 0

		self.initialize_window()
		self.prepare_window()
		self.refresh_window()

		self.activepopups.count += 1

		terminal.refresh()

		self.proceed = True

		while self.proceed:
			while terminal.has_input() and self.proceed:
				self.get_next_char()

		# finished response
		if self.item_option_index is None or self.equipped_option_index is None:
			return None
		else:
			if self.selection_column == "items":
				if self.no_items:
					return None
				return self.item_options[self.item_option_index]
			else:
				if self.no_equipped_items:
					return None
				return self.equipped_items_options[self.equipped_option_index]

	def get_next_char(self):
		char = terminal.read()

		if char in [terminal.TK_UP, terminal.TK_DOWN]:
			if char == terminal.TK_DOWN:
				if self.selection_column == "items":
					if self.item_option_index + 1 < len(self.item_options):
						self.item_option_index += 1
						self.recalc_min_max_rows()
				else:
					if self.equipped_option_index + 1 < len(self.equipped_items_options):
						self.equipped_option_index += 1
						self.recalc_min_max_rows()
			else:
				if self.selection_column == "items":
					if self.item_option_index - 1 >= 0:
						self.item_option_index -= 1
						self.recalc_min_max_rows()
				else:
					if self.equipped_option_index - 1 >= 0:
						self.equipped_option_index -= 1
						self.recalc_min_max_rows()
		elif char in [terminal.TK_TAB, terminal.TK_LEFT, terminal.TK_RIGHT]:
			if self.selection_column == "items":
				if not self.no_equipped_items:
					self.selection_column = "equipped"
			else:
				if not self.no_items:
					self.selection_column = "items"

		elif char == terminal.TK_ENTER:
			self.proceed = False
			return

		elif char == terminal.TK_ESCAPE:
			self.item_option_index = None
			self.equipped_option_index  = None
			self.proceed = False
			self.run_inventory = False
			return

		self.refresh_window()
		terminal.refresh()

	def recalc_min_max_rows(self):
		if self.selection_column == "items":
			selected_option = self.item_options[self.item_option_index]

			if selected_option.end_row < self.body_row_display_length:
				self.items_min_row = 0
				self.items_max_row = min(self.item_row_length - 1, self.body_row_display_length - 1)
			else:
				self.items_max_row = selected_option.end_row
				self.items_min_row = self.items_max_row - self.body_row_display_length + 1
		else:
			selected_option = self.equipped_items_options[self.equipped_option_index]

			if selected_option.end_row < self.body_row_display_length:
				self.equipped_items_min_row = 0
				self.equipped_items_max_row = min(self.equipped_items_row_length - 1, self.body_row_display_length - 1)
			else:
				self.equipped_items_max_row = selected_option.end_row
				self.equipped_items_min_row = self.equipped_items_max_row - self.body_row_display_length + 1

	def initialize_window(self):
		# add title
		self.title_row_length = 0
		self.title_row_list = []

		self.title = "Inventory: " + str(self.inventory.weight) + "/" + str(self.inventory.mob.carry_weight) +"  "+ str(self.inventory.volume) + "/" + str(self.inventory.mob.carry_volume)
		message.s_add_message(message.convert_phrase_to_list(self.title), self.row_width*2+2, self.add_new_title_row)

		# add item options
		item_options_unordered = []

		for item in self.inventory.items:
			item_options_unordered.append(item_option(item, self.inventory.items[item]))

		## group items together by type
		item_options_grouped = {}

		for option in item_options_unordered:
			try:
				item_options_grouped[option.item.type].append(option)
			except KeyError:
				item_options_grouped[option.item.type] = [option]

		## merge options into list ordered by item type
		self.item_options = []

		for option_type, option_list in item_options_grouped.iteritems():
			self.item_options += option_list

		## add item option rows
		self.item_row_length = 0
		self.items_row_list = []

		current_item_type = ''
		for option in self.item_options:
			# check if new type
			if option.item.type != current_item_type:
				message.s_add_message(message.convert_phrase_to_list(option.item.type), self.row_width, self.add_new_item_row)
				current_item_type = option.item.type

			option.start_row = self.item_row_length
			message.s_add_message(message.convert_phrase_to_list(option.string, color=(200,200,200)), self.row_width, self.add_new_item_row)
			option.end_row = self.item_row_length - 1

		self.no_items = (len(self.item_options) == 0)

		# add equipped items
		self.equipped_items_row_length = 0
		self.equipped_items_row_list = []
		self.equipped_items_options = []

		for equipment_slot in self.inventory.equipped_items:
			equipped_item = self.inventory.equipped_items[equipment_slot]
			if equipped_item is not None:
				message.s_add_message(message.convert_phrase_to_list(equipment_slot), self.row_width, self.add_new_equipped_item_row)
				equipped_item_option = item_option(equipped_item, 1)
				equipped_item_option.start_row = self.equipped_items_row_length
				message.s_add_message(message.convert_phrase_to_list(equipped_item_option.item.name), self.row_width, self.add_new_equipped_item_row)
				equipped_item_option.end_row = self.equipped_items_row_length - 1
				self.equipped_items_options.append(equipped_item_option)

		self.no_equipped_items = (len(self.equipped_items_options) == 0)

	def add_new_title_row(self, row):
		self.title_row_list.append(row)
		self.title_row_length += 1

	def add_new_item_row(self, row):
		self.items_row_list.append(row)
		self.item_row_length += 1

		if self.item_row_length + self.title_row_length > self.max_rows:
			self.items_large_window = True

	def add_new_equipped_item_row(self, row):
		self.equipped_items_row_list.append(row)
		self.equipped_items_row_length += 1

		if self.equipped_items_row_length + self.title_row_length > self.max_rows:
			self.equipped_items_large_window = True

	def prepare_window(self):
		self.body_row_display_length = self.max_rows-self.title_row_length

		self.items_min_row = 0
		self.items_max_row = min(self.item_row_length - 1, self.body_row_display_length - 1)

		self.equipped_items_min_row = 0
		self.equipped_items_max_row = min(self.equipped_items_row_length - 1, self.body_row_display_length - 1)

		windows.popup.__init__(self, self.body_row_display_length+2+self.title_row_length, self.row_width*2+2+2, self.game_y_len/2-(self.body_row_display_length+self.title_row_length+2)/2, self.game_x_len/2-(self.row_width*2+2+2)/2, self.activepopups)

	def refresh_window(self):
		self.window.clear()
		self.window.fill(color=(230,0,0,0))
		self.window.print_border()

		self.print_highlight()
		self.print_body()
		self.print_title()

	def print_highlight(self, color=(230,0, 83, 216)):
		if self.selection_column == "items":
			if not self.no_items:
				selection_option = self.item_options[self.item_option_index]
				highlight_min_row = selection_option.start_row
				highlight_max_row = selection_option.end_row
				for i in range(highlight_max_row - highlight_min_row + 1):
					y_index = i+1+self.title_row_length+highlight_min_row-self.items_min_row
					self.window.w_clear(y_index, 1, self.row_width, 1)
					self.window.wprint(y_index, 1, u'█'*self.row_width, color)
		else:
			if not self.no_equipped_items:
				selection_option = self.equipped_items_options[self.equipped_option_index]
				highlight_min_row = selection_option.start_row
				highlight_max_row = selection_option.end_row
				for i in range(highlight_max_row - highlight_min_row + 1):
					y_index = i+1+self.title_row_length+highlight_min_row-self.equipped_items_min_row
					self.window.w_clear(y_index, self.row_width+3, self.row_width, 1)
					self.window.wprint(y_index, self.row_width+3, u'█'*self.row_width, color)

	def print_row(self, row, y_index, x_index):
		for data_pair in row:
			char = data_pair[0]
			color = data_pair[1]
			self.window.put(y_index, x_index, char, color)
			x_index += 1

	def print_title(self):
		for i in range(self.title_row_length):
			row = self.title_row_list[i]
			self.print_row(row, i+1, 1)

	def print_body(self):
		if not self.no_items:
			for i in range(self.items_max_row - self.items_min_row + 1):
				row = self.items_row_list[self.items_min_row+i]
				self.print_row(row, i+1+self.title_row_length, 1)

			if self.items_large_window:
				self.items_print_scroll()

		if not self.no_equipped_items:
			for i in range(self.equipped_items_max_row - self.equipped_items_min_row + 1):
				row = self.equipped_items_row_list[self.equipped_items_min_row+i]
				self.print_row(row, i+1+self.title_row_length, 1+self.row_width+2)

			if self.equipped_items_large_window:
				self.equipped_items_print_scroll()

	def items_print_scroll(self):
		bar_length = self.body_row_display_length-2
		scroll_bar_length = int(round((float(bar_length) / self.item_row_length)*bar_length))+1

		self.window.put(1+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
		self.window.put(1+self.title_row_length, self.row_width+1, '^')
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width+1, u'˅')

		for i in range(bar_length):
			self.window.w_clear(2+i+self.title_row_length, self.row_width+1)
			self.window.put(2+i+self.title_row_length, self.row_width+1, u'█', color=(230,0,0,0))

		start_scroll_bar_index = int(math.ceil((float(self.items_min_row) / self.item_row_length)*bar_length))

		if start_scroll_bar_index + scroll_bar_length > bar_length:
			start_scroll_bar_index -= 1

		for i in range(scroll_bar_length):
			self.window.put(start_scroll_bar_index+i+2+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))

	def equipped_items_print_scroll(self):
		bar_length = self.body_row_display_length-2
		scroll_bar_length = int(round((float(bar_length) / self.equipped_items_row_length)*bar_length))+1

		self.window.put(1+self.title_row_length, self.row_width*2+2, u'█', color=(100,100,100))
		self.window.put(1+self.title_row_length, self.row_width*2+2, '^')
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width*2+2, u'█', color=(100,100,100))
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width*2+2, u'˅')

		for i in range(bar_length):
			self.window.w_clear(2+i+self.title_row_length, self.row_width*2+2)
			self.window.put(2+i+self.title_row_length, self.row_width*2+2, u'█', color=(230,0,0,0))

		start_scroll_bar_index = int(math.ceil((float(self.equipped_items_min_row) / self.equipped_item_row_length)*bar_length))

		if start_scroll_bar_index + scroll_bar_length > bar_length:
			start_scroll_bar_index -= 1

		for i in range(scroll_bar_length):
			self.window.put(start_scroll_bar_index+i+2+self.title_row_length, self.row_width*2+2, u'█', color=(100,100,100))