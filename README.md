# RedstonerUtils

Redstoner's custom plugins, written in python.


# Installation / Set-up

0. Create a new directory called 'redstoner'
0. Download [the latest spigot](http://ci.md-5.net/job/Spigot/lastStableBuild/artifact/Spigot-Server/target/spigot.jar)
0. Run it once inside redstoner, then shut it down again
0. Create a new directory (inside redstoner) called 'lib'
0. Download [mysql-connector](https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.30.zip), extract 'mysql-connector-java-X.X.XX-bin.jar
' and save it as 'mysql-connector.jar' inside lib
0. Download [PyPluginLoader](http://bamboo.gserv.me/browse/PLUG-PYPL/latestSuccessful/artifact/JOB1/Version-agnostic-jar/PyPluginLoader.jar) (we're using [this fork](https://github.com/gdude2002/Python-Plugin-Loader)) into the plugins directory
0. inside plugins, clone this directory into 'redstoner-utils**.py.dir**':  
`git clone git@bitbucket.org:redstonesheep/redstoner-utils.git redstoner-utils.py.dir`
0. Download [PEX](http://dev.bukkit.org/media/files/789/291/PermissionsEx.jar) into plugins
0. **if you want** to develop mysql things, set up a local MySQL server


# branches

* **dev**
  Always use this branch to change code, please test before pushing. (If something goes wrong here, that's okay)

* **master**
  Never commit into this branch directly! Only merge stable versions of *dev*:
  ```bash
  git checkout master
  git merge dev
  ```


# Deploying on the server

**Never** edit the files directly on the server!
The dev server uses the *dev* branch, the live server uses *master*.
**Do not use `git pull` on the server!** *(All files must be pulled/owned by the 'redstoner' user.)*

### Deploying on test server
* Push all changes
* Run `<server-dir>/git_pull_utils.sh`.
* Restart (You can try reloading here, but expect the unexpected)

### Deploying on production server
* Test all code carefully on the test server  
  ***on your machine:***
* `git checkout master`
* `git pull`
* `git merge dev`
* `git push -u origin master`
* `git checkout dev`  
  ***on the server:***
* `rs update_utils`
* Restart


# Modules / Files

If you add a new file, please update this list!

If you want the server to load a file (*module*) on startup, add it to the `modules` list in `main.py`.


* `files/`

  > All config / storage files go here

* `plugin.yml`

  > The plugin.yml file required for bukkut plugins

* `main.py`

  > The only file loaded by PyPluginLoader, loads all other modules  
  > Contains a few methods that **need to be cleaned up**

* `helpers.py`

  > Library that adds a bunch of re-usable methods which are used in nearly all other modules

* `adminchat.py`

  > Adds chat for staff using `/ac <text` or `,<text>`

* `chatgroups.py`

  > Adds group-chat with `/chatgroup` and `/cgt` to toggle normal chat into group mode

* `lagchunks.py`

  > Plugin to locate laggy chunks. `/lc <n>` lists chunks with more than `n` entities

* `mysqlhack.py`

  > A library that makes use of the so called ClassPathHack for jython to allow proper loading of `mysql-connector.jar` at runtime. import only, no methods.

* `plotter.py`

  > Start of a custom plot-plugin like PlotMe, on hold because the PlotMe developer continued to develop PlotMe

* `reports.py`

  > The `/report <text>` and `/rp` plugin

* `saylol.py`

  > Remake of sheep's old SayLol plugin, originally written as a standalone plugin in Java

* `skullclick.py`

  > Shows the owner of a skull when right-clicked

* `webtoken.py`

  > Adds `/token`, reads and writes from the database to generate *pronouncable* (and thus memorable) registration-tokens for the website

* `spawnplayer.py`

  > Code that was used once to create [this](http://www.reddit.com/r/Minecraft/comments/28le52/screenshot_of_all_players_that_joined_my_server/) awesome [screenshot](http://i.imgur.com/v4wg5kl.png)

* `tilehelper.py`

  > A plugin that automatically tiles (stacks) blocks inside a selected region in configurable directions.

* `mentio.py`

  > Adds `/listen`, highlights chat and plays a sound when your name was mentioned

* `cycler.py`

  > Adds `/cycler`, swaps the hotbar with inventory when player changes slot from right->left or left->right

* `motd.py`

  > Adds `/getmotd` & `/setmotd` to update the motd on the fly (no reboot).

* `abot.py`

  > AnswerBot. Hides stupid questions from chat and tells the sender about `/faq` or the like

* `damnspam.py`

  > Adds `/damnspam`, creates timeout for buttons/levers to mitigate button spam.

* `forcefield.py`

  > Adds '/forcefield', creates forcefield for players who want it.

# Code styleguide & tips

## Indentation
Never use tabs!
Use 2 spaces to indent.

## Quotes
Always use double-quotes!
Only use single-quotes when the string contains double-quotes that would need to be escaped.

## Capitalization
Do not use camelCase for variable or function names! Use under_score naming.
camelCase is okay when used like `import foo.bar.camelCase as camelCase`.

## Aligning variable assignments
In case you have multiple variable assignments, align the equals sign:

```Python
# bad
foo = 1
foobar = 2
a = 3

# good
foo    = 1
foobar = 2
a      = 3
```

Pro Tip: Use the AlignTab plugin for Sublime Text!

## Horizontal spacing
Use at least one space left and one space right to equals signs, and one space right to colons.

## Vertical spacing
Leave two empty lines before function definitions. In case you need to use `@hook.something`, add the two lines before that, directly followed by the definition.

## Meaningful names
Give function and variable names meaningful names. If you want to shorten long names, that's fine, but leave a comment on assigment with the actual meaning.

## Readability
Don't create long lines with lots of function calls. Split into multiple lines instead.
Also avoid methods with lots of lines. Split into multiple methods instead.

```Python
# bad
foo = int(player_data[str(server.getPlayer(args[4]).getUniqueId())]["details"].["last_login"].strftime("%s"))

# good
player     = server.getPlayer(args[4])
player_id  = uid(player)
logintime  = player_data[played_id]["last_login"]
epoch_time = int(logintime.strftime("%s"))
```

## Comments
Comments are good!
Please comment everything that's non-obious or makes it easier to understand

## Debugging
Debugging can be a bit special with jython/PyPluginLoader.

When something goes wrong, you probably see a weird traceback that's not telling you shit.
...unless you take a closer look.

You will not see a direct traceback of the python methods.
Instead, you'll probably see a bunch of java, bukkit and python things, because it tries to translate python into java, line per line.
Take a closer look at the method names, they might tell you what it's trying to do and where it's coming from.

Watch out for something like `org.python.pycode._pyx5.horribleCode$23(/path/to/badcode.py:214) ~[?:?]`
0. In this case, `_pyx5` is our module.
0. `horribleCode` is the method that was called
0. `/path/to/badcode.py` is the actual file of our module
0. `:214` is the line in which the error occured.

Please note that the line may not be accurate. You'll often get the start of a loop, or the end of a method - when the actual error was somewhere in there.

In many cases, this is enough to find your bug. If you still cannot find it,try to catch exceptions in your code, as follows:


## Catching exceptions

If you want to catch all exceptions (e.g. for debugging), do not `catch Exception`.
Since we're using jython, this will not catch Java exceptions.
This will give you some more deatails:
```python
from traceback import format_exc as trace
try:
  #code
except: # everything
  print(trace())
```