import src.rooms
import src.items
import src.quests
import src.canvas
import time
import urwid

##################################################################################################################################
###
##        setting up the basic user interaction library
#         bad code: urwid specific code should be somewhere else
#
#################################################################################################################################

# the containers for the shown text
header = urwid.Text(u"")
main = urwid.Text(u"")
footer = urwid.Text(u"")
main.set_layout('left', 'clip')

frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)

##################################################################################################################################
###
##        the main interaction loop
#
#################################################################################################################################

# the keys that should not be handled like usual but are overwritten by other places
stealKey = {}
# bad code: common variables with modules
src.items.stealKey = stealKey

# timestamps for detecting periods in inactivity etc
lastLagDetection = time.time()
lastRedraw = time.time()

# states for stateful interaction
itemMarkedLast = None
lastMoveAutomated = False
fullAutoMode = False
idleCounter = 0
submenue = None
ignoreNextAutomated = False
ticksSinceDeath = None
levelAutomated = 0

# the state for the footer
# bad code: this should be contained in an object
footerInfo = []
footerText = ""
doubleFooterText = footerText+footerText
footerPosition = 0
footerLength = len(footerText)
footerSkipCounter = 20

'''
calculate footer text
'''
def setFooter():
    # bad code: global variables
    global footerInfo
    global footerText
    global doubleFooterText
    global footerPosition
    global footerLength
    global footerSkipCounter

    # calculate the text
    # bad pattern: footer should be dynamically generated
    footerInfo = [
    "@  = you",
    "XX = Wall",
    ":: = floor",
    "[] = door",
    "** = pipe",
    "is = scrap",
    "is = scrap",
    "oo / öö = furnce",
    "OO / 00 = growth tank",
    "|| / // = lever",
    "@a / @b ... @z = npcs",
    "xX = quest marker (your current target)",
    "press "+commandChars.show_help+" for help",
    "press "+commandChars.move_north+" to move north",
    "press "+commandChars.move_south+" to move south",
    "press "+commandChars.show_quests+" for quests",
    "press "+commandChars.show_quests_detailed+" for advanced quests",
    "press "+commandChars.show_inventory+" for inventory",
    "press "+commandChars.move_west+" to move west",
    "press "+commandChars.move_east+" to move east",
    "press "+commandChars.activate+" to activate",
    "press "+commandChars.pickUp+" to pick up",
    "press "+commandChars.hail+" to talk",
    "press "+commandChars.drop+" to drop",
    ]
    footerText = ", ".join(footerInfo)+", "
    doubleFooterText = footerText+footerText
    footerPosition = 0
    footerLength = len(footerText)
    footerSkipCounter = 20

'''
calls show_or_exit with on param less
bad code: keystrokes should not be injected in the first place
'''
def callShow_or_exit(loop,key):
    show_or_exit(key)

'''
the callback for urwid keystrokes
bad code: this is abused as the main loop for this game
'''
def show_or_exit(key):
    # store the commands for later processing
    commandKeyQueue = []
    commandKeyQueue.append(key)

    # transform and store the keystrokes that accumulated in pygame
    try:
        import pygame
        for item in pygame.event.get():
            try:
                key = item.unicode
                if key == "\x1b":
                    key = "esc"
                commandKeyQueue.append(key)
                debugMessages.append("pressed "+key+" ")
            except:
                pass
    except:
        pass

    # handle the keystrokes
    processAllInput(commandKeyQueue)

'''
the abstracted processing for keystrokes.
Takes a list of keystrokes, that have been converted to a common format
'''
def processAllInput(commandKeyQueue):
    for key in commandKeyQueue:
        processInput(key)

