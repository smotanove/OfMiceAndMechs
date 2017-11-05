phasesByName = None
gamestate = None
names = None
characters = None

class FirstTutorialPhase(object):
	def __init__(self):
		self.name = "FirstTutorialPhase"

	def start(self):
		gamestate.currentPhase = self

		# fix the setup
		if not terrain.tutorialMachineRoom.secondOfficer:
			name = names.characterFirstNames[(gamestate.tick+2)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)]
			npc = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name)
			npc.terrain = terrain
			npc.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc,4,3)
			terrain.tutorialMachineRoom.secondOfficer = npc
		npc = terrain.tutorialMachineRoom.secondOfficer

		if not terrain.tutorialMachineRoom.firstOfficer:
			name = name=names.characterFirstNames[(gamestate.tick+9)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)]
			npc2 = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)].split(" ")[-1][0].lower()],5,3,name=name)
			npc2.terrain = terrain
			npc2.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc2,5,3)
			terrain.tutorialMachineRoom.firstOfficer = npc2
		npc2 = terrain.tutorialMachineRoom.firstOfficer

		self.tick = gamestate.tick

		cinematics.showCinematic("welcome to the Trainingenvironment\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")

		def doBasicSchooling():
			if not mainChar.gotBasicSchooling:
				cinematics.showCinematic("the Trainingenvironment will show now. take a look at Everything and press "+commandChars.wait+" afterwards. You will be able to move later")
				cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
				cinematics.showCinematic("you are represented by the "+displayChars.main_char+" Character. find yourself on the Screen and press "+commandChars.wait)
				cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
				cinematics.showCinematic("right now you are in the Boilerroom\n\nthe Floor is represented by "+displayChars.floor+" and Walls are shown as "+displayChars.wall+". the Door is represented by "+displayChars.door_closed+" or "+displayChars.door_opened+" when closed.\n\na empty Room would look like this:\n\n"+displayChars.wall*5+"\n"+displayChars.wall+displayChars.floor*3+displayChars.wall+"\n"+displayChars.wall+displayChars.floor*3+displayChars.door_closed+"\n"+displayChars.wall+displayChars.floor*3+displayChars.wall+"\n"+displayChars.wall*5+"\n\nthe Trainingenvironment will display now. please try to orient yourself in the Room.\n\npress "+commandChars.wait+" when successful")
				cinematic = cinematics.ShowGameCinematic(1)
				def wrapUp():
					mainChar.gotBasicSchooling = True
					doSteamengineExplaination()
					gamestate.save()
				cinematic.endTrigger = wrapUp
				cinematics.cinematicQueue.append(cinematic)
			else:
				doSteamengineExplaination()

		def doSteamengineExplaination():
			cinematics.showCinematic("on the southern Side of the Room you see the Steamgenerators. A Steamgenerator might look like this:\n\n"+displayChars.void+displayChars.pipe+displayChars.boiler_inactive+displayChars.furnace_inactive+"\n"+displayChars.pipe+displayChars.pipe+displayChars.boiler_inactive+displayChars.furnace_inactive+"\n"+displayChars.void+displayChars.pipe+displayChars.boiler_active+displayChars.furnace_active+"\n\nit consist of Furnaces marked by "+displayChars.furnace_inactive+" or "+displayChars.furnace_active+" that heat the Water in the Boilers "+displayChars.boiler_inactive+" till it boils. a Boiler with boiling Water will be shown as "+displayChars.boiler_active+".\n\nthe Steam is transfered to the Pipes marked with "+displayChars.pipe+" and used to power the Ships Mechanics and Weapons\n\nDesign of Generators are often quite unique. try to recognize the Genrators in this Room and press "+commandChars.wait+"")
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.showCinematic("the Furnaces burn Coal shown as "+displayChars.coal+" . if a Furnace is burning Coal, it is shown as "+displayChars.furnace_active+" and shown as "+displayChars.furnace_inactive+" if not.\n\nthe Coal is stored in Piles shown as "+displayChars.pile+". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed.")
			cinematic = cinematics.ShowGameCinematic(0)
			def wrapUp():
				doCoalDelivery()
				gamestate.save()
			cinematic.endTrigger = wrapUp
			cinematics.cinematicQueue.append(cinematic)

		def doCoalDelivery():
			cinematics.showCinematic("Since a Coaldelivery is incoming anyway. please wait and pay Attention.\n\ni will count down the Ticks in the Messagebox now")
			
			class CoalRefillEvent(object):
				def __init__(subself,tick):
					subself.tick = tick

				def handleEvent(subself):
					messages.append("*rumbling*")
					messages.append("*rumbling*")
					messages.append("*smoke and dust on Coalpiles and neighbourng Fields*")
					messages.append("*a chunk of Coal drops onto the floor*")
					terrain.tutorialMachineRoom.addItems([items.Coal(7,5)])
					messages.append("*smoke clears*")

			terrain.tutorialMachineRoom.addEvent(CoalRefillEvent(gamestate.tick+11))

			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("8"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("7"))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("by the Way: the Piles on the lower End of the Room are Storage for Replacementparts and you can sleep in the Hutches n the middle of the Room shown as "+displayChars.hutch_free+" or "+displayChars.hutch_occupied))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("6"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("5"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("4"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("3"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("2"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("1"))
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("Coaldelivery now"))
			cinematic = cinematics.ShowGameCinematic(2)
			def wrapUp():
				doFurnaceFirering()
				gamestate.save()
			cinematic.endTrigger = wrapUp
			cinematics.cinematicQueue.append(cinematic)

		def doFurnaceFirering():
			cinematics.showCinematic("your cohabitants in this Room are:\n '"+npc.name+"' ("+npc.display+") is this Rooms 'Raumleiter' and therefore responsible for proper Steamgeneration in this Room\n '"+npc2.name+"' ("+npc2.display+") was dispatched to support '"+npc.name+"' and is his Subordinate\n\nyou will likely report to '"+npc.name+"' later. please try to find them on the display and press "+commandChars.wait)
			cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
			cinematics.showCinematic(npc2.name+" will demonstrate how to fire a furnace now.\n\nwatch and learn.")
			class AddQuestEvent(object):
				def __init__(subself,tick):
					subself.tick = tick

				def handleEvent(subself):
					quest0 = quests.CollectQuest()
					quest1 = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[2])
					quest2 = quests.MoveQuest(terrain.tutorialMachineRoom,4,3)
					quest0.followUp = quest1
					quest1.followUp = quest2
					quest2.followUp = None
					npc.assignQuest(quest0,active=True)

			class ShowMessageEvent(object):
				def __init__(subself,tick):
					subself.tick = tick

				def handleEvent(subself):
					messages.append("*Erwin von Libwig, please fire the Furnace now*")

			terrain.tutorialMachineRoom.addEvent(ShowMessageEvent(gamestate.tick+1))
			terrain.tutorialMachineRoom.addEvent(AddQuestEvent(gamestate.tick+2))
			cinematic = cinematics.ShowGameCinematic(22)
			def wrapUp():
				doWrapUp()
				gamestate.save()
			cinematic.endTrigger = wrapUp
			cinematics.cinematicQueue.append(cinematic)

		def doWrapUp():
			cinematics.showCinematic("there are other Items in the Room that may or may not be important for you. Here is the full List for you to review:\n\n Bin ("+displayChars.binStorage+"): Used for storing Things intended to be transported further\n Pile ("+displayChars.pile+"): a Pile of Things\n Door ("+displayChars.door_opened+" or "+displayChars.door_closed+"): you can move through it when open\n Lever ("+displayChars.lever_notPulled+" or "+displayChars.lever_pulled+"): a simple Man-Machineinterface\n Furnace ("+displayChars.furnace_inactive+"): used to generate heat burning Things\n Display ("+displayChars.display+"): a complicated Machine-Maninterface\n Wall ("+displayChars.wall+"): ensures the structural Integrity of basically any Structure\n Pipe ("+displayChars.pipe+"): transports Liquids, Pseudoliquids and Gasses\n Coal ("+displayChars.coal+"): a piece of Coal, quite usefull actually\n Boiler ("+displayChars.boiler_inactive+" or "+displayChars.boiler_active+"): generates Steam using Water and and Heat\n Chains ("+displayChars.chains+"): some Chains dangling about. sometimes used as Man-Machineinterface or for Climbing\n Comlink ("+displayChars.commLink+"): a Pipe based Voicetransportationsystem that allows Communication with other Rooms\n Hutch ("+displayChars.hutch_free+"): a comfy and safe Place to sleep and eat")

			class StartNextPhaseEvent(object):
				def __init__(subself,tick):
					subself.tick = tick

				def handleEvent(subself):
					self.end()

			terrain.tutorialMachineRoom.addEvent(StartNextPhaseEvent(gamestate.tick+1))
			gamestate.save()
		doBasicSchooling()

	def end(self):
		cinematics.showCinematic("please try to remember the Information. The lesson will now continue with Movement.")
		phase2 = SecondTutorialPhase()
		phase2.start()

class SecondTutorialPhase(object):
	def __init__(self):
		self.name = "SecondTutorialPhase"

	def start(self):
		gamestate.currentPhase = self

		if not terrain.tutorialMachineRoom.secondOfficer:
			npc = characters.Character(displayChars.staffCharacters[11],4,3,name=names.characterFirstNames[(gamestate.tick+2)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)])
			npc.terrain = terrain
			npc.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc,4,3)
			terrain.tutorialMachineRoom.secondOfficer = npc
		npc = terrain.tutorialMachineRoom.secondOfficer

		if not terrain.tutorialMachineRoom.firstOfficer:
			npc2 = characters.Character(displayChars.staffCharacters[25],5,3,name=names.characterFirstNames[(gamestate.tick+9)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)])
			npc2.terrain = terrain
			npc2.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc2,5,3)
			terrain.tutorialMachineRoom.firstOfficer = npc2
		npc2 = terrain.tutorialMachineRoom.firstOfficer

		questList = []
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,5,5,startCinematics="Movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n "+commandChars.move_north+"=up\n "+commandChars.move_east+"=right\n "+commandChars.move_south+"=down\n "+commandChars.move_west+"=right\nplease move to the designated Target. the Implant will mark your Way"))
		if not mainChar.gotMovementSchooling:
			quest = quests.PatrolQuest([(terrain.tutorialMachineRoom,7,5),(terrain.tutorialMachineRoom,7,2),(terrain.tutorialMachineRoom,2,2),(terrain.tutorialMachineRoom,2,5)],startCinematics="now please patrol around the Room a few times.",lifetime=80)
			def setPlayerState():
				mainChar.gotMovementSchooling = True
			quest.endTrigger = setPlayerState
			questList.append(quest)
			questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="thats enough. move back to waiting position"))
		if not mainChar.gotExamineSchooling:
			quest = quests.ExamineQuest(lifetime=100,startCinematics="use e to examine items. you can get Descriptions and more detailed Information about your Environment than just by looking at things.\n\nto look at something you have to walk into or over the item and press "+commandChars.examine+". For example if you stand next to a Furnace like this:\n\n"+displayChars.furnace_inactive+displayChars.main_char+"\n\npressing "+commandChars.move_west+" and then "+commandChars.examine+" would result in the Description:\n\n\"this is a Furnace\"\n\nyou have 100 Ticks to familiarise yourself with the Movementcommands and to examine the Room. please do.")
			def setPlayerState():
				mainChar.gotExamineSchooling = True
			quest.endTrigger = setPlayerState
			questList.append(quest)
			questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="Move back to Waitingposition"))

		if not mainChar.gotInteractionSchooling:
			quest = quests.CollectQuest(startCinematics="next on my Checklist is to explain the Interaction with your Environment.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nsee this Piles of Coal marked with ӫ on the rigth Side and left Side of the Room.\n\nwhenever you bump into an Item that is to big to be walked on, you will promted for giving an extra Interactioncommand. i'll give you an Example:\n\n ΩΩ＠ӫӫ\n\n pressing "+commandChars.move_west+" and "+commandChars.activate+" would result in Activation of the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.activate+" would result in Activation of the Pile\n pressing "+commandChars.move_west+" and "+commandChars.examine+" would result make you examine the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.examine+" would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards.")
			def setPlayerState():
				mainChar.gotInteractionSchooling = True
				gamestate.save()
			quest.endTrigger = setPlayerState
			questList.append(quest)
		else:
			quest = quests.CollectQuest(startCinematics="Since you failed the Test last time i will quickly reiterate the interaction commands.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nmove over or walk into items and then press the interaction button to be able to interact with it.")
			questList.append(quest)
			
		questList.append(quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[0],startCinematics="now go and fire the top most Furnace."))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please pick up the Coal on the Floor. \n\nyou won't see a whole Year of Service leaving burnable Material next to a Furnace"))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please move back to the waiting position"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		questList[-1].endTrigger = self.end

		mainChar.assignQuest(questList[0])

	def end(self):
		gamestate.save()
		cinematics.showCinematic("you recieved your Preparatorytraining. Time for the Test.")
		phase = ThirdTutorialPhase()
		phase.start()

