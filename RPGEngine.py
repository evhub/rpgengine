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

# WARNING: DO NOT MODIFY THIS LINE!
from __future__ import with_statement, absolute_import, print_function, unicode_literals

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

engnum_maps = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty"
    }
def engnum(inputnum):
    """Gets The English For A Number."""
    return engnum_maps[getint(inputnum)]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class main(mathbase, serverbase):

    def __init__(self, override=False, sendroll=False, debug=False, speed=400, height=10):
        self.startup(debug)
        self.speed = speed
        self.override = override
        self.sendroll = sendroll
        self.root, self.app, self.box = startconsole(self.handler, "Loading RPGEngine...", "RPGEngine", height)
        self.populator()
        self.load()
        self.server = None
        self.turn = -1
        self.x = -1
        self.talk = 0
        self.encounter = 0
        if not self.saferun(self.evalfile, "Rules.rab"):
            popup("Error", "Error finding Rules.rab for import.")
            self.app.display("Unable to find Rules.rab for import.")
        self.app.display("Enter A Command:")

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

    def remparens(self, inputstring):
        return delspace(inputstring, strlist(self.e.groupers.keys()+self.e.groupers.values(), ""))

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
                            istr = engnum(i)
                            casts = customformat(casts)
                            self.e.variables["level_"+istr+"_maxcasts"] = casts
                            self.e.variables["level_"+istr+"_casts"] = casts
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

    def show(self, arg, top=False):
        if self.talk and not top and isinstance(arg, strcalc):
            self.textmsg(": "+out)
        else:
            self.appshow(arg, top)

    def fresh(self, top=True):
        """Refreshes The Environment."""
        if not top:
            self.e.fresh()
        self.e.makevars({
            "debug":funcfloat(self.debugcall, self.e, "debug"),
            "make":funcfloat(self.makecall, self.e, "make", reqargs=1),
            "save":funcfloat(self.savecall, self.e, "save", reqargs=1),
            "install":funcfloat(self.installcall, self.e, "install", reqargs=1),
            "print":funcfloat(self.printcall, self.e, "print"),
            "show":funcfloat(self.showcall, self.e, "show"),
            "ans":funcfloat(self.anscall, self.e, "ans"),
            "grab":funcfloat(self.grabcall, self.e, "grab"),
            "clear":usefunc(self.clear, self.e, "clear"),
            "name":"Guest",
            "skills":usefunc(self.skills, self.e, "skills"),
            "roll":funcfloat(self.rollcall, self.e, "roll"),
            "character":usefunc(self.show_character, self.e, "character"),
            "weapons":usefunc(self.show_weapons, self.e, "weapons"),
            "create":funcfloat(self.createcall, self.e, "create"),
            "equip":funcfloat(self.equipcall, self.e, "equip"),
            "status":usefunc(self.status, self.e, "status"),
            "deal":funcfloat(self.dealcall, self.e, "deal"),
            "cast":funcfloat(self.castcall, self.e, "cast"),
            "casts":usefunc(self.show_casts, self.e, "casts"),
            "rest":usefunc(self.do_rest, self.e, "rest"),
            "reload":usefunc(self.do_reload, self.e, "reload"),
            "client":funcfloat(self.clientcall, self.e, "client"),
            "host":funcfloat(self.hostcall, self.e, "host"),
            "encounter":usefunc(self.do_encounter, self.e, "encounter"),
            "disconnect":usefunc(self.do_disconnect, self.e, "disconnect"),
            "battle":usefunc(self.do_battle, self.e, "battle"),
            "addclient":usefunc(self.do_addclient, self.e, "addclient"),
            "hold":usefunc(self.do_hold, self.e, "hold"),
            "done":usefunc(self.do_done, self.e, "done"),
            "wipe":usefunc(self.do_wipe, self.e, "wipe"),
            "end":usefunc(self.do_end, self.e, "end"),
            "chat":usefunc(self.do_chat, self.e, "chat")
            })

    def skills(self):
        self.app.display("Skills: "+strlist(self.skills, ", "))
        self.setreturned()

    def rollcall(self, variables):
        if not variables:
            calcbonus = 0.0
        elif len(variables) == 1:
            calcbonus = variables[0]
        else:
            calcbonus = diagmatrixlist(variables)
        if isinstance(calcbonus, matrix):
            toroll = "base_roll(),"*calcbonus.y
            roll = self.e.calc(toroll[:-1])
        else:
            roll = self.e.calc("base_roll()")
        rollstr = self.e.prepare(roll, False, True)
        total = roll+calcbonus
        totalstr = self.e.prepare(total, False, True)
        self.app.display("Roll: "+rollstr)
        self.app.display("Total: "+totalstr)
        if self.sendroll:
            self.textmsg(" rolled "+rollstr+" + "+bonus+" = "+totalstr)
        self.setreturned()
        return total

    def show_character(self):
        popup("Info", self.character())
        self.setreturned()

    def show_weapons(self, original):
        self.app.display(self.weapons())
        self.setreturned()

    def createcall(self, variables):
        if len(variables) < 3:
            raise ExecutionError("ArgumentError", "Not enough arguments to create")
        elif len(variables) == 3:
            name = self.e.prepare(variables[0], False, False)
            self.weps.append(name)
            self.e.variables[name+"_attack"] = variables[1]
            self.e.variables[name+"_attack"] = variables[2]
            self.setreturned()
        else:
            raise ExecutionError("ArgumentError", "Too many arguments to create")

    def equipcall(self, variables):
        if not variables:
            raise ExecutionError("ArgumentError", "Not enough arguments to equip")
        elif len(variables) < 3:
            name = self.e.prepare(variables[0], False, False)
            self.e.variables["critrange"] = name+"_critrange"
            self.e.variables["crittimes"] = name+"_crittimes"
            if len(original) > 1:
                variant = self.e.prepare(variables[1], False, False)
                self.e.variables["attack"] = name+"_attack_"+variant
                self.e.variables["damage"] = name+"_damage_"+variant
            else:
                self.e.variables["attack"] = name+"_attack"
                self.e.variables["damage"] = name+"_damage"
            self.setreturned()
        else:
            raise ExecutionError("ArgumentError", "Too many arguments to equip")

    def status(self):
        self.dealcall([0.0])

    def dealcall(self, variables):
        if istext(self.e.variables["hp"]):
            self.e.variables["hp"] = self.e.calc(self.e.variables["hp"])
        self.e.variables["hp"] -= self.e.funcs.sumcall(variables)
        if istext(self.e.variables["maxhp"]):
            self.e.variables["maxhp"] = self.e.calc(self.e.variables["maxhp"])
        if self.e.variables["hp"] > self.e.variables["maxhp"]:
            self.e.variables["hp"] = self.e.variables["maxhp"]
        self.app.display("HP: "+self.e.prepare(self.e.variables["hp"], False, True)+"/"+self.e.prepare(self.e.variables["maxhp"], False, True))
        pop = False
        outstring = "Status: "
        if istext(self.e.variables["con_score"]):
            self.e.variables["con_score"] = self.e.calc(self.e.variables["con_score"])
        if self.e.variables["hp"] < -1.0*self.e.variables["con_score"]:
            outstring += "Dead"
            pop = "You're Dead!"
        elif self.e.variables["hp"] <= 0:
            outstring += "Unconscious"
        else:
            outstring += "Conscious"
        self.app.display(outstring)
        if pop:
            popup("Info", pop)
        self.setreturned()

    def castcall(self, variables):
        if not variables:
            raise ExecutionError("ArgumentError", "Not enough arguments to cast")
        elif len(variables) == 1:
            if self.spellcaster == 0:
                self.app.display("You're not a spellcaster!")
            else:
                if isnum(variables[0]):
                    original = engnum(variables[0])
                else:
                    original = self.e.prepare(variables[0], False, False)
                if self.e.isreserved(original):
                    raise ValueError("Invalid part of a variable name "+original)
                elif getnum(self.e.calc(self.e.variables["level_"+original+"_casts"])) <= 0:
                    self.app.display("You're out of level "+original+" casts!")
                else:
                    self.e.variables["level_"+original+"_casts"] = self.e.calc("level_"+original+"_casts-1")
                    self.app.display("Level "+original+" Casts Used: "+self.e.prepare(self.e.variables["level_"+original+"_casts"], False, True)+"/"+self.e.prepare(self.e.variables["level_"+original+"_maxcasts"], False, True))
            self.setreturned()
        else:
            for arg in variables:
                self.castcall([arg])

    def show_casts(self):
        if self.spellcaster == 0:
            self.app.display("You're not a spellcaster!")
        else:
            error = 0
            level = 0
            while error == 0:
                name = engnum(level)
                try:
                    self.app.display("Level "+name+" Casts Used: "+self.e.prepare(self.e.variables["level_"+name+"_casts"], False, True)+"/"+self.e.prepare(self.e.variables["level_"+name+"_maxcasts"], False, True))
                except:
                    error = 1
                level += 1
        self.setreturned()

    def do_rest(self):
        if self.spellcaster == 1:
            error = 0
            level = 0
            while error == 0:
                name = engnum(level)
                try:
                    self.e.variables["level_"+name+"_casts"] = self.e.variables["level_"+name+"_maxcasts"]
                except:
                    error = 1
                level += 1
        self.setreturned()
        self.dealcall([self.e.calc("-1*rest_health")])

    def do_reload(self):
        self.load()
        self.setreturned()
        self.app.display("Enter A Command:")

    def clientcall(self, variables):
        if not variables:
            raise ExecutionError("ArgumentError", "Not enough arguments to client")
        elif len(variables) < 3:
            self.setreturned()
            self.app.display("Connecting...")
            self.port = getint(variables[0])
            if len(variables) > 1:
                self.host = self.e.prepare(variables[1], False, False)
            else:
                self.host = None
            self.server = False
            self.talk = 1
            self.name = self.e.find("name", False, True)
            self.register(self.connect, 200)
        else:
            raise ExecutionError("ArgumentError", "Too many arguments to client")

    def hostcall(self, variables):
        if not variables:
            raise ExecutionError("ArgumentError", "Not enough arguments to host")
        elif len(variables) < 3:
            self.setreturned()
            self.app.display("Waiting for connections...")
            self.port = getint(variables[0])
            if len(original) > 1:
                self.number = getint(variables[1])
            else:
                self.number = 1
            self.server = True
            self.talk = 1
            self.names = {None: self.e.find("name", False, True)}
            self.register(self.connect, 200)
        else:
            raise ExecutionError("ArgumentError", "Too many arguments to host")

    def do_encounter(self):
        if self.encounter != 0 or self.server == None:
            self.app.display("You can't use that right now.")
        else:
            self.app.display("Waiting for other players...")
            self.sync()
            self.app.display("Launching game...")
            self.gui()
        self.setreturned()

    def do_disconnect(self):
        self.setreturned()
        if self.server == None:
            self.app.display("You can't use that right now.")
        else:
            self.disconnect()

    def do_battle(self):
        if self.server == None or self.x >= 0:
            self.app.display("You can't use that right now.")
        else:
            self.battle()
        self.setreturned()

    def do_addclient(self):
        self.setreturned()
        if self.server and self.x < 0:
            self.number += 1
            self.app.display("Waiting for a connection...")
            self.c.add()
            self.app.display("Connection added.")
        else:
            self.app.display("You can't use that right now.")

    def do_hold(self):
        self.setreturned()
        if self.server == False and self.turn == 1:
            self.queue.append("0")
            self.turn = 0
        elif self.server and self.turn == 2:
            for x in xrange(0, len(self.order)-1):
                if self.order[x] == None:
                    self.order[x] = self.order[x+1]
                    self.order[x+1] = None
            self.turn = 0
        else:
            self.app.display("You can't use that right now.")

    def do_done(self):
        self.setreturned()
        if self.server == False and self.turn == 1:
            self.queue.append("1")
            self.turn = 0
        elif self.server and self.turn == 2:
            self.turn = 0
        else:
            self.app.display("You can't use that right now.")

    def do_wipe(self):
        if self.server and self.turn == 2:
            self.structures = []
        else:
            self.app.display("You can't use that right now.")
        self.setreturned()

    def do_end(self):
        if self.server and self.turn == 2:
            self.turn = 0
            self.x = -2
        else:
            self.app.display("You can't use that right now.")
        self.setreturned()

    def do_chat(self):
        if self.talk == 1:
            self.talk = 0
            self.app.display("Chat turned off.")
        elif self.talk == 0:
            if self.server == None:
                self.app.display("You can't use that right now.")
            else:
                self.talk = 1
                self.app.display("Chat turned on.")
        self.setreturned()

    def convert(self, x, y):
        return self.width/2 + (x+1)*self.xsize, self.height/2 - (y-1)*self.ysize

    def inverse(self, x, y):
        return int((x - self.width/2)/self.xsize)-1, int((y - self.height/2)/self.ysize)*-1+1

    def battle(self):
        self.x = 0
        self.turn = 0
        roll = self.e.calc("base_roll:")
        if self.server:
            self.app.display("Initiative Roll: "+self.e.prepare(roll, False, False))
            total = float(roll+self.e.calc("initiative"))
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
        elif self.server != None:
            self.app.display("Initiative Roll: "+self.e.prepare(roll, False, False))
            total = str(float(roll+self.e.calc("initiative")))
            self.app.display("Initiative Total: "+total)
            self.queue.append(total)
            self.register(self.idle, 600)

    def idle(self):
        item = self.getsent()
        if item == "0":
            self.turn = 1
            popup("Info", "It's your turn!")
            self.app.display("It's your turn!")
            while self.turn > 0:
                self.update()
            self.register(self.idle, 600)
        elif item == "-":
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
                    self.update()
            else:
                self.queue[self.order[self.x]].append("0")
                waited = self.wait()
                while waited == None:
                    self.update()
                    waited = self.wait()
                cmd = int(getnum(waited))
                if not cmd and self.x < len(self.order):
                    self.order[self.x], self.order[self.x+1] = self.order[self.x+1], self.order[self.x]
            self.x += 1
            self.register(self.rounds, 600)
        else:
            self.send("-")
            self.x = -1
            self.app.display("Battle Ended.")
            self.turn = 2

    def wait(self):
        for i,a in self.getsent():
            if a == self.order[self.x]:
                return i
        return None

    def chat(self, msg):
        if self.talk == 1:
            self.app.display("> "+str(msg))

    def begin(self):
        self.app.display("Loaded.")

    def refresh(self, empty="#"):
        self.printdebug("{\n"+str(self.debug)+" ("+str(self.encounter)+"):", self.queue)
        if self.debug:
            self.debug += 1
        empty = str(empty)
        if self.server:
            for a in self.c.c:
                if len(self.queue[a]) > 0:
                    self.c.fsend(a, self.queue[a].pop(0))
                else:
                    self.c.fsend(a, empty)
            temp = {}
            encounter = self.encounter
            self.root.update()
            for a in self.c.c:
                temp[a] = None
                test = self.retrieve(a)
                if test != empty:
                    if test.startswith(empty):
                        temp[a] = test.strip(empty)
                    else:
                        self.addsent((test,a))
                encounter += int(getnum(self.retrieve(a).strip(empty)))
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
                        trash = self.retrieve(a).split(",")
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
        elif self.server != None:
            test = self.retrieve().strip(empty)
            if test:
                self.addsent(test)
            if len(self.queue) > 0:
                self.c.fsend(self.queue.pop(0))
            else:
                self.c.fsend(empty)
            self.c.fsend(self.encounter)
            self.root.update()
            if self.retrieve().strip(empty) == "1":
                self.c.fsend(str(self.locx)+","+str(self.locy))
                self.players = []
                players = clean(self.retrieve()[1:-1].split("), "))
                for x in players:
                    x = self.remparens(x[1:]).split(", ")
                    self.players.append((int(x[0]), int(x[1])))
                self.enemies = []
                enemies = clean(self.retrieve()[1:-1].split("), "))
                for x in enemies:
                    x = self.remparens(x[1:]).split(", ")
                    self.enemies.append((int(x[0]), int(x[1])))
                self.structures = []
                structures = clean(self.retrieve()[1:-1].split("), "))
                for x in structures:
                        x = self.remparens(x[1:]).split(", ")
                        self.structures.append((float(x[0]), float(x[1]), float(x[2]), float(x[3])))
        if self.server != None:
            self.printdebug(":: "+str(len(self.agenda)))
            todo = self.agenda
            self.agenda = []
            for wait, func in todo:
                wait -= 1
                if wait <= 0:
                    self.register(func, 200)
                else:
                    self.agenda.append((wait, func))
            self.register(self.refresh, self.speed)
        if self.encounter == 1:
            self.render()
        elif self.encounter == -1:
            self.top.destroy()
        self.printdebug("}")

    def render(self):
        for x in self.identifiers:
            self.grid.clear(x)
        self.identifiers = []
        if self.server == False:
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
        if self.server == False and (self.override or self.turn == 1):
            self.locy += 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0], self.enemies[self.selected][1]+1
            self.render()

    def down(self):
        if self.server == False and (self.override or self.turn == 1):
            self.locy -= 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0], self.enemies[self.selected][1]-1
            self.render()

    def right(self):
        if self.server == False and (self.override or self.turn == 1):
            self.locx += 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0]+1, self.enemies[self.selected][1]
            self.render()

    def left(self):
        if self.server == False and (self.override or self.turn == 1):
            self.locx -= 1
            self.render()
        elif self.selected != None and (self.override or self.turn == 2):
            self.enemies[self.selected] = self.enemies[self.selected][0]-1, self.enemies[self.selected][1]
            self.render()

    def draw(self, event):
        if self.server and (self.override or self.turn == 2):
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
        if self.server and (self.override or self.turn == 2):
            tx, ty = self.grid.convert(event)
            x, y = self.inverse(tx, ty)
            if (x,y) in self.enemies:
                self.selected = self.enemies.index((x,y))

    def create(self, event):
        if self.server and (self.override or self.turn == 2):
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
        if self.server == False:
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

if __name__ == "__main__":
    main(override, sendroll, debug, speed).start()
