RPGEngine
=========

Uses Rabbit to power a program that will assist in Dungeons and Dragons, Pathfinder, etc. roleplaying calculations.

INSTALLATION:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### WINDOWS:
1. Unzip RPGEngine.zip to the location you would like to run it from.
2. Insure that all the contents of RPGEngine.zip are in the same place. That includes the 'dist' and 'build' folders and 'RPGEngine.bat'.
3. Run 'RPGEngine.bat' every time you would like to use the program.

### OTHER:
1. Unzip MacRPGEngine.zip to the location you would like to run it from
2. Insure that all the contents of MacRPGEngine.zip are in the same place. That includes 'RPGEngine.py', 'PythonPlus.pyc', 'Rules.txt', 'Player.gif', 'Enemy.gif', and 'Pixel.gif'.
3. Run 'RPGEngine.py' as an executable every time you would like to use the program
4. If you are still unable to launch the file, download Python 2.7 (http://www.python.org/download/)
5. Then, run RPGEngine.py using the Python Launcher

BASIC TUTORIAL:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

While RPGEngine can seem intimidating at first, it's really quite simple and very powerful. Read everything in this section closely to become a master.

When you boot up RPGEngine the first window you will see is the 'console.' The console is where commands are entered and text is displayed. To see a list of console commands type 'help' in the console.

### THE CONSOLE:
The console is very powerful. It can do dynamic mathematical calculations, make rolls, keep track of variables, and much more. Here are some common examples of things you can do with the console:
```
a = b*2		# The console can be used to set or change variables. A command of this form will set the variable 'a' to the value 'b' times two.
a+1			# This command will print the value of 'a' plus one to the console. This form of command can be used to implement a variety of mathematical operations.
2d6:+1		# The console is fully able to implement basic dice shorthand, but either a colon or open and close parentheses must be used. This command will evaluate to the result of the 2d6 plus one.
roll a		# This command will make a roll (default d20) and add the value of 'a' to it. Both the base roll and the total will be shown.
```

### IMPORTING A PC:
To fully utilize RPGEngine it is highly recommended that you import a character from PCGen. Here is how you do that:
1. Create your character in PCGen
2. Go to 'file' then 'export' and choose the second one from the bottom (my_outputsheets/my_fantasy/mtmlxml/csheet_my_fantasy_output_sheet.htm) and without changing any of the other settings select 'Export'
3. Save the file and then open it so you can select the text in it without the encoding (any web browser should work)
4. Copy ALL the text from the file into a file PC.txt
5. Place PC.txt in the same directory as RPGEngine (On Windows that means in your 'dist' folder)

### USING YOUR PC:
Importing a PC will load a suite of variables into your console that correspond to your character's attributes. Here are some examples:
```
initiative	# Lots of basic statistics are loaded.
bab			# While your bab is loaded as a variable, your weapon attack bonuses are loaded separately.
cmb			# Your basic defensive and offensive stats are loaded.
str			# Basic attributes are always loaded.
will		# Your different saves are loaded.
ac			# All your different Armor Classes are loaded
stealth		# All your usable skills are loaded.
```

Once you have imported a PC a whole new suite of commands are available to you. Here is a list of some of them and how to use them:
```
deal a		# This will cause your character to take 'a' damage. RPGEngine will keep track of your health.
				# NOTE: Type 'status' to display your health without using this command.
cast 2		# This will use up one of your level '2' spell slots.
				# NOTE: Type 'casts' for a list of all your casts.
rest		# This will restore your spell slots and a portion of your health (default is your level).
character	# This will display a basic summary of your character
				# NOTE: Type 'skills' to display your skills.
```

### EQUIPPING WEAPONS:
Upon loading in your PC you will notice that the variables 'attack' and 'damage' are left undefined. That is because the program doesn't know what weapon you would like to use. Here are the commands you would use to tell it:
```
weapons					# This will list off the different weapons available to you.
							# NOTE: This list will include the different ways that you could hold your weapon or the different ranges you could use it at as separate weapons. Each of these will be labeled as 'weapon_#' with each number corresponding to a different way of holding or a different range.
equip unarmed			# This will equip the weapon 'unarmed'. Doing this will set the values of 'attack' and 'damage' to those of the weapon you have chosen.
create weapon 1 1d2+1	# This will create a weapon called 'weapon' that has a '1' attack and a '1d2+1' damage.
```

### CONNECTING TO OTHERS:
One of RPGEngine's main features is the ability to connect to others. Once a connection is creaed a whole suite of new features become available. Creating a connection is quite simple and only requires a couple of commands:
```
join 25566 8.24.563.274	# This command is used to connect to a game that is being created by the host. The first variable is the port, the second is the IP address.
host 25566 4			# This command is used to host a game. The first variable is the port, the second variable is the number of players. The game will not start until that number of players have joined.
							# NOTE: It is recommended that the host explicitly forward the port he/she would like to use for hosting. Not doing so may cause other players to be unable to connect.
disconnect				# This command will disconnect you from whomever you are currently connected to.
```

### CHATTING:
RPGEngine comes with built-in chat functionality while connected to others. Here is a list of commands to use that functionality:
```
chat					# This command turns chat on or off for you. Use this command to prevent yourself from receiving chat messages.
"my cmb is "+cmb		# Putting something in quotation marks will send a chat message. Variables can be added to messages just like they were numbers and their values will be added to the string.
```

### PLAYING ENCOUNTERS:
RPGEngine also supports a dynamic game system. This comes in the form of a large grid that you can move your character around if you are a player or draw in places and enemies if you are the host. Using this system is somewhat complicated at first. We'll start with the basics:
```
encounter	# This command will initiate an encounter. All connected players must enter the encounter to start.
```

Once you are part of a game you will see a window fairly empty except for the players at the center. Now you need to be able to do things in your world. Here are the keyboard combinations for the things you can do:
```
Up/Down/Left/Right		# These keys are used to either move your player if you are a player or move your currently selected enemy if you are the host.
							# NOTE: The rest of the keyboard commands are host-only. These are the only ones for players as well.
Shift-Click				# This key combination will start drawing a line. Shift-Click again to finish drawing.
							# NOTE: Use the console command 'wipe' to clear all drawings.
Shift-Right-Click		# This key combination will create and select an enemy.
Right-Click				# This key will attempt to select an enemy at the area clicked.
Shift-BackSpace			# This key combination will delete the currently selected enemy.
```

PARTICIPATING IN BATTLES:
Battle mode allows for automatic management of turns. Here is a list of the commands used to manage battles:
```
battle		# This command will attempt to start a battle. All connected players must enter this command for the battle to start.
				# NOTE: You must be in a game for this to work.
done		# This command will end your turn.
hold		# This command will hold your turn, permanently moving you one forward in the turn order.
end			# This command will end the battle.
				# NOTE: This command can only be used by the host during his/her turn.
```

ADVANCED TUTORIAL:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

NOTICE: Do not begin the advanced tutorial until you have finished reading over the Basic Tutorial. Reading over the Advanced Tutorial is NOT necessary to use all of the core functions of RPGEngine. ONLY advanced users should consider reading over the advanced tutorial.

This tutorial will explain the uses for the remaining less-used commands that were not covered by the Basic Tutorial. The Advanced Tutorial will also include instructions on modifying and adding to RPGEngine.

### ADVANCED COMMANDS:
We'll begin the advanced tutorial by covering some of the more complicated console commands. Here are the rest of the commands not covered by the Basic Tutorial:
```
open						# This command will allow one extra player to join an in-progress game.
								# NOTE: This command must be used by the host when not in a battle.
errors						# This command will display a list of errors that were encountered upon previous executions of commands.
show a						# This command will display the value of 'a' directly without attempting to calculate what it is.
get							# This command will display a raw output of all the currently defined variables and functions.
sin:(x)						# This command will display the sine of 'x'. The colon may be omitted.
f(x) = x					# This command is used to create functions. This particular command can be read as 'f(x) = x'.
f(x) =  -1*x@x<0;  x		# This command is used to define piecewise functions. This particular command can be read as 'f(x) = (-1*x if x<0) or (x if else)'.
(0,1,2,3)~x~(x+1)			# This command will execute 'x+1' for when x is 0, 1, 2, and 3. The central ‘x~’ may be omitted.
run Extras.txt				# This command will run a file that contains commands.
extras = import Extras.py	# This command will import a specially-written RPGEngine python add-on. Instructions for writing these add-ons can be found lower down.
```

### CHANGING OPTIONS:
To change different RPGEngine options one should navigate to and open the file 'Rules.txt' within their RPGEngine directory. Once in that file changes can be made as necessary. Every line in the file that does not start with a '#' will be run as a command. Certain special variables must be defined in Rules.txt. They are:
```
str			# Attribute modifiers must be defined. Attribute scores are imported.
base_roll	# This defines the base roll to be made when the 'roll' command is used.
rest_health	# This defines the health restored when the 'rest' command is used.
```

### MODIFYING GRAPHICS:
RPGEngine uses different '.gif' files to build it's game space. Here are descriptions of those files and how to use them:
```
Player.gif	# This graphic defines what players look like. It should be square.
Enemy.gif	# This graphic defines what enemies look like. It should have the same dimensions as 'Player.gif'.
Pixel.gif	# This graphic is used for rendering lines. It should be a single pixel.
Grid.gif	# This graphic is optional and if present will be underlayed below the game space. This can be used to create backgrounds or display a grid.
```
