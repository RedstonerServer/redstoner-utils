# RedstonerUtils

Redstoner's custom plugins, written in python.


# Installation / Set-up

0. Create a new directory called 'redstoner'
0. Download [the latest bukkit](http://dl.bukkit.org/downloads/craftbukkit/get/latest-dev/craftbukkit.jar)
0. Run it once inside redstoner, then shut it down again
0. Create a new directory (inside redstoner) called 'lib'
0. Download [jython](http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.5.3/jython-standalone-2.5.3.jar) and save it as 'jython.jar' inside lib
0. Download [mysql-connector](https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.30.zip), extract 'mysql-connector-java-X.X.XX-bin.jar
' and save it as 'mysql-connector.jar' inside lib
0. Download [PyPluginLoader](http://gserv.me/static/PyPluginLoader-0.3.5.jar) into the plugins directory
0. Download [PEX](http://dev.bukkit.org/media/files/789/291/PermissionsEx.jar) into plugins
0. **if you want** to develop mysql things, set up a local MySQL server


# branches

* **dev**
  Always use this branch to change code, please test before pushing. (If something goes wrong here, that's okay)

* **master**
  Never commit into this branch directly! Only merge stable versions of *dev*


# Deploying

There ain't much to do. The dev server uses the *dev* branch, the live server uses *master*. Just pull and restart the server.

Be **very careful** with the live server! Make sure you're in the master branch and the code is working before pulling/restarting!


# Modules / Files

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

  > Adds `/token`, reads and writes from the database to generate *pronouncable* (and thus memorable) registration-tokens for the website.