'''
handle a keystroke
bad code: there are way too much lines of code in this function
'''
def processInput(key):
    # ignore mouse interaction
    # bad pattern mouse input should be used
    if type(key) == tuple:
        return

    # bad code: global variables
    global lastLagDetection
    global idleCounter
    global pauseGame
    global submenue
    global ignoreNextAutomated
    global ticksSinceDeath

    # show the scrolling footer
    # bad code: this should be contained in an object
    if key in ("lagdetection",):
        # show the scrolling footer
        if (not submenue) and (not len(cinematics.cinematicQueue) or not cinematics.cinematicQueue[0].overwriteFooter):
            # bad code: global variables
            global footerPosition
            global footerLength
            global footerSkipCounter

            # scroll footer every 20 lagdetection events (about 2 seconds)
            # bad code: using the lagdetection as timer is abuse
            if footerSkipCounter == 20:
               footerSkipCounter = 0
               screensize = loop.screen.get_cols_rows()
               footer.set_text(doubleFooterText[footerPosition:screensize[0]-1+footerPosition])
               if footerPosition == footerLength:
                   footerPosition = 0
               else:
                   footerPosition += 1
            footerSkipCounter += 1

        # set the cinematic specific footer
        else:
            footerSkipCounter = 20
            if not submenue:
                footer.set_text(" "+cinematics.cinematicQueue[0].footerText)
            else:
                footer.set_text(" "+submenue.footerText)

    # handle lag detection
    # bad code: lagdetection is abused as a timer
    if key in ("lagdetection",):
        # trigger the next lagdetection keystroke
        loop.set_alarm_in(0.1, callShow_or_exit, "lagdetection")
        lastLagDetection = time.time()

        # advance the game if the character stays idle
        if len(cinematics.cinematicQueue) or pauseGame:
            return
        idleCounter += 1
        if idleCounter < 4:
            return
        else:
            if idleCounter%5 == 0:
                key = commandChars.wait
            else:
                return
    else:
        # reset activity counter
        idleCounter = 0

    # discard keysstrokes if they were not processed for too long
    if not key in (commandChars.autoAdvance, commandChars.quit_instant, commandChars.ignore,commandChars.quit_delete, commandChars.pause, commandChars.show_quests, commandChars.show_quests_detailed, commandChars.show_inventory, commandChars.show_inventory_detailed, commandChars.show_characterInfo):
        if lastLagDetection < time.time()-0.4:
            return

    pauseGame = False

    # repeat autoadvance keystrokes
    # bad code: keystrokes are abused here, a timer would be more appropriate
    if key in (commandChars.autoAdvance):
        if not ignoreNextAutomated:
            loop.set_alarm_in(0.2, callShow_or_exit, commandChars.autoAdvance)
        else:
            ignoreNextAutomated = False

    # handle a keystroke while on map or in cinemetic
    if not submenue:
        # bad code: global variables
        global itemMarkedLast
        global lastMoveAutomated

        # handle cinematics
        if len(cinematics.cinematicQueue):
            cinematic = cinematics.cinematicQueue[0]

            # allow to quit even in a cutscene
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                raise urwid.ExitMainLoop()

            # skip the cinematic if requested
            elif key in (commandChars.pause,commandChars.advance,commandChars.autoAdvance) and cinematic.skipable:
                cinematic.abort()
                cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
                loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
                return

            # advance the cutscene
            else:
                if not cinematic.advance():
                    return
                if not cinematic.background:
                    # bad code: changing the key mid function
                    key = commandChars.ignore

        # set the flag to advance the game
        doAdvanceGame = True
        if key in (commandChars.ignore):
            doAdvanceGame = False

        # invalidate input for unconcious char
        if mainChar.unconcious:
            key = commandChars.wait

        # show a few rounds after death and exit
        if mainChar.dead:
            if not ticksSinceDeath:
                ticksSinceDeath = gamestate.tick
            key = commandChars.wait
            if gamestate.tick > ticksSinceDeath+5:
                # destroy the gamestate
                # bad pattern should not allways destroy gamestate
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("you lost")
                saveFile.close()
                raise urwid.ExitMainLoop()

        # call callback if key was overwritten
        if key in stealKey:
            stealKey[key]()

        # handle the keystroke for a char on the map
        else:
            if key in ("´",):
                # open the debug menue
                if debug:
                    submenue = DebugMenu()
                else:
                    messages.append("debug not enabled")

            if key in (commandChars.quit_delete,):
                # destroy save and quit
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("reset")
                saveFile.close()
                raise urwid.ExitMainLoop()

            if key in (commandChars.quit_normal, commandChars.quit_instant):
                # save and quit
                gamestate.save()
                raise urwid.ExitMainLoop()

            if key in (commandChars.pause):
                # kill one of the autoadvance keystrokes
                # bad pattern: doesn't actually pause
                ignoreNextAutomated = True
                doAdvanceGame = False

            def moveCharacter(direction):
                # do inner room movement
                if mainChar.room:
                    item = mainChar.room.moveCharacterDirection(mainChar,direction)

                    # remeber items bumped into for possible interaction
                    if item:
                        messages.append("You cannot walk there "+str(direction))
                        messages.append("press "+commandChars.activate+" to apply")
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
                        return item
                # do movement on terrain
                # bad code: these calculation should be done elsewhere
                else:
                    # gather the rooms the character might have entered
                    if direction == "north":
                        bigX = (mainChar.xPosition)//15
                        bigY = (mainChar.yPosition-1)//15
                    elif direction == "south":
                        bigX = (mainChar.xPosition)//15
                        bigY = (mainChar.yPosition+1)//15
                    elif direction == "east":
                        bigX = (mainChar.xPosition+1)//15
                        bigY = (mainChar.yPosition)//15
                    elif direction == "west":
                        bigX = (mainChar.xPosition)//15
                        bigY = (mainChar.yPosition-1)//15

                    roomCandidates = []
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    def enterLocalised(room,localisedEntry):
                        # get the entry point in room coordinates
                        if localisedEntry in room.walkingAccess:
                            # check if the entry point is blocked (by a door)
                            for item in room.itemByCoordinates[localisedEntry]:
                                if not item.walkable:
                                    # print some info
                                    messages.append("you need to open the door first")
                                    messages.append("press "+commandChars.activate+" to apply")
                                    header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                    # remember the item for interaction and abort
                                    return item
                                # teleport the character into the room
                                room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                terrain.characters.remove(mainChar)
                        else:
                            messages.append("you cannot move there")

                    # check if character has entered a room
                    hadRoomInteraction = False
                    for room in roomCandidates:
                        # check north
                        if direction == "north":
                            # check if the character crossed the edge of the room
                            if room.yPosition*15+room.offsetY+room.sizeY == mainChar.yPosition:
                                if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
                                    if localisedEntry[1] == -1:
                                        localisedEntry = (localisedEntry[0],room.sizeY-1)

                        # check south
                        elif direction == "south":
                            # check if the character crossed the edge of the room
                            if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
                                if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)

                        # check east
                        elif direction == "east":
                            # check if the character crossed the edge of the room
                            if room.xPosition*15+room.offsetX == mainChar.xPosition+1:
                                if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = ((mainChar.xPosition-room.offsetX+1)%15,(mainChar.yPosition-room.offsetY)%15)

                        # check west
                        elif direction == "west":
                            # check if the character crossed the edge of the room
                            if room.xPosition*15+room.offsetX+room.sizeX == mainChar.xPosition:
                                if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = ((mainChar.xPosition-room.offsetX-1)%15,(mainChar.yPosition-room.offsetY)%15)

                        else:
                            debugMessages.append("moved into invalid direction: "+str(direction))

                        if hadRoomInteraction:
                            item = enterLocalised(room,localisedEntry)
                            if item:
                                return item

                    # handle walking without room interaction
                    if not hadRoomInteraction:
                        # get the items on the destination coordinate 
                        try:
                            if direction == "north":
                                foundItems = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition-1]
                            elif direction == "south":
                                foundItems = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition+1]
                            elif direction == "east":
                                foundItems = terrain.itemByCoordinates[mainChar.xPosition+1,mainChar.yPosition]
                            elif direction == "west":
                                foundItems = terrain.itemByCoordinates[mainChar.xPosition-1,mainChar.yPosition]
                        except Exception as e:
                            foundItems = []

                        # check for items blocking the move to the destination coordinate
                        foundItem = False
                        item = None
                        for item in foundItems:
                            if item and not item.walkable:
                                # print some info
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                # remember the item for interaction and abort
                                foundItem = True
                                break

                        # move the character
                        if not foundItem:
                            if direction == "north":
                                mainChar.yPosition -= 1
                            elif direction == "south":
                                mainChar.yPosition += 1
                            elif direction == "east":
                                mainChar.xPosition += 1
                            elif direction == "west":
                                mainChar.xPosition -= 1
                            mainChar.changed()

                        return item

            if key in (commandChars.move_north):
                itemMarkedLast = moveCharacter("north")
                if itemMarkedLast and not itemMarkedLast.walkable:
                    return
            if key in (commandChars.move_south):
                itemMarkedLast = moveCharacter("south")
                if itemMarkedLast and not itemMarkedLast.walkable:
                    return
            if key in (commandChars.move_east):
                itemMarkedLast = moveCharacter("east")
                if itemMarkedLast and not itemMarkedLast.walkable:
                    return
            if key in (commandChars.move_west):
                itemMarkedLast = moveCharacter("west")
                if itemMarkedLast and not itemMarkedLast.walkable:
                    return

            # murder the next available character
            # bad pattern: enemies kill on 1 distance so the player should be able to do so too
            if key in (commandChars.attack):
                if not "NaiveMurderQuest" in mainChar.solvers:
                    messages.append("you do not have the nessecary solver yet")
                else:
                    if mainChar.room:
                        for char in mainChar.room.characters:
                            if char == mainChar:
                                continue
                            if not (mainChar.xPosition == char.xPosition and mainChar.yPosition == char.yPosition):
                                continue
                            char.die()
                # bad code: no else, so characters can only be killed within rooms -_-

            # activate an item 
            if key in (commandChars.activate):
                if not "NaiveActivateQuest" in mainChar.solvers:
                    messages.append("you do not have the nessecary solver yet")
                else:
                    if itemMarkedLast:
                        # active marked item
                        itemMarkedLast.apply(mainChar)
                    else:
                        # active an item on floor
                        for item in mainChar.container.itemsOnFloor:
                            if item.xPosition == mainChar.xPosition and item.yPosition == mainChar.yPosition:
                                item.apply(mainChar)

            # examine an item 
            if key in (commandChars.examine):
                if not "ExamineQuest" in mainChar.solvers:
                    messages.append("you do not have the nessecary solver yet")
                else:
                    if itemMarkedLast:
                        mainChar.examine(itemMarkedLast)
                    else:
                        # examine an item on floor
                        for item in mainChar.container.itemsOnFloor:
                            if item.xPosition == mainChar.xPosition and item.yPosition == mainChar.yPosition:
                                mainChar.examine(itemMarkedLast)
                                break

            # drop first item from inventory
            # bad pattern: the user has to have the choice for what item to drop
            if key in (commandChars.drop):
                if not "NaiveDropQuest" in mainChar.solvers:
                    messages.append("you do not have the nessecary solver yet")
                else:
                    if len(mainChar.inventory):
                        mainChar.drop(mainChar.inventory[0])

            # drink from the first available item in inventory
            # bad pattern: the user has to have the choice for what item to drop
            # bad code: drinking should happen in character
            if key in (commandChars.drink):
                character = mainChar
                for item in character.inventory:
                    if isinstance(item,src.items.GooFlask):
                        if item.uses > 0:
                            item.apply(character)
                            break

            # pick up items
            if key in (commandChars.pickUp):
                if not "NaivePickupQuest" in mainChar.solvers:
                    messages.append("you do not have the nessecary solver yet")
                else:
                    if len(mainChar.inventory) > 10:
                        messages.append("you cannot carry more items")
                    else:
                        # get the position to pickup from
                        if itemMarkedLast:
                            pos = (itemMarkedLast.xPosition,itemMarkedLast.yPosition)
                        else:
                            pos = (mainChar.xPosition,mainChar.yPosition)

                        # pickup all items from this coordinate
                        itemByCoordinates = mainChar.container.itemByCoordinates
                        if pos in itemByCoordinates:
                            for item in itemByCoordinates[pos]:
                                item.pickUp(mainChar)

            # open chat partner selection
            if key in (commandChars.hail):
                submenue = ChatPartnerselection()

            mainChar.automated = False
            if key in (commandChars.advance,commandChars.autoAdvance):
                # do the next step for the main character
                if len(mainChar.quests):
                    lastMoveAutomated = True

                    mainChar.automated = True
                else:
                    pass
            elif not key in (commandChars.pause):
                # recalculate the questmarker since it could be tainted
                lastMoveAutomated = False
                if mainChar.quests:
                    mainChar.setPathToQuest(mainChar.quests[0])

        # drop the marker for interacting with an item after bumping into it 
        # bad code: ignore autoadvance opens up an unintended exploit
        if not key in ("lagdetection",commandChars.wait,commandChars.autoAdvance):
            itemMarkedLast = None

        # enforce 60fps
        # bad code: urwid specific code should be isolated
        global lastRedraw
        if lastRedraw < time.time()-0.016:
            loop.draw_screen()
            lastRedraw = time.time()

        specialRender = False

        # doesn't open the dev menu and toggles rendering mode instead
        # bad code: code should act as advertised
        if key in (commandChars.devMenu):
            if displayChars.mode == "unicode":
                displayChars.setRenderingMode("pureASCII")
            else:
                displayChars.setRenderingMode("unicode")

        # open quest menu
        if key in (commandChars.show_quests):
            submenue = QuestMenu()

        # open help menu
        if key in (commandChars.show_help):
            submenue = HelpMenu()

        # open inventory
        if key in (commandChars.show_inventory):
            submenue = InventoryMenu()

        # open the menu for giving quests
        if key in (commandChars.show_quests_detailed):
            submenue = AdvancedQuestMenu()

        # open the character information
        if key in (commandChars.show_characterInfo):
            submenue = CharacterInfoMenu()

        # open the help screen
        if key in (commandChars.show_help):
            specialRender = True        
            pauseGame = True

    # render submenues
    if submenue:
        # set flag to not render the game
        specialRender = True        
        pauseGame = True

        # let the submenu handle the keystroke
        if not key in (commandChars.autoAdvance):
            done = submenue.handleKey(key)
        else:
            done = False

        if done:
            submenue = None
            pauseGame = False
            specialRender = False
            doAdvanceGame = False
        
    # render the game
    if not specialRender:
        
        # advance the game
        if doAdvanceGame:
            if mainChar.satiation < 30 and mainChar.satiation > -1:
                if mainChar.satiation == 0:
                    messages.append("you starved")
                else:
                    messages.append("you'll starve in "+str(mainChar.satiation)+" ticks!")
            advanceGame()

        # render information on top
        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

        # render map
        # bad code: display mode specific code
        canvas = render()
        main.set_text((urwid.AttrSpec("#999","black"),canvas.getUrwirdCompatible()));
        if (useTiles):
            canvas.setPygameDisplay(pydisplay,pygame,tileSize)

    # show the game won screen
    if gamestate.gameWon:
        main.set_text((urwid.AttrSpec("default","default"),""))
        main.set_text((urwid.AttrSpec("default","default"),"credits"))
        header.set_text((urwid.AttrSpec("default","default"),"good job"))

