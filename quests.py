showCinematic = None

class Quest(object):
	def __init__(self,followUp=None,startCinematics=None):
		self.followUp = followUp
		self.character = None
		self.listener = []
		self.active = False
		self.startCinematics=startCinematics

	def triggerCompletionCheck(self):
		if not self.active:
			return 
		pass
	
	def postHandler(self):
		self.character.quests.remove(self)
		if self.followUp:
			self.character.assignQuest(self.followUp,active=True)
		else:
			self.character.startNextQuest()

		if self.character.watched:
			messages.append("Thank you kindly. @"+self.character.name)
		
		self.deactivate()

	def assignToCharacter(self,character):
		self.character = character
		self.recalculate()

	def recalculate(self):
		if not self.active:
			return 

		self.triggerCompletionCheck()

	def changed(self):
		messages.append("QUEST: "+self.description+" changed")

	def addListener(self,listenFunction):
		if not listenFunction in self.listener:
			self.listener.append(listenFunction)

	def delListener(self,listenFunction):
		if listenFunction in self.listener:
			self.listener.remove(listenFunction)

	def activate(self):
		self.active = True
		if self.startCinematics:
			showCinematic(self.startCinematics)			
			try:
				loop.set_alarm_in(0.0, callShow_or_exit, '.')
			except:
				pass

	def deactivate(self):
		self.active = False

class CollectQuest(Quest):
	def __init__(self,toFind="canBurn",startCinematics=None):
		self.toFind = toFind
		self.description = "please fetch things with property: "+toFind
		
		foundItem = None

		super().__init__(startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		foundItem = None
		for item in self.character.inventory:
			hasProperty = False
			try:
				hasProperty = getattr(item,self.toFind)
			except:
				continue
			
			if hasProperty:
				foundItem = item
				break

		if foundItem:
			self.postHandler()
			pass

	def assignToCharacter(self,character):
		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def recalculate(self):
		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY

		if not self.active:
			return 

		try:
			for item in self.character.room.itemsOnFloor:
				hasProperty = False
				try:
					hasProperty = getattr(item,self.toFind)
				except:
					continue
				
				if hasProperty:
					foundItem = item
					break

			if foundItem:
				self.dstX = foundItem.xPosition
				self.dstY = foundItem.yPosition
		except:
			pass
		super().recalculate()

class ActivateQuest(Quest):
	def __init__(self,toActivate,followUp=None,desiredActive=True,startCinematics=None):
		self.toActivate = toActivate
		self.toActivate.addListener(self.recalculate)
		self.description = "please activate the "+self.toActivate.name+" ("+str(self.toActivate.xPosition)+"/"+str(self.toActivate.yPosition)+")"
		self.dstX = self.toActivate.xPosition
		self.dstY = self.toActivate.yPosition
		self.desiredActive = desiredActive
		super().__init__(followUp,startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if self.toActivate.activated == self.desiredActive:
			self.postHandler()

	def recalculate(self):
		if not self.active:
			return 

		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY
		if hasattr(self,"toActivate"):
			if hasattr(self.toActivate,"xPosition"):
				self.dstX = self.toActivate.xPosition
			if hasattr(self.toActivate,"xPosition"):
				self.dstY = self.toActivate.yPosition
		super().recalculate()

class MoveQuest(Quest):
	def __init__(self,room,x,y,followUp=None,startCinematics=None):
		self.dstX = x
		self.dstY = y
		self.targetX = x
		self.targetY = y
		self.room = room
		self.description = "please go to coordinate "+str(self.dstX)+"/"+str(self.dstY)	
		super().__init__(followUp,startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if hasattr(self,"dstX") and hasattr(self,"dstY"):
			if self.character.xPosition == self.dstX and self.character.yPosition == self.dstY:
				self.postHandler()

	def assignToCharacter(self,character):
		if not self.active:
			return 

		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def recalculate(self):
		if not self.active:
			return 

		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY
		if self.room == self.character.room:
			self.dstX = self.targetX
			self.dstY = self.targetY
		elif self.character.room and self.character.quests[0] == self:
			self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)
		super().recalculate()

class LeaveRoomQuest(Quest):
	def __init__(self,room,followUp=None,startCinematics=None):
		self.room = room
		self.description = "please leave the room."
		self.dstX = self.room.walkingAccess[0][0]
		self.dstY = self.room.walkingAccess[0][1]
		super().__init__(followUp,startCinematics=startCinematics)

	def assignToCharacter(self,character):
		if not self.active:
			return 

		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if not self.character.room == self.room:
			self.postHandler()
