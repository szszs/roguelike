# -*- coding: utf-8 -*- 
### character
from window import windows
from mobs import *
from tiles_data import tiles
from include import gradient
import string
import math

class character(living):
	def __init__(self, id_, name, plural, description, description_long, health, speed, carry_weight, carry_volume, sight_range, stamina,hunger, thirst, mana, ethereal, tile, aura, emit, sight_border_requirement, detect_glow_str, detect_glow_range, actions):
		living.__init__(self, id_, name, plural, description, description_long, health, speed, carry_weight, carry_volume,sight_range, stamina, hunger, thirst, mana, ethereal, tile, aura, emit, sight_border_requirement, detect_glow_str, detect_glow_range, actions)

	def window_init(self, w_ylen, w_xlen, y, x):
		self.window = windows.window(w_ylen, w_xlen, y, x)

	def recalc_win(self, game_y_len, game_x_len):
		self.window.move(1, 1)
		self.printstats()

	def printstats(self):
		self.window.clear()
		# print name
		self.window.wprint(0, 6-len(self.name)/2, str(self.name))
		# print stats
		for i in range(len(self.dynam_stats)):
			dynam_stat = self.dynam_stats[i]
			stat_bar = dynam_stat.get_stat_bar(self.window.xlen)
			for n in range(self.window.xlen):
				self.window.put(1+i, n, u'█', stat_bar[n])

			stat_amt = str(int(dynam_stat.value)) + '/' + str(dynam_stat.max)

			self.window.wprint(1+i, self.window.xlen // 2 -len(stat_amt)/2, stat_amt)

	def do_action(self, action_id, action_args, prep_args, game):
		action = game.action_generator.get_action_from_id(action_id)

		action.prep(self, *prep_args)
		
		game.update(self.next_update_time)
		successful, message = action.do(game, *action_args)
		if not successful:
			game.message_panel.add_phrase(message, [255,0,0])
			game.message_panel.print_messages()

		game.update(self.next_update_time)

		game.update_screen()

	def re_calculate_chunk_info(self, old_mapy, old_mapx):
		if old_mapy != self.worldmap.get_mapy(self.y) or old_mapx != self.worldmap.get_mapx(self.x):
			self.worldmap.recalcloc(self.mapy, self.mapx)

	def die(self, game):
		game.game_over()