'''
The base class for submenues offer selections
bad code: there is redundant code from the specific submenus that should be put here
'''
class SubMenu(object):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        self.persistentText = ""
        self.footerText = "press w / s to move selection up / down, press enter / j / k to select"
        self.followUp = None
        super().__init__()

    '''
    sets the options to select from
    '''
    def setOptions(self, query, options):
        # convert options to ordered dict
        import collections
        self.options = collections.OrderedDict()
        self.niceOptions = collections.OrderedDict()
        counter = 1
        for option in options:
            self.options[str(counter)] = option[0]
            self.niceOptions[str(counter)] = option[1]
            counter += 1

        # set related state
        self.query = query
        self.selectionIndex = 1
        self.lockOptions = True
        self.selection = None

    '''
    straightforward getter for the selected item
    '''
    def getSelection(self):
        return self.selection

    '''
    show the options and allow the user to select one
    '''
    def handleKey(self, key):
        if key == "esc":
            return True

        out = "\n"
        out += self.query+"\n"

        if not self.lockOptions:
            if key == "w":
                # change the marked option
                self.selectionIndex -= 1
                if self.selectionIndex == 0:
                    self.selectionIndex = len(self.options)
            if key == "s":
                # change the marked option
                self.selectionIndex += 1
                if self.selectionIndex > len(self.options):
                    self.selectionIndex = 1
            if key in ["enter","j","k"]:
                # select the marked option
                # bad code: transforming the key to the shortcut is needlessly complicated
                key = list(self.options.items())[self.selectionIndex-1][0]

            # select option by shortcut
            if key in self.options:
                self.selection = self.options[key]
                self.options = None
                if self.followUp:
                    self.followUp()
                return True
        else:
             self.lockOptions = False

        # render the options
        counter = 0
        for k,v in self.niceOptions.items():
            counter += 1
            if counter == self.selectionIndex:
                out += str(k)+" ->"+str(v)+"\n"
            else:
                out += str(k)+" - "+str(v)+"\n"

        # show the rendered options 
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText+"\n\n"+out))

        return False

    '''
    set text in urwid
    bad code: should either be used everywhere or be removed
    bad code: urwid specific code
    '''
    def set_text(self,text):
        main.set_text((urwid.AttrSpec("default","default"),text))

