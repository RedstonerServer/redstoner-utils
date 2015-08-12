#!/usr/bin/env bash

# exit on failure
set -e

echo -e "> This will only set up Spigot and all the plugins, configuration files are still up to you to manage"
echo -e "> Press enter to coninue"
read

mkdir -v "redstoner"
cd "redstoner"

mkdir -v "server"

mkdir -v "build"
cd "build"

echo -e "\n> Downloading Spigot build tools"
curl --progress-bar -Lo "buildtools.jar" "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar"

echo -e "\n> Building Spigot, this will take a while ..."
java -jar BuildTools.jar > /dev/null

cp -v spigot-*.jar "../server/spigot.jar"
rm spigot-*.jar
cd "../server/"

mkdir -v "plugins"
cd "plugins"

echo ">> Downloading essentials.jar ..."
curl --progress-bar -Lo "essentials.jar" "https://github.com/RedstonerServer/Essentials/releases/download/stable-2.9.6-REDSTONER/Essentials-2.x-REDSTONER.jar"
echo ">> Downloading essentialschat.jar ..."
curl --progress-bar -Lo "essentialschat.jar" "https://hub.spigotmc.org/jenkins/job/Spigot-Essentials/lastSuccessfulBuild/artifact/EssentialsChat/target/EssentialsChat-2.x-SNAPSHOT.jar"
echo ">> Downloading imageonmap.jar ..."
curl --progress-bar -Lo "imageonmap.jar." "https://dev.bukkit.org/media/files/772/680/imageonmap.jar"
echo ">> Downloading logblock.jar ..."
curl --progress-bar -Lo "logblock.jar." "https://dev.bukkit.org/media/files/757/963/LogBlock.jar"
echo ">> Downloading logblockquestioner.zip ..."
curl --progress-bar -Lo "logblockquestioner.zip" "https://cloud.github.com/downloads/DiddiZ/LogBlockQuestioner/LogBlockQuestioner%20v0.03.zip"
echo ">> Downloading multiverse-core.jar ..."
curl --progress-bar -Lo "multiverse-core.jar" "https://dev.bukkit.org/media/files/588/781/Multiverse-Core-2.4.jar"
echo ">> Downloading multiverse-portals.jar ..."
curl --progress-bar -Lo "multiverse-portals.jar." "https://dev.bukkit.org/media/files/588/790/Multiverse-Portals-2.4.jar"
echo ">> Downloading multiverse-netherportals.jar ..."
curl --progress-bar -Lo "multiverse-netherportals.jar." "https://dev.bukkit.org/media/files/589/64/Multiverse-NetherPortals-2.4.jar"
echo ">> Downloading multiverse-inventories.jar ..."
curl --progress-bar -Lo "multiverse-inventories.jar." "https://dev.bukkit.org/media/files/663/303/Multiverse-Inventories-2.5.jar"
echo ">> Downloading permissionsex.jar ..."
curl --progress-bar -Lo "permissionsex.jar" "https://dev.bukkit.org/media/files/882/992/PermissionsEx-1.23.3.jar"
echo ">> Downloading plotme.jar ..."
curl --progress-bar -Lo "plotme.jar" "http://ci.worldcretornica.com/job/PlotMe-Core/244/artifact/target/PlotMe-Core.jar"
echo ">> Downloading plotme-defaultgenerator.jar ..."
curl --progress-bar -Lo "plotme-defaultgenerator.jar" "http://ci.worldcretornica.com/job/PlotMe-DefaultGenerator/83/artifact/target/PlotMe-DefaultGenerator.jar"
echo ">> Downloading serversigns.jar ..."
curl --progress-bar -Lo "serversigns.jar." "https://dev.bukkit.org/media/files/876/381/ServerSigns.jar"
echo ">> Downloading redstoneclockdetector.jar ..."
curl --progress-bar -Lo "redstoneclockdetector.jar." "https://dev.bukkit.org/media/files/577/253/RedstoneClockDetector.jar"
echo ">> Downloading vault.jar ..."
curl --progress-bar -Lo "vault.jar" "https://dev.bukkit.org/media/files/837/976/Vault.jar"
echo ">> Downloading worldborder.jar ..."
curl --progress-bar -Lo "worldborder.jar." "https://dev.bukkit.org/media/files/883/629/WorldBorder.jar"
echo ">> Downloading worldguard.jar ..."
curl --progress-bar -Lo "worldguard.jar." "https://github.com/RedstonerServer/WorldGuard/releases/download/6.0.0-redstoner/worldguard-6.0.0-REDSTONER.jar"
echo ">> Downloading worldedit.jar ..."
curl --progress-bar -Lo "worldedit.jar" "https://dev.bukkit.org/media/files/880/435/worldedit-bukkit-6.1.jar"
echo ">> Downloading pythonpluginloader.jar ..."
curl --progress-bar -Lo "pythonpluginloader.jar" "https://bamboo.gserv.me/browse/PLUG-PYPL/latestSuccessful/artifact/JOB1/Version-agnostic-jar/PyPluginLoader.jar"

