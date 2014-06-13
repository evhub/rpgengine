#!/usr/bin/python

# NOTE:
# This is the code. If you are seeing this when you open the program normally, please follow the steps here:
# https://sites.google.com/site/evanspythonhub/having-problems

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO AREA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Program by: Evan
# EDITOR made in 2012
# This program allows dynamic mathematical processing over RPG statistics.

# To-Do:
# - non-dm hosting

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CONFIG AREA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Controls general debugging:
debug = False

# Controls automatic roll sending:
sendroll = True

# Controls turn restrictions:
override = False

# Determines the speed of connections:
speed = 400

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DATA AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from rabbit.all import *

def customformat(inputstring):
    inputstring = delspace(superformat(inputstring))
    if inputstring == "n,a":
        inputstring = "0/0"
    outstring = ""
    for x in inputstring.split(","):
        if x.startswith("+"):
            x = x[1:]
        outstring += x+","
    return outstring[:-1]

def remparens(inputstring):
    return inputstring.replace("(","").replace(")","").replace("[","").replace("]","")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class main(mathbase):
    helpstring = """Basic Commands:
    <command> [;; <command> ;; <command>...]
    <name> [:]= <expression>
Expressions:
    <item>, [<item>, <item>...]
    <function> [:](<variables>)[:(<variables>):(<variables>)...]
    <expression> [@<condition>[; <expression>@<condition>; <expression>@<condition>;... <expression>]]
    "string"
Console Commands:
    show <expression>
    help [string]
    errors
    clear
    clean
Character Commands:
    roll <modifier>
    deal <damage>
    cast <level>
    casts
    rest
    weapons
    equip <weapon>
    skills
    status
    character
Game Commands:
    join <port> <address>
    host <port> <connections>
    encounter
    chat
    username
    disconnect
    battle
    done
    hold
    end
    wipe
    open
Control Commands:
    do <command>
    del <variable>
    get [variable]
Import Commands:
    <name> = import <file>
    run <file>
    save <file>"""

    def __init__(self, override=False, sendroll=False, debug=False, speed=400, height=10):
        self.oldshow = lambda *args: mathbase.show(self, *args)
        self.debug = int(debug)
        self.printdebug(": ON")
        self.speed = speed
        self.override = override
        self.sendroll = sendroll
        self.root, self.app, self.box = startconsole(self.handler, "Loading RPGEngine...", "RPGEngine", height)
        self.show = self.app.display
        self.errorlog = {}
        self.returned = 1
        self.ans = [matrix(0)]
        self.populator()
        self.load()
        self.server = -1
        self.turn = -1
        self.x = -1
        self.talk = 0
        self.encounter = 0
        if not self.evalfile("Rules.txt"):
            popup("Error", "Error finding Rules.txt for import.")
            self.app.display("Unable to find Rules.txt for import.")
        if self.debug:
            self.debugvariables = globals()
            self.debugvariables.update(self.__dict__)
            self.debugvariables.update(locals())
        self.app.display("Enter A Command:")

    def setdebug(self, state):
        """Sets The Debugging State."""
        self.e.debug = True
        if self.debug:
            self.e.printdebug(": OFF")
        else:
            self.e.printdebug(": ON")
        self.debug = int(state)
        self.e.debug = self.debug

    def load(self):
        if self.debug:
            self.app.display("Warning: Debug mode active.")
            tempfile = openfile("PC.txt", "rb")
            base = readfile(tempfile)
            self.fromsheet(base)
            tempfile.close()
        else:
            try:
                tempfile = openfile("PC.txt", "rb")
                base = readfile(tempfile)
                self.fromsheet(base)
                tempfile.close()
            except IOError:
                self.app.display("Unable to find PC.txt for import.")
            except:
                popup("Error", "Error processing PC.txt for import.")
                self.app.display("Unable to load PC.txt for import.")
            else:
                self.app.display("Successfully imported PC.txt.")

    def fromsheet(self, base):
        lines = base.splitlines()
        for y in xrange(0, len(lines)):
            if lines[y].startswith("CHARACTER NAME"):
                self.e.variables["name"] = basicformat(lines[y-1].split()[0])
                for z in lines[y+1].split("	")[0].split(" "):
                    for i in reversed(xrange(0, len(z))):
                        if z[i] not in string.digits:
                            break
                    i += 1
                    self.e.variables[customformat(z[:i])] = customformat(z[i:])
                break
        for x in xrange(y, len(lines)):
            if lines[x].startswith("CLASS"):
                x += 1
                self.e.variables["level"] = float(lines[x].split("	")[0])
                break
        self.atts = {"Strength":"str_score", "Dexterity":"dex_score", "Constitution":"con_score", "Intelligence":"int_score", "Wisdom":"wis_score", "Charisma":"cha_score"} 
        while len(self.atts) > 0:
            x += 1
            test = lines[x].split("	")
            if test[0] in self.atts.keys():
                self.e.variables[self.atts[test[0]]+"_base"] =  customformat(test[1])
                self.e.variables[self.atts[test[0]]] =  customformat(test[3])
                del self.atts[test[0]]
        self.atts = {"Hit Points":"maxhp"}
        y = self.loop(x, lines)
        self.e.variables["hp"] = self.e.variables["maxhp"]
        for x in xrange(y, len(lines)):
            test = clean(lines[x].split("	"), ":")
            if test[0] == "Armour Class":
                self.e.variables["ac"] = float(test[1])
                self.e.variables["flatfooted"] = float(test[2])
                self.e.variables["touch"] = float(test[3])
                break
        self.atts = {"Modifier":"initiative", "Bonus":"bab"}
        y = self.loop(x, lines)
        self.skills = []
        for x in xrange(y, len(lines)):
            lines[x] = lines[x][1:]
            if lines[x].startswith("	  "):
                test = lines[x][3:].split("	")
                name = customformat(test[0].replace("(","[").replace(")","]").replace("/",""))
                self.e.variables[name] = float(test[2])
                self.skills.append(name)
            elif lines[x].startswith("  "):
                test = lines[x][2:].split("	")
                name = customformat(test[0].replace("(","[").replace(")","]").replace("/",""))
                self.e.variables[name] = float(test[2])
                self.skills.append(name)
            elif "Useable Untrained" in lines[x]:
                break
            elif lines[x].startswith(" "):
                test = lines[x][1:].split("	")
                name = customformat(test[0].replace("(","[").replace(")","]").replace("/",""))
                self.e.variables[name] = float(test[2])
                self.skills.append(name)
        self.atts = {"Constitution":"fortitude", "Dexterity":"reflex", "Wisdom":"will"}
        x = self.loop(x, lines)
        trash = 3
        while trash > 0:
            x += 1
            test = lines[x].split("	")
            if test[0] == "ATTACK BONUS":
                if trash == 3:
                    self.e.variables["melee"] = customformat(test[1].replace("/",","))
                elif trash == 2:
                    self.e.variables["ranged"] = customformat(test[1].replace("/",","))
                elif trash == 1:
                    self.e.variables["cmb"] = customformat(test[1].replace("/",","))
                trash -= 1
        addendum = ""
        for x in xrange(x, len(lines)):
            addendum += lines[x]+"\n"
        groups = addendum.split("\n\n")
        for x in xrange(0, len(groups)):
            groups[x] = groups[x].split("\n")
        self.e.variables["unarmed_attack"] = customformat(groups[1][1].replace("/",","))
        self.e.variables["unarmed_damage"] = customformat(groups[1][2])
        self.e.variables["unarmed_critrange"] = customformat(groups[1][3].split("/x")[0].split("-")[0])
        self.e.variables["unarmed_crittimes"] = customformat(groups[1][3].split("/x")[1])
        self.weps = []
        wep = 0
        for x in xrange(2, len(groups)):
            if len(groups[x])>=20 and groups[x][1].startswith("HAND"):
                wep += 1
                names = groups[x][0].split(" ")
                for y in names:
                    name = basicformat(y).replace("*","")
                    if not "(" in name and not ")" in name and not name.startswith("+") and not name.startswith("-"):
                        name = customformat(name)
                        break
                self.weps.append(name)
                self.e.variables[name+"_critrange"] = customformat(groups[x][5].split("/x")[0].split("-")[0])
                self.e.variables[name+"_crittimes"] = customformat(groups[x][5].split("/x")[1])
                i = 5
                while True:
                    i += 1
                    if groups[x][i].startswith(" Bonus	"):
                        break
                s = i
                while not groups[x][i].startswith(" Dam	"):
                    if groups[x][i].startswith(" Bonus	"):
                        test = groups[x][i][7:]
                    else:
                        test = groups[x][i]
                    self.e.variables[name+"_attack_"+str(i-s)] = customformat(test.replace("/",","))
                    i += 1
                if len(groups[x][i].split(" ")) > 1:
                    new = groups[x][i][5:].split("	")
                    for x in xrange(0, len(new)):
                        self.e.variables[name+"_damage_"+str(x+1)] = customformat(new[x])
                else:
                    self.e.variables[name+"_damage_1"] = customformat(groups[x][i][5:])
                    self.e.variables[name+"_damage_2"] = customformat(groups[x][i+1])
                    self.e.variables[name+"_damage_3"] = customformat(groups[x][i+2])
                    self.e.variables[name+"_damage_4"] = customformat(groups[x][i+3])
                    self.e.variables[name+"_damage_5"] = customformat(groups[x][i+4])
                    self.e.variables[name+"_damage_6"] = customformat(groups[x][i+5])
            elif groups[x][0] == "MONEY":
                break
        self.spellcaster = 0
        y = x
        for x in xrange(y, len(groups)):
            if "Spells" in groups[x][0] and groups[x][1].startswith("LEVEL"):
                for z in xrange(2, len(groups[x])):
                    if groups[x][z].startswith("PER DAY"):
                        spells = groups[x][z].split("	")[1:]
                        i = 0
                        for casts in spells:
                            casts = customformat(casts)
                            self.e.variables["level_"+str(i)+"_maxcasts"] = casts
                            self.e.variables["level_"+str(i)+"_casts"] = casts
                            i += 1
                        self.spellcaster = 1
                        break
                break

    def character(self):
        sheet = "Level: "+str(self.e.variables["level"])+" - HP: "+str(self.e.variables["hp"])+"/"+str(self.e.variables["maxhp"])
        sheet += "\nSTR: "+str(self.e.variables["str_score"])+" - DEX: "+str(self.e.variables["dex_score"])+" - CON: "+str(self.e.variables["con_score"])+" - INT: "+str(self.e.variables["int_score"])+" - WIS: "+str(self.e.variables["wis_score"])+" - CHA: "+str(self.e.variables["cha_score"])
        sheet += "\nAC: "+str(self.e.variables["ac"])+" - Flatfooted: "+str(self.e.variables["flatfooted"])+" - Touch: "+str(self.e.variables["touch"])
        sheet += "\nInitiative: "+str(self.e.variables["initiative"])+" - Saves: [Fortitude: "+str(self.e.variables["fortitude"])+" - Reflex: "+str(self.e.variables["reflex"])+" - Will: "+str(self.e.variables["will"])+"]"
        sheet += "\nAttack Bonuses: [Base: "+str(self.e.variables["bab"])+" - Melee: "+str(self.e.variables["melee"])+" - Ranged: "+str(self.e.variables["ranged"])+" - CMB: "+str(self.e.variables["cmb"])+"]"
        return sheet

    def weapons(self):
        weplist = "Weapons: unarmed"
        for x in self.weps:
            i = 1
            while haskey(self.e.variables, x+"_attack_"+str(i)):
                weplist += ", "+x+":"+str(i)
                i += 1
        return weplist

    def loop(self, x, lines):
        while len(self.atts) > 0:
            x += 1
            test = lines[x].split("	")
            if test[0] in self.atts.keys():
                self.e.variables[self.atts[test[0]]] =  customformat(test[1].replace("/",","))
                del self.atts[test[0]]
        return x

    def show(self, arg):
        if self.talk and isinstance(arg, strcalc):
            self.textmsg(": "+out)
        else:
            self.oldshow(arg)

    def populator(self):
        self.pre_cmds = [
            self.do_find,
            self.pre_help,
            self.pre_cmd
            ]
        self.cmds = [
            self.do_find,
            self.cmd_debug,
            self.cmd_errors,
            self.cmd_clear,
            self.cmd_clean,
            self.cmd_get,
            self.cmd_run,
            self.cmd_save,
            self.cmd_assert,

            self.cmd_skills,
            self.cmd_roll,
            self.cmd_character,
            self.cmd_weapons,
            self.cmd_create,
            self.cmd_equip,
            self.cmd_deal,
            self.cmd_cast,
            self.cmd_casts,
            self.cmd_rest,
            self.cmd_reload,
            self.cmd_join,
            self.cmd_host,
            self.cmd_encounter,
            self.cmd_disconnect,
            self.cmd_battle,
            self.cmd_open,
            self.cmd_hold,
            self.cmd_done,
            self.cmd_wipe,
            self.cmd_end,
            self.cmd_chat,
            self.cmd_scan,

            self.cmd_do,
            self.cmd_show,
            self.cmd_del,
            self.cmd_set,
            self.cmd_normal
            ]
        self.set_cmds = [
            self.set_import,
            self.set_def,
            self.set_normal
            ]
        self.e = evaluator(processor=self)
        self.e.makevars({
            "print":funcfloat(self.printcall, self.e, "print"),
            "ans":funcfloat(self.anscall, self.e, "ans"),
            "grab":funcfloat(self.grabcall, self.e, "grab"),
            "name":"Guest",
            "status":"deal 0"
            })

    def cmd_skills(self, original):
        if superformat(original) == "skills":
            self.app.display("Skills: "+strlist(self.skills, ", "))
            return True

    def cmd_roll(self, original):
        if superformat(original).startswith("roll "):
            original = self.e.find(original[5:])
            bonus = customformat(original)
            calcbonus = self.calc(bonus)
            if "matrix" in typestr(calcbonus):
                toroll = "base_roll,"*calcbonus.y
                roll = self.calc(toroll[:-1])
            else:
                roll = self.calc("base_roll")
            rollstr = self.e.prepare(roll, False, True)
            self.app.display("Roll: "+rollstr)
            totalstr = self.e.prepare(roll+calcbonus, False, True)
            self.saferun(self.app.display, "Total: "+totalstr)
            if self.sendroll:
                self.textmsg(" rolled "+rollstr+" + "+bonus+" = "+totalstr)
            return True

    def cmd_character(self, original):
        if superformat(original) == "character":
            popup("Info", self.character())
            return True

    def cmd_weapons(self, original):
        if superformat(original) == "weapons":
            self.app.display(self.weapons())
            return True

    def cmd_create(self, original):
        if superformat(original).startswith("create "):
            original = original[7:].split(" ")
            self.weps.append(original[0])
            self.e.variables[original[0]+"_attack"] = self.e.prepare(self.calc(original[1]), False, True)
            self.e.variables[original[0]+"_attack"] = self.e.prepare(self.calc(original[2]), False, True)
            return True

    def cmd_equip(self, original):
        if superformat(original).startswith("equip "):
            original = original[6:]
            original = original.split(":")
            name = original[0]
            self.e.variables["critrange"] = name+"_critrange"
            self.e.variables["crittimes"] = name+"_crittimes"
            if len(original) > 1:
                self.e.variables["attack"] = name+"_attack_"+original[1]
                self.e.variables["damage"] = name+"_damage_"+original[1]
            else:
                self.e.variables["attack"] = name+"_attack"
                self.e.variables["damage"] = name+"_damage"
            return True

    def cmd_deal(self, original):
        if superformat(original).startswith("deal "):
            original = original[5:]
            self.e.variables["hp"] = self.calc(self.e.prepare(self.e.variables["hp"], False, True)+"+-1*"+self.e.prepare(self.calc(customformat(original)), False, True))
            if float(self.calc(self.e.variables["hp"])) > float(self.calc(self.e.variables["maxhp"])):
                self.e.variables["hp"] = self.e.variables["maxhp"]
            self.app.display("HP: "+str(self.e.variables["hp"])+"/"+str(self.e.variables["maxhp"]))
            pop = False
            outstring = "Status: "
            hp = float(self.calc(self.e.variables["hp"]))
            if hp < -1.0*float(self.calc(self.e.variables["con_score"])):
                outstring += "Dead"
                pop = "You're Dead!"
            elif hp <= 0:
                outstring += "Unconscious"
            else:
                outstring += "Conscious"
            self.app.display(outstring)
            if pop:
                popup("Info", pop)
            return True

    def cmd_cast(self, original):
        if superformat(original).startswith("cast "):
            original = original[5:]
            if self.spellcaster == 0:
                self.app.display("You're not a spellcaster!")
            else:
                if float(self.calc(self.e.variables["level_"+original+"_casts"])) <= 0:
                    self.app.display("You're out of "+original+" level casts!")
                else:
                    self.e.variables["level_"+original+"_casts"] = self.e.prepare(self.calc("level_"+original+"_casts+-1"), False, True)
                    self.app.display("Level "+original+" Casts Used: "+str(self.e.variables["level_"+original+"_casts"])+"/"+str(self.e.variables["level_"+original+"_maxcasts"]))
            return True

    def cmd_casts(self, original):
        if superformat(original) == "casts":
            if self.spellcaster == 0:
                self.app.display("You're not a spellcaster!")
            else:
                error = 0
                level = 0
                while error == 0:
                    try:
                        self.app.display("Level "+str(level)+" Casts Used: "+str(self.e.variables["level_"+str(level)+"_casts"])+"/"+str(self.e.variables["level_"+str(level)+"_maxcasts"]))
                    except:
                        error = 1
                    level += 1
            return True

    def cmd_rest(self, original):
        if superformat(original) == "rest":
            if self.spellcaster == 1:
                error = 0
                level = 0
                while error == 0:
                    try:
                        self.e.variables["level_"+str(level)+"_casts"] = self.e.variables["level_"+str(level)+"_maxcasts"]
                    except:
                        error = 1
                    level += 1
            self.process("deal -1*rest_health")
            return True

    def cmd_reload(self, original):
        if superformat(original) == "reload":
            self.load()
            self.app.display("Enter A Command:")
            return True

    def cmd_join(self, original):
        if superformat(original).startswith("join "):
            original = original[5:]
            original = original.split(" ", 1)
            self.app.display("Connecting...")
            self.c = client(bool(self.debug))
            if len(original) > 1:
                self.c.connect(int(original[0]), original[1])
            else:
                self.c.connect(int(original[0]))
            self.app.display("Connected.")
            self.server = 0
            self.que = [self.e.variables["name"]]
            self.sent = None
            self.talk = 1
            self.register(self.refresh, self.speed)
            return True

    def cmd_host(self, original):
        if superformat(original).startswith("host "):
            original = original[5:]
            original = original.split(" ", 1)
            self.app.display("Waiting for connections...")
            self.c = multiserver(int(original[0]), debug=bool(self.debug))
            if len(original) < 2:
                self.number = 1
            else:
                self.number = int(original[1])
            self.c.start(self.number)
            self.app.display("Connected.")
            self.server = 1
            self.que = {}
            for a in self.c.c:
                self.que[a] = []
            self.sent = []
            self.talk = 1
            self.names = {None:self.e.variables["name"]}
            self.register(self.refresh, self.speed)
            self.register(self.namer, 600)
            return True

    def cmd_encounter(self, original):
        if superformat(original) == "encounter":
            if self.encounter != 0 or self.server < 0:
                self.app.display("You can't use that right now.")
            else:
                self.app.display("Waiting for other players...")
                self.sync()
                self.app.display("Launching game...")
                self.gui()
            return True

    def cmd_disconnect(self, original):
        if superformat(original) == "disconnect":
            if self.server <0:
                self.app.display("You can't use that right now.")
            else:
                self.disconnect()
            return True

    def cmd_battle(self, original):
        if superformat(original) == "battle":
            if self.server < 0 or self.x >= 0:
                self.app.display("You can't use that right now.")
            else:
                self.battle()
            return True

    def cmd_open(self, original):
        if superformat(original) == "open":
            if self.server == 1 and self.x < 0:
                self.number += 1
                self.app.display("Waiting for a connection...")
                self.c.add()
                self.app.display("Connection added.")
            else:
                self.app.display("You can't use that right now.")
            return True

    def cmd_hold(self, original):
        if superformat(original) == "hold":
            if self.server == 0 and self.turn == 1:
                self.que.append("0")
                self.turn = 0
            elif self.server == 1 and self.turn == 2:
                for x in xrange(0, len(self.order)-1):
                    if self.order[x] == None:
                        self.order[x] = self.order[x+1]
                        self.order[x+1] = None
                self.turn = 0
            else:
                self.app.display("You can't use that right now.")
            return True

    def cmd_done(self, original):
        if superformat(original) == "done":
            if self.server == 0 and self.turn == 1:
                self.que.append("1")
                self.turn = 0
            elif self.server == 1 and self.turn == 2:
                self.turn = 0
            else:
                self.app.display("You can't use that right now.")
            return True

    def cmd_wipe(self, original):
        if superformat(original) == "wipe":
            if self.server == 1 and self.turn == 2:
                self.structures = []
            else:
                self.app.display("You can't use that right now.")
            return True

    def cmd_end(self, original):
        if superformat(original) == "end":
            if self.server == 1 and self.turn == 2:
                self.turn = 0
                self.x = -2
            else:
                self.app.display("You can't use that right now.")
            return True

    def cmd_chat(self, original):
        if superformat(original) == "chat":
            if self.talk == 1:
                self.talk = 0
                self.app.display("Chat turned off.")
            elif self.talk == 0:
                if self.server < 0:
                    self.app.display("You can't use that right now.")
                else:
                    self.talk = 1
                    self.app.display("Chat turned on.")
            return True

    def cmd_scan(self, original):
        if superformat(original) == "scan":
            if self.debug:
                self.app.display("SCANNING MEMORY...")
                self.debugvariables.update(globals())
                self.debugvariables.update(self.__dict__)
                self.debugvariables.update(locals())
                scan(self.debugvariables)
                self.app.display("RESULTS PRINTED TO CONSOLE.")
            else:
                self.app.display("This command is only available in debug mode.")
            return True

    def convert(self, x, y):
        return self.width/2 + (x+1)*self.xsize, self.height/2 - (y-1)*self.ysize

    def inverse(self, x, y):
        return int((x - self.width/2)/self.xsize)-1, int((y - self.height/2)/self.ysize)*-1+1

    def sync(self):
        if self.server == 0:
            self.que.append("$")
            self.receive()
        else:
            self.receive()
            self.csend("$")

    def battle(self):
        self.x = 0
        self.turn = 0
        if self.server == 0:
            roll = self.calc("base_roll")
            self.app.display("Initiative Roll: "+self.e.prepare(roll, False, False))
            total = str(float(roll+self.calc("initiative")))
            self.app.display("Initiative Total: "+total)
            self.que.append(total)
            self.register(self.idle, 600)
        elif self.server == 1:
            roll = self.calc("base_roll")
            self.app.display("Initiative Roll: "+self.e.prepare(roll, False, False))
            total = float(roll+self.calc("initiative"))
            self.app.display("Initiative Total: "+str(total))
            self.app.display("Getting Initiatives...")
            inits = self.receive()
            inits.append((total, None))
            inits.sort()
            initdisplay = " Initiatives: "
            self.order = []
            for i,a in inits:
                self.order.append(a)
                initdisplay += self.names[a]+" ("+str(i)+"), "
            self.textmsg(initdisplay[:-2])
            self.app.display("Beginning Battle...")
            self.register(self.rounds, 600)

    def idle(self):
        if self.sent == "0":
            self.sent = None
            self.turn = 1
            popup("Info", "It's your turn!")
            self.app.display("It's your turn!")
            while self.turn > 0:
                self.root.update()
            self.register(self.idle, 600)
        elif self.sent == "-":
            self.sent = None
            self.x = -1
            self.app.display("Battle Ended.")
            self.turn = 1
        else:
            self.register(self.idle, 600)

    def rounds(self):
        if self.x >= 0:
            if self.x >= len(self.order):
                self.x = 0
            if self.order[self.x] == None:
                self.turn = 2
                popup("Info", "It's your turn!")
                self.app.display("It's your turn!")
                while self.turn > 0:
                    self.root.update()
            else:
                self.que[self.order[self.x]].append("0")
                waited = self.wait()
                while waited == None:
                    self.root.update()
                    waited = self.wait()
                cmd = int(getnum(waited))
                if not cmd and self.x < len(self.order):
                    self.order[self.x], self.order[self.x+1] = self.order[self.x+1], self.order[self.x]
            self.x += 1
            self.register(self.rounds, 600)
        else:
            self.csend("-")
            self.x = -1
            self.app.display("Battle Ended.")
            self.turn = 2

    def wait(self):
        for i,a in self.sent:
            if a == self.order[self.x]:
                self.sent = []
                return i
        return None

    def receive(self):
        if self.server == 0:
            while self.sent == None:
                self.root.update()
            temp = self.sent
            self.sent = None
            return temp
        else:
            while len(self.sent) < self.number:
                self.root.update()
            temp = self.sent
            self.sent = []
            return temp

    def chat(self, msg):
        if self.talk == 1:
            self.app.display("> "+msg)

    def textmsg(self, item):
        if self.server == 0:
            self.que.append("+:"+item)
        elif self.server == 1:
            output = self.e.variables["name"]+item
            self.chat(output)
            self.csend("+:"+output)

    def csend(self, item):
        for a in self.c.c:
            self.que[a].append(item)

    def addsent(self, item):
        if self.server == 0:
            if item.startswith("+:"):
                self.chat(item[2:])
            else:
                self.sent = item
        elif self.server == 1:
            i,a = item
            if i.startswith("+:"):
                i = i[2:]
                output = self.names[a]+i
                self.csend("+:"+output)
                self.chat(output)
            else:
                self.sent.append((i,a))

    def retreive(self, a=None):
        try:
            if a == None:
                out = self.c.retreive(self.root.update)
            else:
                out = self.c.retreive(a, self.root.update)
        except IOError:
            self.disconnect()
            raise RuntimeError
        else:
            return out

    def refresh(self):
        if self.debug:
            print(str(self.debug)+" ("+str(self.encounter)+"):", self.que)
            self.debug += 1
        if self.server == 0:
            test = self.retreive().strip("#")
            if test != "":
                self.addsent(test)
            if len(self.que) > 0:
                self.que.reverse()
                self.c.fsend(self.que.pop())
                self.que.reverse()
            else:
                self.c.fsend("#")
            self.c.fsend(self.encounter)
            self.root.update()
            if self.retreive().strip("#") == "1":
                self.c.fsend(str(self.locx)+","+str(self.locy))
                self.players = []
                players = clean(self.retreive()[1:-1].split("), "))
                for x in players:
                    x = remparens(x[1:]).split(", ")
                    self.players.append((int(x[0]), int(x[1])))
                self.enemies = []
                enemies = clean(self.retreive()[1:-1].split("), "))
                for x in enemies:
                    x = remparens(x[1:]).split(", ")
                    self.enemies.append((int(x[0]), int(x[1])))
                self.structures = []
                structures = clean(self.retreive()[1:-1].split("), "))
                for x in structures:
                        x = remparens(x[1:]).split(", ")
                        self.structures.append((float(x[0]), float(x[1]), float(x[2]), float(x[3])))
            self.register(self.refresh, self.speed)
        elif self.server == 1:
            for a in self.c.c:
                if len(self.que[a]) > 0:
                    self.que[a].reverse()
                    self.c.fsend(a, self.que[a].pop())
                    self.que[a].reverse()
                else:
                    self.c.fsend(a, "#")
            temp = {}
            encounter = self.encounter
            self.root.update()
            for a in self.c.c:
                temp[a] = None
                test = self.retreive(a)
                if test != "#":
                    if test.startswith("#"):
                        temp[a] = test.strip("#")
                    else:
                        self.addsent((test,a))
                encounter += int(getnum(self.retreive(a).strip("#")))
            if encounter < self.number+1:
                for a in self.c.c:
                    self.c.fsend(a, "0")
            else:
                for a in self.c.c:
                    self.c.fsend(a, "1")
                self.players = []
                data = {}
                for a in self.c.c:
                    if temp[a] == None:
                        trash = self.retreive(a).split(",")
                    else:
                        trash = temp[a].split(",")
                    data[a] = (int(trash[0]), int(trash[1]))
                for a in self.c.c:
                    temp = []
                    for ta in data:
                        if ta != a:
                            temp.append(data[ta])
                    self.c.fsend(a, temp)
                    self.c.fsend(a, self.enemies)
                    self.c.fsend(a, self.structures)
                for k in data.values():
                    self.players.append(k)
            self.register(self.refresh, self.speed)
        if self.encounter == 1:
            self.render()
        elif self.encounter == -1:
            self.top.destroy()

    def render(self):
        for x in self.identifiers:
            self.grid.clear(x)
        self.identifiers = []
        if self.server == 0:
            x, y = self.convert(self.locx, self.locy)
            self.identifiers.append(self.grid.new(self.player, x, y))
        for locx,locy in self.players:
            x, y = self.convert(locx, locy)
            self.identifiers.append(self.grid.new(self.player, x, y))
        for locx,locy in self.enemies:
            x, y = self.convert(locx, locy)
            self.identifiers.append(self.grid.new(self.enemy, x, y))
        for ax,ay, bx,by in self.structures:
            self.make(ax,ay, bx,by)

    def up(self):
        if self.server == 0 and (self.override or self.turn == 1):
            self.locy += 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0], self.enemies[self.selected][1]+1
            self.render()

    def down(self):
        if self.server == 0 and (self.override or self.turn == 1):
            self.locy -= 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0], self.enemies[self.selected][1]-1
            self.render()

    def right(self):
        if self.server == 0 and (self.override or self.turn == 1):
            self.locx += 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0]+1, self.enemies[self.selected][1]
            self.render()

    def left(self):
        if self.server == 0 and (self.override or self.turn == 1):
            self.locx -= 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0]-1, self.enemies[self.selected][1]
            self.render()

    def draw(self, event):
        if self.server == 1 and (self.override or self.turn == 2):
            if self.drawing == None:
                self.drawing = self.grid.convert(event)
            else:
                ax, ay = self.drawing
                self.drawing = None
                bx, by = self.grid.convert(event)
                self.make(ax,ay, bx,by)
                self.structures.append((ax,ay, bx,by))

    def make(self, ax,ay, bx,by):
        if ax == bx:
            ax = int(ax)
            ay = int(ay)
            by = int(by)
            if ay > by:
                ay, by = by, ay
            for y in xrange(ay, by):
                self.identifiers.append(self.grid.new(self.structure, ax, y))
        elif ay == by:
            ay = int(ay)
            ax = int(ax)
            bx = int(bx)
            if ax > bx:
                ax, bx = bx, ax
            for x in xrange(ax, bx):
                self.identifiers.append(self.grid.new(self.structure, x, ay))
        else:
            rise = float(by-ay)
            run = float(bx-ax)
            absrise = abs(rise)
            absrun = abs(run)
            if absrise > absrun:
                rise = rise/absrise
                run = run/absrise
            else:
                run = run/absrun
                rise = rise/absrun
            while abs(ax-bx) > 0.1 and abs(ay-by) > 0.1:
                self.identifiers.append(self.grid.new(self.structure, ax, ay))
                ay += rise
                ax += run

    def select(self, event):
        if self.server == 1 and (self.override or self.turn == 2):
            tx, ty = self.grid.convert(event)
            x, y = self.inverse(tx, ty)
            if (x,y) in self.enemies:
                self.selected = self.enemies.index((x,y))

    def create(self, event):
        if self.server == 1 and (self.override or self.turn == 2):
            tx, ty = self.grid.convert(event)
            x, y = self.inverse(tx, ty)
            self.enemies.append((x,y))
            self.selected = len(self.enemies)-1
            self.render()

    def remove(self):
        if self.selected != None and (self.override or self.turn == 2):
            self.enemies.remove(self.enemies[self.selected])
            self.selected = None
            self.render()

    def gui(self, width=800, height=600):
        self.turn = 0
        self.top = self.window()
        rootbind(self.top, self.xgui)
        self.top.bind("<Up>", lambda event: self.up())
        self.top.bind("<Down>", lambda event: self.down())
        self.top.bind("<Right>", lambda event: self.right())
        self.top.bind("<Left>", lambda event: self.left())
        self.drawing = None
        self.top.bind("<Shift-Button-1>", self.draw)
        self.top.bind("<Button-2>", self.select)
        self.top.bind("<Shift-Button-2>", self.create)
        self.top.bind("<Shift-BackSpace>", lambda event: self.remove)
        self.width = width
        self.height = height
        self.grid = displayer(self.top, self.width, self.height)
        self.player = openphoto("Player.gif")
        self.enemy = openphoto("Enemy.gif")
        self.ysize = self.player.height()
        self.xsize = self.player.width()
        self.structure = openphoto("Pixel.gif")
        try:
            self.graph = openphoto("Graph.gif")
        except:
            pass
        else:
            self.grid.new(self.graph)
        self.identifiers = []
        self.structures = []
        self.players = []
        self.enemies = []
        self.selected = None
        if self.server == 0:
            self.locx, self.locy = 0, 0
            self.turn = 1
        else:
            self.turn = 2
        self.render()
        self.encounter = 1
        self.app.display("Game ready.")
        self.top.mainloop()
        self.xgui()

    def xgui(self):
        self.encounter = -1
        self.identifiers = []
        self.turn = -1

    def disconnect(self):
        self.talk = 0
        if self.server == 0:
            self.c.close()
        else:
            for a in dict(self.c.c):
                self.c.close(a)
        self.server = -1
        self.app.display("Disconnected.")

    def namer(self):
        for n,a in self.sent:
            self.names[a] = n
        self.sent = []

if __name__ == "__main__":
    main(override, sendroll, debug, speed).start()