'''
does a simple selection and terminates
bad code: this does nothing the Submenu doesn't do
'''
class SelectionMenu(SubMenu):
    '''
    set up the selection
    '''
    def __init__(self, text, options):
        super().__init__()
        self.setOptions(text, options)

    '''
    handles the key
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True
        header.set_text("")

        # let superclass handle the actual selection
        if not self.getSelection():
             super().handleKey(key)

        # stop when done
        if self.getSelection():
            return True
        else:
            return False

'''
Spawns a Chat submenu with a player selected character
bad code: only works within rooms right now
bad code: since there is no need to wait for some return this submenue should not wrap around the Chat menu
bad code: sub menues should be implemented in the base class
'''
class ChatPartnerselection(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__()
        self.subMenu = None

    '''
    set up the selection and spawn the chat 
    '''
    def handleKey(self, key):
        # wrap around the chat menu
        if self.subMenu:
            return self.subMenu.handleKey(key)

        if key == "esc":
            # abort
            return True

        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        # offer the player to select from characters in room
        # bad code: should be done in __init__
        if not self.options and not self.getSelection():
            options = []
            if mainChar.room:
                # get characters in room
                for char in mainChar.room.characters:
                    if char == mainChar:
                        continue
                    options.append((char,char.name))
            else:
                # get character on terrain
                for char in mainChar.terrain.characters:
                    if char == mainChar:
                        continue
                    options.append((char,char.name))

                # get nearby rooms
                bigX = mainChar.xPosition//15
                bigY = mainChar.yPosition//15
                rooms = []
                coordinates = [(bigX,bigY),(bigX-1,bigY),(bigX+1,bigY),(bigX,bigY-1),(bigX,bigY+1)]
                for coordinate in coordinates:
                    if not coordinate in terrain.roomByCoordinates:
                        continue
                    rooms.extend(terrain.roomByCoordinates[coordinate])

                # add character from nearby open rooms
                for room in rooms:
                    if not room.open:
                        continue 

                    for char in room.characters:
                        options.append((char,char.name))
                
            self.setOptions("talk with whom?",options)

        # delegate the actual selection to the super class
        if not self.getSelection():
             super().handleKey(key)

        if self.getSelection():
            # spawn the chat submenu
            self.subMenu = ChatMenu(self.selection)
            self.subMenu.handleKey(key)
        else:
            return False

'''
the chat option for recruiting a character
# bad code: should be in chats.py
'''
class RecruitChat(SubMenu):
    dialogName = "follow my orders." # the name for this chat when presented as dialog option

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        super().__init__()

    '''
    show dialog and recruit character depending on success
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog and reactions should be generated within the characters
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True

        if self.firstRun:
            # add player text
            self.persistentText += mainChar.name+": \"come and help me.\"\n"

            if self.partner.reputation > mainChar.reputation:
                # reject player
                if mainChar.reputation <= 0:
                    # reject player very harshly
                    self.persistentText += self.partner.name+": \"No.\""
                    mainChar.reputation -= 5
                    messages.append("You were rewarded -5 reputation")
                else:
                    if self.partner.reputation//mainChar.reputation:
                        # reject player harshly
                        self.persistentText += self.partner.name+": \"you will need at least have to have "+str(self.partner.reputation//mainChar.reputation)+" times as much reputation to have me consider that\"\n"
                        messages.append("You were rewarded -"+str(2*(self.partner.reputation//mainChar.reputation))+" reputation")
                        mainChar.reputation -= 2*(self.partner.reputation//mainChar.reputation)
                    else:
                        # reject player somewhat nicely
                        self.persistentText += self.partner.name+": \"maybe if you come back later\""
                        mainChar.reputation -= 2
                        messages.append("You were rewarded -2 reputation")
            else:
                if gamestate.tick%2:
                    # reject player
                    self.persistentText += self.partner.name+": \"sorry, too busy.\"\n"
                    mainChar.reputation -= 1
                    messages.append("You were rewarded -1 reputation")
                else:
                    # allow the recruitment
                    self.persistentText += self.partner.name+": \"on it!\"\n"
                    mainChar.subordinates.append(self.partner)
            text = self.persistentText+"\n\n-- press any key --"
            main.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        else:
            # continue after the first keypress
            # bad code: the first keystroke is the second keystroke that is handled
            self.done = True
            return False

'''
a chat with a character, partially hardcoded partially dynamically generated 
bad code: sub menues should be implemented in the base class
'''
class ChatMenu(SubMenu):

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.subMenu = None
        self.skipTurn = False
        super().__init__()

    '''
    show the dialog options and wrap the corresponding submenus
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog should be generated within the characters
    '''
    def handleKey(self, key):
        if self.partner.unconcious:
            # wake up character instead of speaking
            messages.append("wake up!")
            self.partner.wakeUp()
            return True

        if key == "esc":
           # abort
           if self.partner.reputation < 2*mainChar.reputation:
               return True
           else:
               # refuse to abort the chat
               self.persistentText = self.partner.name+": \""+mainChar.name+" improper termination of conversion is not compliant with the communication protocol IV. \nProper behaviour is expected.\"\n"
               mainChar.reputation -= 1
               messages.append("you were rewarded -1 reputation")
               main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
               self.skipTurn = True
               return False
                             
        if self.skipTurn:
           self.skipTurn = False
           key = "."

        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        # wrap around chat submenue
        if self.subMenu:
            # let the submenue handle the key
            if not self.subMenu.done:
                self.subMenu.handleKey(key)
                if not self.subMenu.done:
                    return False

            # return to main dialog menu
            self.subMenu = None
            self.state = "mainOptions"
            self.selection = None
            self.lockOptions = True
            self.options = []

        # display greetings
        if self.state == None:
            self.state = "mainOptions"
            self.persistentText += self.partner.name+": \"Everything in Order, "+mainChar.name+"?\"\n"
            self.persistentText += mainChar.name+": \"All sorted, "+self.partner.name+"!\"\n"

        # show selection of sub chats
        if self.state == "mainOptions":
            # set up selection for the main dialog options 
            if not self.options and not self.getSelection():
                # add the chat partners special dialog options
                options = []
                for option in self.partner.getChatOptions(mainChar):
                    if not isinstance(option,dict):
                        options.append((option,option.dialogName))
                    else:
                        options.append((option,option["dialogName"]))

                # add default dialog options
                options.append(("showQuests","what are you dooing?"))
                options.append(("exit","let us proceed, "+self.partner.name))

                # set the options
                self.setOptions("answer:",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            # spawn the dialog options submenu
            if self.getSelection():
                if not isinstance(self.selection,str):
                    # spawn the selected dialog option
                    if not isinstance(self.selection,dict):
                        self.subMenu = self.selection(self.partner)
                    else:
                        self.subMenu = self.selection["chat"](self.partner)
                        if "params" in self.selection:
                            self.subMenu.setUp(self.selection["params"])

                    self.subMenu.handleKey(key)
                elif self.selection == "showQuests":
                    # spawn quest submenu for partner
                    global submenue
                    submenue = QuestMenu(char=self.partner)
                    submenue.handleKey(key)
                    return False
                elif self.selection == "exit":
                    # end the conversation
                    self.state = "done"
                self.selection = None
                self.lockOptions = True
            else:
                return False

        # say goodbye
        if self.state == "done":
            if self.lockOptions:
                self.persistentText += self.partner.name+": \"let us proceed, "+mainChar.name+".\"\n"
                self.persistentText += mainChar.name+": \"let us proceed, "+self.partner.name+".\"\n"
                self.lockOptions = False
            else:
                return True

        # show redered text via urwid
        # bad code: urwid code should be somewere else
        if not self.subMenu:
            main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
minimal debug ability
'''
class DebugMenu(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self,char=None):
        super().__init__()
        self.firstRun = True

    '''
    show some debug output
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True

        if self.firstRun:
            # bad code: unstructured chaos
            import objgraph
            #objgraph.show_backrefs(mainChar, max_depth=4)
            """
            msg = ""
            for item in objgraph.most_common_types(limit=50):
                msg += ("\n"+str(item))
            main.set_text(msg)

            constructionSite = terrain.roomByCoordinates[(4,2)][0]
            quest = quests.ConstructRoom(constructionSite,terrain.tutorialStorageRooms)
            mainChar.assignQuest(quest,active=True)
            """

            # show debug output
            main.set_text(str(terrain.tutorialStorageRooms[3].storageSpace)+"\n"+str(list(reversed(terrain.tutorialStorageRooms[3].storageSpace)))+"\n\n"+str(terrain.tutorialStorageRooms[3].storedItems))
            self.firstRun = False
            return False
        else:
            return True

'''
show the quests for a character and allow player interaction
'''
class QuestMenu(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self,char=None):
        self.lockOptions = True
        if not char:
            char = mainChar
        self.char = char
        self.offsetX = 0
        self.questIndex = 0
        super().__init__()

    '''
    show a questlist and handle interactions
    overrides the superclasses method completely
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True

        # scrolling
        # bad code: doesn't actually work
        if key == "W":
            self.offsetX -= 1
        if key == "S":
            self.offsetX += 1
        if self.offsetX < 0:
            self.offsetX = 0

        # move the marker that marks the selected quest
        if key == "w":
            self.questIndex -= 1
        if key == "s":
            self.questIndex += 1
        if self.questIndex < 0:
            self.questIndex = 0
        if self.questIndex > len(self.char.quests)-1:
            self.questIndex = len(self.char.quests)-1

        # make the selected quest active
        if key == "j":
            if self.questIndex:
                quest = self.char.quests[self.questIndex]
                self.char.quests.remove(quest)
                self.char.quests.insert(0,quest)
                self.char.setPathToQuest(quest)
                self.questIndex = 0

        # render the quests
        addition = ""
        if self.char == mainChar:
            addition = " (you)"
        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview for "+self.char.name+""+addition+"\n(press "+commandChars.show_quests_detailed+" for the extended quest menu)\n\n"))
        self.persistentText = []
        self.persistentText.append(renderQuests(char=self.char,asList=True,questIndex = self.questIndex))

        if not self.lockOptions:
            if key in ["q"]:
                # spawn the quest menu for adding quests
                global submenue
                submenue = AdvancedQuestMenu()
                submenue.handleKey(key)
                return False
        self.lockOptions = False

        self.persistentText.extend(["\n","* press q for advanced quests\n","* press W to scroll up","\n","* press S to scroll down","\n","\n"])

        # flatten the mix of strings and urwid format so that it is less recursive to workaround an urwid bug
        # bad code: should be elsewhere
        def flatten(pseudotext):
            newList = []
            for item in pseudotext:
                if isinstance(item,list):
                   for subitem in flatten(item):
                      newList.append(subitem) 
                elif isinstance(item,tuple):
                   newList.append((item[0],flatten(item[1])))
                else:
                   newList.append(item)
            return newList
        self.persistentText = flatten(self.persistentText)

        # show rendered quests via urwid
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
show the players inventory
bad code: should be abstracted
bad code: uses global functions to render
'''
class InventoryMenu(SubMenu):
    '''
    show the inventory
    bad pattern: no player interaction
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True

        global submenue

        # bad pattern: detailed inventory does not exist
        header.set_text((urwid.AttrSpec("default","default"),"\ninventory overview\n(press "+commandChars.show_inventory_detailed+" for the extended inventory menu)\n\n"))

        # bad code: uses global function
        self.persistentText = (urwid.AttrSpec("default","default"),renderInventory())

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
show the players attributes
bad code: should be abstracted
bad code: uses global function to render
'''
class CharacterInfoMenu(SubMenu):
    '''
    show the attributes
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True

        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\ncharacter overview"))
        main.set_text((urwid.AttrSpec("default","default"),[mainChar.getDetailedInfo()]))
        header.set_text((urwid.AttrSpec("default","default"),""))

'''
player interaction for delegating a quest
'''
class AdvancedQuestMenu(SubMenu):
    '''
    straighforwad state initalisation
    '''
    def __init__(self):
        self.character = None
        self.quest = None
        self.questParams = {}
        super().__init__()

    '''
    gather the quests parameters and assign the quest
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True

        # start rendering
        header.set_text((urwid.AttrSpec("default","default"),"\nadvanced Quest management\n"))
        out = "\n"
        if self.character:
            out += "character: "+str(self.character.name)+"\n"
        if self.quest:
            out += "quest: "+str(self.quest)+"\n"
        out += "\n"

        # let the player select the character to assign the quest to 
        if self.state == None:
            self.state = "participantSelection"
        if self.state == "participantSelection":
            # set up the options
            if not self.options and not self.getSelection():
                # add the main player as target
                options = []
                options.append((mainChar,mainChar.name+" (you)"))

                # add the main players subordinates as target
                for char in mainChar.subordinates:
                    options.append((char,char.name))
                self.setOptions("whom to give the order to: ",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)
                
            # store the character to assign the quest to
            if self.getSelection():
                self.state = "questSelection"
                self.character = self.selection
                self.selection = None
                self.lockOptions = True
            else:
                return False

        # let the player select the type of quest to create
        if self.state == "questSelection":
            # add a list of quests
            if not self.options and not self.getSelection():
                options = []
                for key,value in src.quests.questMap.items():

                    # show only quests the chractre has done
                    if not key in mainChar.questsDone:
                        continue

                    # do not show naive quests
                    if key.startswith("Naive"):
                        continue

                    options.append((value,key))
                self.setOptions("what type of quest:",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            # store the type of quest to create
            if self.getSelection():
                self.state = "parameter selection"
                self.quest = self.selection
                self.selection = None
                self.lockOptions = True
                self.questParams = {}
            else:
                return False

        # let the player select the parameters for the quest
        if self.state == "parameter selection":
            if self.quest == src.quests.EnterRoomQuestMeta:
                # set up the options
                if not self.options and not self.getSelection():
                    # add a list of of rooms
                    options = []
                    for room in terrain.rooms:
                        # do not show unimportant rooms
                        if isinstance(room,src.rooms.MechArmor) or isinstance(room,src.rooms.CpuWasterRoom):
                            continue
                        options.append((room,room.name))
                    self.setOptions("select the room:",options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key)

                # store the parameter
                if self.getSelection():
                    self.questParams["room"] = self.selection
                    self.state = "confirm"
                    self.selection = None
                    self.lockOptions = True
                else:
                    return False

            elif self.quest == src.quests.StoreCargo:
                # set up the options for selecting the cargo room
                if "cargoRoom" not in self.questParams:
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in terrain.rooms:
                            # show only cargo rooms
                            if not isinstance(room,src.rooms.CargoRoom):
                                continue
                            options.append((room,room.name))
                        self.setOptions("select the room:",options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["cargoRoom"] = self.selection
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
                else:
                    # set up the options for selecting the storage room
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in terrain.rooms:
                            # show only storage rooms
                            if not isinstance(room,src.rooms.StorageRoom):
                                continue
                            options.append((room,room.name))
                        self.setOptions("select the room:",options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["storageRoom"] = self.selection
                        self.state = "confirm"
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
            else:
                # skip parameter selection
                self.state = "confirm"

        # get confirmation and assign quest
        if self.state == "confirm":
            # set the options for confirming the selection
            if not self.options and not self.getSelection():
                options = [("yes","yes"),("no","no")]
                if self.quest == src.quests.EnterRoomQuestMeta:
                    self.setOptions("you chose the following parameters:\nroom: "+str(self.questParams)+"\n\nDo you confirm?",options)
                else:
                    self.setOptions("Do you confirm?",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            if self.getSelection():
                if self.selection == "yes":
                    # instanciate quest
                    # bad code: repetive code
                    if self.quest == src.quests.MoveQuestMeta:
                       questInstance = self.quest(mainChar.room,2,2,creator=void)
                    elif self.quest == src.quests.ActivateQuestMeta:
                       questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0],creator=void)
                    elif self.quest == src.quests.EnterRoomQuestMeta:
                       questInstance = self.quest(self.questParams["room"],creator=void)
                    elif self.quest == src.quests.FireFurnaceMeta:
                       questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0],creator=void)
                    elif self.quest == src.quests.WaitQuest:
                       questInstance = self.quest(creator=void)
                    elif self.quest == src.quests.LeaveRoomQuest:
                       try:
                           questInstance = self.quest(self.character.room,creator=void)
                       except:
                           pass
                    elif self.quest == src.quests.ClearRubble:
                       questInstance = self.quest(creator=void)
                    elif self.quest == src.quests.RoomDuty:
                       questInstance = self.quest(creator=void)
                    elif self.quest == src.quests.ConstructRoom:
                       for room in terrain.rooms:
                           if isinstance(room,src.rooms.ConstructionSite):
                               constructionSite = room
                               break
                       questInstance = self.quest(constructionSite,terrain.tutorialStorageRooms,creator=void)
                    elif self.quest == src.quests.StoreCargo:
                       for room in terrain.rooms:
                           if isinstance(room,src.rooms.StorageRoom):
                               storageRoom = room
                       questInstance = self.quest(self.questParams["cargoRoom"],self.questParams["storageRoom"],creator=void)
                    elif self.quest == src.quests.MoveToStorage:
                       questInstance = self.quest([terrain.tutorialLab.itemByCoordinates[(1,9)][0],terrain.tutorialLab.itemByCoordinates[(2,9)][0]],terrain.tutorialStorageRooms[1],creator=void)
                    else:
                       questInstance = self.quest(creator=void)

                    # show some fluff
                    if not self.character == mainChar:
                       self.persistentText += self.character.name+": \"understood?\"\n"
                       self.persistentText += mainChar.name+": \"understood and in execution\"\n"

                    # assign the quest
                    self.character.assignQuest(questInstance, active=True)

                    self.state = "done"
                else:
                    # reset progress
                    self.state = "questSelection"
                    
                self.selection = None
                self.lockOptions = False
            else:
                return False

        # close submenu
        if self.state == "done":
            if self.lockOptions:
                self.lockOptions = False
            else:
                return True

        # show rendered text via urwid
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
render the information section on top of the screen
bad pattern: should be configurable
'''
def renderHeader():
    # render the sections to display
    questSection = renderQuests(maxQuests=2)
    messagesSection = renderMessages()

    # calculate the size of the elements
    screensize = loop.screen.get_cols_rows()
    questWidth = (screensize[0]//3)-2
    messagesWidth = screensize[0]-questWidth-3

    # prepare for rendering the header
    txt = ""
    counter = 0
    splitedQuests = questSection.split("\n")
    splitedMessages = messagesSection.split("\n")
    rowCounter = 0

    # add header lines
    continueLooping = True
    questLine = ""
    messagesLine = ""
    while True:
        # get the next line for each element
        if questLine == "" and len(splitedQuests):
            questLine = splitedQuests.pop(0)
        if messagesLine == "" and len(splitedMessages):
            messagesLine = splitedMessages.pop(0)

        # stop adding lines after some rounds
        rowCounter += 1
        if (rowCounter > 5):
            break

        if len(questLine) > questWidth:
            # cut off left line
            txt += questLine[:questWidth]+"┃ "
            questLine = questLine[questWidth:]
        else:
            # padd left line
            txt += questLine+" "*(questWidth-len(questLine))+"┃ "
            # bug?: doen't this pop twice?
            if splitedQuests:
                questLine = splitedQuests.pop(0)
            else:
                questLine = ""

        if len(messagesLine) > messagesWidth:
            # cut off right line
            txt += messagesLine[:messagesWidth]
            messagesLine = messagesLine[messagesWidth:]
        else:
            txt += messagesLine
            # bug?: doen't this pop twice?
            if splitedMessages:
                messagesLine = splitedMessages.pop(0)
            else:
                messagesLine = ""
        txt += "\n"
            
    # add the lower decoration
    txt += "━"*+questWidth+"┻"+"━"*(screensize[0]-questWidth-1)+"\n"

    return txt

'''
render the last x messages into a string
'''
def renderMessages(maxMessages=5):
    txt = ""
    if len(messages) > maxMessages:
        for message in messages[-maxMessages+1:]:
            txt += str(message)+"\n"
    else:
        for message in messages:
            txt += str(message)+"\n"

    return txt


'''
render the quests into a string or list
bad code: the asList and questIndex parameters are out of place
'''
def renderQuests(maxQuests=0,char=None, asList=False, questIndex=0):
    # basic set up
    if not char:
        char = mainChar
    if asList:
        txt = []
    else:
        txt = ""

    if len(char.quests):
        # render the quests
        counter = 0
        for quest in char.quests:
            # render quest
            if asList:
                if counter == questIndex:
                    txt.extend([(urwid.AttrSpec("#0f0","default"),"QUEST: "),quest.getDescription(asList=asList,colored=True,active=True),"\n"])
                else:
                    txt.extend([(urwid.AttrSpec("#090","default"),"QUEST: "),quest.getDescription(asList=asList,colored=True),"\n"])
            else:
                txt+= "QUEST: "+quest.getDescription(asList=asList)+"\n"

            # break if maximum reached
            counter += 1
            if counter == maxQuests:
                break
    else:
        # return placeholder for no quests
        if asList:
            txt.append("No Quest")
        else:
            txt += "No Quest"

    return txt

'''
render the inventory of the player into a string
'''
def renderInventory():
    char = mainChar
    txt = []
    if len(char.inventory):
        for item in char.inventory:
            if isinstance(item.display,int):
                txt.extend([displayChars.indexedMapping[item.display]," - ",item.name,"\n     ",item.getDetailedInfo(),"\n"])
            else:
                txt.extend([item.display," - ",item.name,"\n     ",item.getDetailedInfo(),"\n"])
    else:
        txt = "empty Inventory"
    return txt

'''
the help submenue
bad code: uses global function to render
'''
class HelpMenu(SubMenu):
    '''
    show the help text
    '''
    def handleKey(self, key):
        if key == "esc":
            # abort
            return True
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview\n\n"))

        self.persistentText = ""

        self.persistentText += renderHelp()

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
return the help text
bad code: should not be a global function
'''
def renderHelp():
    char = mainChar
    txt = "the Goal of the Game is to stay alive and to gain Influence.\nThe daily Grind can be delageted to subordinates.\nBe useful, gain Power and use your Power to be more useful.\n\n"
    txt += "your keybindings are:\n\n"
    txt += "* move_north: "+commandChars.move_north+"\n"
    txt += "* move_east: "+commandChars.move_east+"\n"
    txt += "* move_west: "+commandChars.move_west+"\n"
    txt += "* move_south: "+commandChars.move_south+"\n"
    txt += "* activate: "+commandChars.activate+"\n"
    txt += "* drink: "+commandChars.drink+"\n"
    txt += "* pickUp: "+commandChars.pickUp+"\n"
    txt += "* drop: "+commandChars.drop+"\n"
    txt += "* hail: "+commandChars.hail+"\n"
    txt += "* examine: "+commandChars.examine+"\n"
    txt += "* quit_normal: "+commandChars.quit_normal+"\n"
    txt += "* quit_instant: "+commandChars.quit_instant+"\n"
    txt += "* quit_delete: "+commandChars.quit_delete+"\n"
    txt += "* autoAdvance: "+commandChars.autoAdvance+"\n"
    txt += "* advance: "+commandChars.advance+"\n"
    txt += "* pause: "+commandChars.pause+"\n"
    txt += "* ignore: "+commandChars.ignore+"\n"
    txt += "* wait: "+commandChars.wait+"\n"
    txt += "* show_quests "+commandChars.show_quests+"\n"
    txt += "* show_quests_detailed: "+commandChars.show_quests_detailed+"\n"
    txt += "* show_inventory: "+commandChars.show_inventory+"\n"
    txt += "* show_inventory_detailed: "+commandChars.show_inventory_detailed+"\n"
    txt += "* show_characterInfo: "+commandChars.show_characterInfo+"\n"
    txt += "* redraw: "+commandChars.redraw+"\n"
    txt += "* show_help: "+commandChars.show_help+"\n"
    txt += "* attack: "+commandChars.attack+"\n"
    txt += "* devMenu: "+commandChars.devMenu+"\n"
    return txt
    
'''
render the map
'''
def render():
    # render the map
    chars = terrain.render()

    # center on player
    if mainChar.room:
        centerX = mainChar.room.xPosition*15+mainChar.room.offsetX+mainChar.xPosition
        centerY = mainChar.room.yPosition*15+mainChar.room.offsetY+mainChar.yPosition
    else:
        centerX = mainChar.xPosition
        centerY = mainChar.yPosition

    # set size of the window into the world
    viewsize = 41
    halfviewsite = (viewsize-1)//2

    # calculate the windows position
    screensize = loop.screen.get_cols_rows()
    decorationSize = frame.frame_top_bottom(loop.screen.get_cols_rows(),True)
    screensize = (screensize[0]-decorationSize[0][0],screensize[1]-decorationSize[0][1])
    shift = (screensize[1]//2-20,screensize[0]//4-20)

    # place rendering in screen
    canvas = src.canvas.Canvas(size=(viewsize,viewsize),chars=chars,coordinateOffset=(centerY-halfviewsite,centerX-halfviewsite),shift=shift,displayChars=displayChars)

    return canvas

# get the interaction loop from the library
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)

# kick of the interaction loop
loop.set_alarm_in(0.2, callShow_or_exit, "lagdetection")
loop.set_alarm_in(0.0, callShow_or_exit, "~")

