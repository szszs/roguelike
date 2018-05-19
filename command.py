# -*- coding: utf-8 -*- 
### commands
import weather
import tiles
import time
import math
import wizard

from bearlibterminal import terminal

import mobs
import action
from windowmod import *

class commands(object):
	def __init__(self):
		self.move = {
		### numpad on keyboard
		terminal.TK_KP_1 : [1, -1],
		terminal.TK_KP_2 : [1, 0],
		terminal.TK_KP_3 : [1, 1],
		terminal.TK_KP_4 : [0, -1],
		terminal.TK_KP_5 : [0, 0],
		terminal.TK_KP_6 : [0, 1],
		terminal.TK_KP_7 : [-1, -1],
		terminal.TK_KP_8 : [-1, 0],
		terminal.TK_KP_9 : [-1, 1],
		### conventional 4-dir
		terminal.TK_RIGHT : [0, 1],
		terminal.TK_DOWN : [1, 0],
		terminal.TK_LEFT : [0, -1],
		terminal.TK_UP : [-1, 0],
		### rest
		terminal.TK_R : [0, 0]
		}

		self.update_time = 0

	def command(self, uinput, game):
		if terminal.check(terminal.TK_SHIFT):
			self.shift_on = True
		else:
			self.shift_on = False

		if uinput == terminal.TK_ESCAPE:
			game.proceed = False
		elif uinput in self.move.keys():
			movement_time = time.clock()

			newy = game.me.y + self.move[uinput][0]
			newx = game.me.x + self.move[uinput][1]

			if game.world.check_passable(newy, newx):
				if self.shift_on:
					move_action = action.a_Sprint
				else:
					move_action = action.a_Walk

				game.update(move_action._calc_prep_time(game.me.speed.max))

				if game.world.check_passable(newy, newx):
					game.me.remove()
					game.me.add(newy, newx)
					if game.me.emit:
						game.me.aura._move(newy, newx)

					game.world.recalcloc(game.me.mapy, game.me.mapx)
				
					if uinput != terminal.TK_KP_5:
						game.me.stamina.alter(-move_action.stamina_cost)

				else:
					game.message_panel.add_phrase('Something blocked your path!', [255,0,0])
					game.message_panel.print_messages()

				game.update(move_action._calc_recover_time(game.me.speed.max))

				game.update_screen()

			else:
				game.message_panel.add_phrase('Cannot move there.', [255,0,0])
				game.message_panel.print_messages()
			
			#p print("movement update: --- %s seconds ---" % (time.clock() - movement_time))

		elif uinput == terminal.TK_W:
			time_advance = 100
			game.update(time_advance)
			game.update_screen()
			game.message_panel.add_phrase('Time advanced by ' + str(time_advance))
			game.message_panel.print_messages()

		elif uinput == terminal.TK_C:
			type_of_construct = terminal.read()

			construct_lib = {
			terminal.TK_W : tiles.wall_wood,
			terminal.TK_G : tiles.gray_glass
			}

			try:
				construct = construct_lib[type_of_construct]
				dir = terminal.read()
			except KeyError:
				dir = type_of_construct
				construct = tiles.black_block
			
			if game.world.layers.add_tile(game.me.y + self.move[dir][0], game.me.x + self.move[dir][1], construct):
				game.message_panel.add_phrase('Placed ' + construct.examine.lower(), [255,255,255])
			else:
				game.message_panel.add_phrase('Error placing constructy.', [255,0,0])
			game.message_panel.print_messages()
			game.update_screen()

		elif uinput == terminal.TK_V:
			if terminal.check(terminal.TK_SHIFT):
				topy = game.me.y - 10
				topx = game.me.x - 10
				for n in range(20):
					for i in range(20):
						game.world.conmap.add_tile(topy + n, topx + i, tiles.floor_wood)

		elif uinput == terminal.TK_M:
			while not terminal.has_input():
				dir = terminal.read()
				break
			game.message_panel.add_phrase(dir, [255,0,0])
			game.message_panel.print_messages()

		elif uinput == terminal.TK_S:
			if not self.shift_on:
				type_of_mob = terminal.read()
				if type_of_mob == terminal.TK_1:
					mobs.test_mob.create(game.me.y + 4, game.me.x, game.world, game.FOV, game.all_mobs, game.timer.time)
				elif type_of_mob == terminal.TK_2:
					mobs.test_light_mob.create(game.me.y + 4, game.me.x, game.world, game.FOV, game.all_mobs, game.timer.time)
				elif type_of_mob == terminal.TK_3:
					mobs.test_speed_mob.create(game.me.y + 8, game.me.x, game.world, game.FOV, game.all_mobs, game.timer.time)
				elif type_of_mob == terminal.TK_4:
					mobs.test_blind_mob.create(game.me.y + 8, game.me.x, game.world, game.FOV, game.all_mobs, game.timer.time)
				elif type_of_mob ==terminal.TK_5:
					mobs.test_determined_mob.create(game.me.y + 8, game.me.x, game.world, game.FOV, game.all_mobs, game.timer.time)
			else:
				for chunk in game.all_mobs.mobs.values():
					for mob in chunk:
						mob.can_move = not mob.can_move
			game.update_screen()

		elif uinput == terminal.TK_L:
			while not terminal.has_input():
				type_of_torch = terminal.read()
				break
			if type_of_torch == terminal.TK_R:
				torch = tiles.torch
			elif type_of_torch == terminal.TK_B:
				torch = tiles.torch_blue
			while not terminal.has_input():
				dir = terminal.read()
				break
			torchy = game.me.y + self.move[dir][0]
			torchx = game.me.x + self.move[dir][1]

			if game.world.layers.add_tile(torchy, torchx, torch):
				new_aura=torch.aura_maker.create_aura(game.world, game.world.aura_group, game.world.glow_coords, game.FOV)
				new_aura._spawn(torchy, torchx)

			game.update_screen()

		elif uinput == terminal.TK_X:
			check_y = game.me.y
			check_x = game.me.x

			game.info_panel.open(game.bg_windows)
			game.info_panel.prompt(game, check_y, check_x)
			game.info_panel.exit(game.bg_windows)
			game.world.view(game)
			terminal.refresh()

		elif uinput == terminal.TK_H:
			for dynam_stat in game.me.dynam_stats:
				dynam_stat.alter(-1)
			game.me.printstats()

		elif uinput == terminal.TK_ENTER:
			message_test_popup = text_input_popup('Enter test message to be displayed on the message panel:', game.preferences.w_ylen, game.preferences.w_xlen, title='test title', activepopups=game.activepopups, only_ascii = False)
			message_test = message_test_popup.init()
			if message_test:
				print '-------------'
				game.message_panel.add_phrase(message_test)
				game.message_panel.print_messages()
				print '-------------'

		elif uinput == terminal.TK_A:
			proceed = True
			dir = terminal.read()
			if dir == terminal.TK_ESCAPE:
				proceed = False
			while dir not in self.move.keys() and proceed:
				dir = terminal.read()

			if proceed:
				attack_y = game.me.y + self.move[dir][0]
				attack_x = game.me.x + self.move[dir][1]

				attack_action = action.a_smite

				game.update(attack_action._calc_prep_time(game.me.speed.max))
				
				if game.me.stamina.value >= attack_action.stamina_cost:
					attack_action.do(game, game.me, attack_y, attack_x, game.all_mobs.mob_lib)
					game.me.stamina.alter(-attack_action.stamina_cost)
				else:
					game.message_panel.add_phrase("Not enough stamina!")
					game.message_panel.print_messages()
				
				game.update(attack_action._calc_recover_time(game.me.speed.max))

				game.update_screen()






		# other possibilities
		elif uinput == terminal.TK_RESIZED:
			# print '--------------------------!!!RESIZED!!!!!!!!!!--------------------'
			# game.w_ylen = terminal.state(terminal.TK_HEIGHT)
			# game.w_xlen = terminal.state(terminal.TK_WIDTH)

			# game.world.recalc_win(game.w_ylen, game.w_xlen)

			# game.message_panel.recalc_win(game.w_ylen, game.w_xlen)

			# game.info_panel.recalc_win(game.w_ylen, game.w_xlen)

			# game.me.recalc_win(game.w_ylen, game.w_xlen)

			# game.all_mobs.recalc_win(game.w_ylen, game.w_xlen)

			# game.bg_windows.recalc_win(game.w_ylen, game.w_xlen, 0, 0, 150)

			# game.bg_windows.recalc_borders()
			# game.bg_windows.print_borders()

			self.update_view(game)

		# wizard mode
		elif uinput == terminal.TK_BACKSLASH: # text_input_popup
			wizard_popup = text_input_popup('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut consequat dui vel bibendum volutpat. Curabitur at turpis felis. Curabitur quis mauris eu orci rhoncus auctor vel non turpis. Cras egestas tellus sit amet est dignissim, et fringilla risus condimentum. \\b Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus. Sed ante lorem, hendrerit quis velit nec, sollicitudin mattis risus.', game.preferences.w_ylen, game.preferences.w_xlen, title='Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title. Test title.', activepopups=game.activepopups)
			wizard_command = wizard_popup.init()
			if wizard_command:
				wizard.process_request(wizard_command, game)