class ThirdTutorialPhase(object):
	def __init__(self):
		self.name = "ThirdTutorialPhase"

	def start(self):
		gamestate.currentPhase = self

		if not terrain.tutorialMachineRoom.secondOfficer:
			npc = characters.Character(displayChars.staffCharacters[11],4,3,name=names.characterFirstNames[(gamestate.tick+2)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)])
			npc.terrain = terrain
			npc.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc,4,3)
			terrain.tutorialMachineRoom.secondOfficer = npc
		self.npc = terrain.tutorialMachineRoom.secondOfficer

		if not terrain.tutorialMachineRoom.firstOfficer:
			npc2 = characters.Character(displayChars.staffCharacters[25],5,3,name=names.characterFirstNames[(gamestate.tick+9)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)])
			npc2.terrain = terrain
			npc2.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc2,5,3)
			terrain.tutorialMachineRoom.firstOfficer = npc2
		npc2 = terrain.tutorialMachineRoom.firstOfficer


		cinematics.showCinematic("during the Test Messages and new Task will be shown on the Buttom of the Screen. start now.")

		self.mainCharFurnaceIndex = 0
		self.npcFurnaceIndex = 0

		def endMainChar():
			cinematics.showCinematic("stop.")
			for quest in mainChar.quests:
				quest.deactivate()
			mainChar.quests = []
			terrain.tutorialMachineRoom.removeEventsByType(AnotherOne)
			mainChar.assignQuest(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please move back to the waiting position"))

			messages.append("your turn Ludwig")

			questList = []
			#questList.append(quests.FillPocketsQuest())
			#questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[1]))
			#questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[2]))
			questList.append(quests.FillPocketsQuest())

			lastQuest = questList[0]
			for item in questList[1:]:
				lastQuest.followUp = item
				lastQuest = item
			questList[-1].followup = None

			class AnotherOne2(object):
				def __init__(subself,tick,index):
					subself.tick = tick
					subself.furnaceIndex = index

				def handleEvent(subself):
					self.npc.assignQuest(quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[subself.furnaceIndex],failTrigger=self.end))
					newIndex = subself.furnaceIndex+1
					self.npcFurnaceIndex = subself.furnaceIndex
					if newIndex < 8:
						self.npc.assignQuest(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[newIndex]))
						terrain.tutorialMachineRoom.addEvent(AnotherOne2(gamestate.tick+gamestate.tick%20+10,newIndex))

			self.anotherOne2 = AnotherOne2

			class WaitForClearStart2(object):
				def __init__(subself,tick,index):
					subself.tick = tick

				def handleEvent(subself):
					boilerStillBoiling = False
					for boiler in terrain.tutorialMachineRoom.boilers:
						if boiler.isBoiling:
							boilerStillBoiling = True	
					if boilerStillBoiling:
						terrain.tutorialMachineRoom.addEvent(WaitForClearStart2(gamestate.tick+2,0))
					else:
						cinematics.showCinematic("Libwig start now.")
						self.npc.assignQuest(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[0]))
						terrain.tutorialMachineRoom.addEvent(AnotherOne2(gamestate.tick+10,0))

			def tmp2():
				terrain.tutorialMachineRoom.addEvent(WaitForClearStart2(gamestate.tick+2,0))

			questList[-1].endTrigger = tmp2
			self.npc.assignQuest(questList[0])

		class AnotherOne(object):
			def __init__(subself,tick,index):
				subself.tick = tick
				subself.furnaceIndex = index

			def handleEvent(subself):
				messages.append("another one")
				mainChar.assignQuest(quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[subself.furnaceIndex],failTrigger=endMainChar))
				newIndex = subself.furnaceIndex+1
				self.mainCharFurnaceIndex = subself.furnaceIndex
				if newIndex < 8:
					mainChar.assignQuest(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[newIndex]))
					terrain.tutorialMachineRoom.addEvent(AnotherOne(gamestate.tick+gamestate.tick%20+5,newIndex))

		class WaitForClearStart(object):
			def __init__(subself,tick,index):
				subself.tick = tick

			def handleEvent(subself):
				boilerStillBoiling = False
				for boiler in terrain.tutorialMachineRoom.boilers:
					if boiler.isBoiling:
						boilerStillBoiling = True	
				if boilerStillBoiling:
					terrain.tutorialMachineRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))
				else:
					cinematics.showCinematic("start now.")
					mainChar.assignQuest(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[0]))
					terrain.tutorialMachineRoom.addEvent(AnotherOne(gamestate.tick+10,0))

		def tmp():
			cinematics.showCinematic("wait for the furnaces to burn down.")
			terrain.tutorialMachineRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))

		tmp()

	def end(self):
		messages.append("your Score: "+str(self.mainCharFurnaceIndex))
		messages.append("Libwigs Score: "+str(self.npcFurnaceIndex))

		for quest in self.npc.quests:
			quest.deactivate()
		self.npc.quests = []
		terrain.tutorialMachineRoom.removeEventsByType(self.anotherOne2)
		mainChar.assignQuest(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please move back to the waiting position"))

		if self.npcFurnaceIndex >= self.mainCharFurnaceIndex:
			cinematics.showCinematic("considering your Score until now moving you directly to your proper assignment is the most efficent Way for you to proceed.")
			phase3 = VatPhase()
			phase3.start()
		elif self.mainCharFurnaceIndex == 7:
			cinematics.showCinematic("you passed the Test. in fact you passed the Test with a perfect Score. you will be valuable")
			phase3 = LabPhase()
			phase3.start()
		else:
			cinematics.showCinematic("you passed the Test. \n\nyour Score: "+str(self.mainCharFurnaceIndex)+"\nLibwigs Score: "+str(self.npcFurnaceIndex))
			phase3 = MachineRoomPhase()
			phase3.start()
		gamestate.save()


class LabPhase(object):
	def __init__(self):
		self.name = "LabPhase"

	def start(self):
		gamestate.currentPhase = self

		questList = []

		questList.append(quests.MoveQuest(terrain.tutorialLab,3,3,startCinematics="please move to the waiting position"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		questList[-1].endTrigger = self.end

		mainChar.assignQuest(questList[0])

	def end(self):
		cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
		SecondTutorialPhase().start()
		gamestate.save()

class VatPhase(object):
	def __init__(self):
		self.name = "VatPhase"

	def start(self):
		gamestate.currentPhase = self
	
		questList = []
		if not (mainChar.room and mainChar.room == terrain.tutorialVat):
			questList.append(quests.EnterRoomQuest(terrain.tutorialVat,startCinematics="please goto the Vat"))

		questList.append(quests.MoveQuest(terrain.tutorialVat,3,3,startCinematics="please move to the waiting position"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		questList[-1].endTrigger = self.end

		mainChar.assignQuest(questList[0])

	def end(self):
		cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
		SecondTutorialPhase().start()
		gamestate.save()

class MachineRoomPhase(object):
	def __init__(self):
		self.name = "MachineRoomPhase"

	def start(self):
		gamestate.currentPhase = self

		if not terrain.tutorialMachineRoom.firstOfficer:
			npc2 = characters.Character(displayChars.staffCharacters[25],5,3,name=names.characterFirstNames[(gamestate.tick+9)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)])
			npc2.terrain = terrain
			npc2.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc2,5,3)
			terrain.tutorialMachineRoom.firstOfficer = npc2
		npc2 = terrain.tutorialMachineRoom.firstOfficer

		terrain.tutorialMachineRoom.secondOfficer = mainChar

		terrain.tutorialMachineRoom.endTraining()

		questList = []
		if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
			questList.append(quests.EnterRoomQuest(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom"))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="time to do some actual work. report to "+terrain.tutorialMachineRoom.firstOfficer.name))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		mainChar.assignQuest(questList[0])

	def end(self):
		gamestate.gameWon = True
		gamestate.save()

def registerPhases():
	phasesByName["VatPhase"] = VatPhase
	phasesByName["MachineRoomPhase"] = MachineRoomPhase
	phasesByName["LabPhase"] = LabPhase
	phasesByName["FirstTutorialPhase"] = FirstTutorialPhase
	phasesByName["SecondTutorialPhase"] = SecondTutorialPhase
	phasesByName["ThirdTutorialPhase"] = ThirdTutorialPhase