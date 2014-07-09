# RedstonerUtils

Redstoner's custom plugins, written in python.


# Installation / Set-up

1-line-install-script for bash:
`wget -O install.sh "http://pastie.org/pastes/9310905/download?key=6byp4mrqmiui8yqeo3s6yw"; md5sum --check <<<"3499671c0832e561bc9c7d476d2167cb  install.sh" && sh install.sh`

Detailed description:

0. Create a new directory called 'redstoner'
0. Download [the latest spigot](http://ci.md-5.net/job/Spigot/lastStableBuild/artifact/Spigot-Server/target/spigot.jar)
0. Run it once inside redstoner, then shut it down again
0. Create a new directory (inside redstoner) called 'lib'
0. Download [jython](http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.5.3/jython-standalone-2.5.3.jar) and save it as 'jython.jar' inside lib
0. Download [mysql-connector](https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.30.zip), extract 'mysql-connector-java-X.X.XX-bin.jar
' and save it as 'mysql-connector.jar' inside lib
0. Download [PyPluginLoader](http://gserv.me/static/PyPluginLoader-0.3.5.jar) (we're using [this fork](https://github.com/gdude2002/Python-Plugin-Loader)) into the plugins directory
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

Please use the script `<server-dir>/git_pull_utils.sh`.
**Do not use `git pull` on the server!**
All files must be owned and pulled by the *redstoner* user.

Be **very careful** with the live server! Make sure you're in the *master* branch and the code is working before pulling/restarting!


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


# Code styleguide & tips

## Indentation
Never use tabs!
Use 2 spaces to indent.

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

Please note that the line may not be accurate. You'll often get the start or end of a loop, method, or the like - when the actual error was somewhere in there.

In many cases, this is enough to find your bug. If you still cannot find it,try to catch exceptions in your code, as follows:


## Catching exceptions

If you want to catch all exceptions (e.g. for debugging), do not:
```python
try:
  # code
except Exception, e:
  print(e)
```
Since we're using jython, this will not catch Java exceptions.
This will give you some more deatails:
```python
import traceback
try:
  #code
except: # everything
  print(traceback.format_exc())
```