echo -e "\n> Unpacking LogBlockQuestioner"
unzip -q "logblockquestioner.zip" "LogBlockQuestioner.jar"
rm "logblockquestioner.zip"
mv -v "LogBlockQuestioner.jar" "logblockquestioner.jar."

echo -e "\n> Pulling redstoner-utils ..."
git clone -q "git@github.com:RedstonerServer/redstoner-utils.git" "redstoner-utils.py.dir" > /dev/null

echo -e "\n> All plugins downloaded"

cd "redstoner-utils.py.dir"
echo -e "\n> Duplicating sample files"
for file in ls ./*.example; do
  cp -v "$file" "$(echo "$file" | rev | cut -d "." -f 2- | rev)"
done

cd "../.."

mkdir -v "lib"
cd "lib"

echo -e "\n> Downloading MySQL Connector ..."
curl --progress-bar -Lo "mysql-connector.zip" "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.36.zip"
echo "> Extracting MySQL Connector"
unzip -p mysql-connector.zip "mysql-connector-java-5.1.36/mysql-connector-java-5.1.36-bin.jar" > mysql-connector.jar
rm "mysql-connector.zip"

cd ".."

echo -e "\n> Creating startup script"

cat > start.sh <<EOF
#!/usr/bin/env bash
java -Xms512m -Xmx1g -jar spigot.jar
EOF
chmod +x start.sh

port="25565"
re='^[0-9]+$'
if [[ "$1" =~ $re ]]; then
  port="$1"
fi

echo "> Setting port to $port"
echo "> Generating server.properties"

cat > server.properties <<EOF
#Minecraft server properties
#Sat Jul 25 15:42:21 CEST 2015
spawn-protection=16
generator-settings=
force-gamemode=false
allow-nether=true
gamemode=1
broadcast-console-to-ops=true
enable-query=false
player-idle-timeout=0
difficulty=1
spawn-monsters=true
op-permission-level=4
resource-pack-hash=
announce-player-achievements=true
pvp=true
snooper-enabled=true
level-type=FLAT
hardcore=false
enable-command-block=false
max-players=20
network-compression-threshold=256
max-world-size=29999984
server-port=$port
server-ip=
spawn-npcs=true
allow-flight=false
level-name=world
view-distance=10
resource-pack=
spawn-animals=true
white-list=false
generate-structures=true
online-mode=true
max-build-height=256
level-seed=
use-native-transport=true
motd=Redstoner dev server
enable-rcon=false
EOF

echo -e "> Generating eula.txt"
echo "eula=true" > eula.txt

echo -e "\n> $(tput setf 2)All Done! $(tput sgr0)Don't forget to configure plugins for your needs."
echo "> Run redstoner/server/start.sh to start the server"
echo "> Our plugins are in redstoner/server/plugins/redstoner-utils.py.dir"