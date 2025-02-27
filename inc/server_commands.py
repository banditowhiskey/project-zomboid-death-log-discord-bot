# Project Zomboid server commands
# Commands must be prepended with a '/' (foward slash command)
# This dict is organized as command == key and value == description.
# The organization will likely change. It more-so exists as is currently
# for purposes of documenting their existence.
SERVER_COMMANDS = {
"additem"          :  "gives items to players",
"addvehicle"       :  "spawn a vehicle",
"addxp"            :  "gives experience points to a player",
"alarm"            :  "sound a building alarm if inside a room",
"changeoption"     :  "changes server options",
"chopper"          :  "spawn a helicopter event on a random player",
"changepwd"        :  "changes player password",
"createhorde"      :  "spawns a horde ",
"godmode"          :  "activates player invincibility",
"gunshot"          :  "plays a gunshot sound near the player",
"help"             :  "opens help menu",
"invisibile"       :  "activates player invisibility",
"noclip"           :  "allows the player to move through solid objects",
"quit"             :  "saves and exits the server",
"releasesafehouse" :  "releases an owned safehouse",
"reloadoptions"    :  "reloads server options ",
"replay"           :  "records a replay",
"save"             :  "saves the world file",
"sendpulse"        :  "shows server performance",
"showoptions"      :  "shows server options",
"startrain"        :  "/stoprain - starts or stops rain weather effect",
"teleport"         :  "teleports to a player",
"teleportto"       :  "teleports to specified coordinates "
}
