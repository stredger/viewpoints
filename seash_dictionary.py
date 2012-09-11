"""
Author: Alan Loh

Module: A data structure of all the available commands of seash held in a
        dictionary of dictionaries format. Also holds the methods for
        parsing user command input and executing functions corresponding
        to the command.

User input is parsed according to whether or not it follows the structure 
of a command's dictionary and its children.  When parsing a command word, 
it simply checks to see if the user's input string list contains the command word 
at the appropriate index respective to the level of command dictionary currently
being iterated. If it is an user argument, however, it will
simply assign the user's inputted string as the key of the respective
argument's dictionary.

Command input is split by white spaces, so except for the case of arguments 
located at the end of the command string series, the parser will not taken 
into account file names or arguments that are multiple words long. Also, 
because of the way the command callback functions pull out user arguments, 
arguments of similar type need different 'name' field in its command dictionary
to help distinguish one from the other.
"""


# for access to list of targets
import seash_global_variables

import seash_exceptions

import command_callbacks



"""
Command dictionary entry format:
  '(command key)':{'name':'', 'callback':, 'priority':, 'help_text':'', 'children':[

'(command key)' - The expected command word the user is suppose to input to
call the command's function. If a certain type of argument is expected, a general
word in all caps should be enclosed within square brackets that signify the type 
of argument needed. For example, '[TARGET]' if a target ID is expected, or 
'[FILENAME]' if the name of a file is needed. Frequently used type includes 
'[TARGET]' for targets, '[KEYNAME]' for loaded keynames, '[FILENAME]' for files,
and '[ARGUMENT]' for everything else, so unless another category of arguments is 
needed, only use those four strings for command keys of arguments in order for 
the parser to work correctly.
 
For general commands like 'browse', however, the key would simply be the same 
command word, 'browse'. 

In general, the command key should only be a single word from the whole command 
string being implemented, and with the exception of Arguments that occur at the 
end of the command string, no user-inputted arguments should ever contain spaces.


'name':       - The name of the command word. For general commands, it should be 
the same as the command key. For arguments, however, the name should be 
distinguishable from other potential arguments of the same command key to avoid 
conflicts when pulling the user's argument from the input dictionary during 
command execution.


'callback':     - Reference to the command callback function associated with the
command string up to this point. Only command dictionaries that mark a complete 
command string should contain a reference to a callback method. Otherwise, it 
should be set to none. Default location of command callback functions is 
command_callbacks.py.


'priority'      - Gives the command callback function of the dictionary 
containing the key 'priority' the priority of being executed first before 
executing the main function of the command string. It should be implemented and 
assigned True if needed. Otherwise, it should not be added into any other command
dictionary.

An example of how it should work is in the case of 'as [KEYNAME] browse':
A keyname needs to be set before executing 'browse', so the command dictionary of
'[KEYNAME]' has 'priority' in being executed first to set the user's keyname 
before executing 'browse's command function.


'help_text'     - The text that will be outputted whenever a user accesses the 
help function for that command. Not every command dictionary needs a help text
associated with it, so it defaults as a blank string, and if none of the command 
dictionaries in the help call holds a help text, it will default at the last 
command dictionary that holds one, namely the dictionary associated with 'help'.


'children'      - The list of command dictionaries that follows the current one.
This will determine the validity of an command input when parsing. Each user
inputted string is verified that it follows one of the potential chains of 
command strings through the series of command dictionaries. Limit only one
argument dictionary per children list to avoid confusion when parsing user
argument input.
 
For example, in the command 'show resources', the children of the command 
dictionary for 'show' will contain the command dictionary 'resources' along with
any other potential command words that can follow 'show'.

"""


seashcommanddict = {
  'on':{'name':'on', 'callback':None, 'help_text':"""
on group
on group [command]

Sets the default group for future commands.   Most other commands will only 
operate on the vessels specified in the default group.  The default group is 
listed in the seash command prompt 'identity@group !>'.   The 'on' command can 
also be prepended to another command to set the group for only this command.


Example:

exampleuser@browsegood !> on WAN
exampleuser@WAN !>

exampleuser@browsegood !> on WAN show ip
1.2.3.4
5.6.7.8
exampleuser@browsegood !>
""", 'children':{
      '[TARGET]':{'name':'ontarget', 'callback':command_callbacks.on_target, 'priority':True, 'help_text':'', 'children':{
      }}
  }},


  'as':{'name':'as', 'callback':None, 'help_text':"""
as identity
as identity [command]

Sets the default identity for an operation.   The credentials (i.e. public
and private key) for this user are used for the following commands.   The 
default identity is listed in
the seash command prompt 'identity@group !>'.   The 'as' command can also
be prepended to another command to set the identity for just this command.

Example:

exampleuser@%all !> as tom
tom@%all !>

exampleuser@browsegood !> as tom browse
(browse output here)
exampleuser@browsegood !>
""", 'children':{
      '[KEYNAME]':{'name':'askeyname', 'callback':command_callbacks.as_keyname, 'priority':True, 'help_text':'', 'children':{
      }},
  }},


  'help':{'name':'help', 'callback':command_callbacks.help, 'priority':True, 'help_text':"""
A target can be either a host:port:vesselname, %ID, or a group name.

loadkeys fn [as identity]    -- Loads filename.publickey and filename.privatekey
as keyname [command]-- Run a command using an identity (or changes the default).
on target [command] -- Run a command on a target (or changes the default)
add [target] [to group]      -- Adds a target to a new or existing group 
remove [target] [from group] -- Removes a target from a group
show                         -- Displays shell state (see 'help show')
set                          -- Changes the shell or vessels (see 'help set')
browse                       -- Find vessels I can control
list                         -- Update and display information about the vessels
upload localfn (remotefn)    -- Upload a file
download remotefn (localfn)  -- Download a file (to multiple local files)
cat remotefn                 -- Display the contents of a remote file
delete remotefn              -- Delete a file
reset                        -- Reset the vessel (clear files / log and stop)
run file [args ...]          -- Upload a file and start executing it
stop                         -- Stop an experiment but leave the log / files
help [extended | set | show ]-- Try 'help extended' for more commands
exit                         -- Exits the shell

See https://seattle.cs.washington.edu/wiki/RepyTutorial for more info!""", 
    'children':{}
  },


  'extended':{'name':'extended', 'callback':command_callbacks.help, 'help_text':"""
Extended commands (not commonly used):

move target to group         -- Add target to group, remove target from default
loadstate fn -- Load encrypted shell state from a file with the keyname
savestate fn -- Save the shell's state information to a file with the keyname.
genkeys fn [len] [as identity] -- creates new pub / priv keys (default len=1024)
loadpub fn [as identity]     -- loads filename.publickey 
loadpriv fn [as identity]    -- loads filename.privatekey
start file [args ...]        -- Start an experiment (doesn't upload)
contact host:port[:vessel]   -- Communicate with a node explicitly
update                       -- Update information about the vessels
split resourcefn             -- Split another vessel off (requires owner)
join                         -- Join vessels on the same node (requires owner)
""", 'children':{}},

  'show':{'name':'show', 'callback':command_callbacks.show, 'help_text':"""
show info       -- Display general information about the vessels
show users      -- Display the user keys for the vessels
show ownerinfo  -- Display owner information for the vessels
show advertise  -- Display advertisement information about the vessels
show ip [to file] -- Display the ip addresses of the nodes
show hostname   -- Display the hostnames of the nodes
show location   -- Display location information (countries) for the nodes
show coordinates -- Display the latitude & longitude of the nodes
show owner      -- Display a vessel's owner
show targets    -- Display a list of targets
show identities -- Display the known identities
show keys       -- Display the known keys
show log [to file] -- Display the log from the vessel (*)
show files      -- Display a list of files in the vessel (*)
show resources  -- Display the resources / restrictions for the vessel (*)
show offcut     -- Display the offcut resource for the node (*)
show timeout    -- Display the timeout for nodes
show uploadrate -- Display the upload rate which seash uses to estimate
                   the required time for a file upload

(*) No need to update prior, the command contacts the nodes anew
""", 'children':{
      'info':{'name':'info', 'callback':command_callbacks.show_info, 'help_text':"""
show info

This command prints general information about vessels in the default group
including the version, nodeID, etc.

Example:
exampleuser@%1 !> show info
192.x.x.178:1224:v3 has no information (try 'update' or 'list')
exampleuser@%1 !> update
exampleuser@%1 !> show info
192.x.x.178:1224:v3 {'nodekey': {'e': 65537L, 'n': 929411623458072017781884599109L}, 'version': '0.1r', 'nodename': '192.x.x.175'}

""", 'children':{}},
      'users':{'pattern':'users', 'name':'users', 'callback':command_callbacks.show_users, 'help_text':"""
show users

This command lists the set of user keys for vessels in the default group.   
If the key has been loaded into seash as an identity, this name will be used.

Example:
exampleuser@browsegood !> show users
192.x.x.178:1224:v3 has no information (try 'update' or 'list')
192.x.x.2:1224:v12 has no information (try 'update' or 'list')
192.x.x.2:1224:v3 has no information (try 'update' or 'list')
exampleuser@browsegood !> update
exampleuser@browsegood !> show users
192.x.x.178:1224:v3 (no keys)
192.x.x.2:1224:v12 65537 136475...
192.x.x.2:1224:v3 exampleuser

""", 'children':{}},
      'ownerinfo':{'name':'ownerinfo', 'callback':command_callbacks.show_ownerinfo, 'help_text':"""
show ownerinfo

This lists the ownerinfo strings for vessels in the default group.   See
'set ownerinfo' for more details
""", 'children':{}},
      'advertise':{'name':'advertise', 'callback':command_callbacks.show_advertise, 'help_text':"""
show advertise

This indicates whether the node manager will advertise the vessel's keys in 
the advertise services.   See 'set advertise' for more details.
""", 'children':{}},
      'ip':{'name':'ip', 'callback':command_callbacks.show_ip, 'help_text':"""
show ip 
show ip [to file]

This lists the ip addresses of the vessels in the default group.   These IP
addresses may be optionally written to a file.   

Note that machines behind a NAT, mobile devices, or other systems with 
atypical network connectivity may list a host name instead.

Example:
exampleuser@ !> show targets
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%4 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v12']
%3 ['193.x.x.42:1224:v18']
%2 ['192.x.x.2:1224:v3']
exampleuser@ !> on browsegood
exampleuser@browsegood !> show ip
192.x.x.2
193.x.x.42
219.x.x.62

""", 'children':{
          'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
              '[FILENAME]':{'name':'filename', 'callback':command_callbacks.show_ip_to_file, 'help_text':'', 'children':{}},
          }},
          '>':{'name':'>', 'callback':None, 'help_text':'', 'children':{
              '[FILENAME]':{'name':'filename', 'callback':command_callbacks.show_ip_to_file, 'help_text':'', 'children':{}},
          }},
      }},
      'hostname':{'name':'hostname', 'callback':command_callbacks.show_hostname, 'help_text':"""
show hostname

This lists the DNS host names for the vessels in the default group.   If this
information is not available, this will be listed.

Example:
exampleuser@browsegood !> show ip
192.x.x.2
193.x.x.42
219.x.x.62
exampleuser@browsegood !> show hostname
192.x.x.2 is known as Guest-Laptop.home
193.x.x.42 is known as pl2.maskep.aerop.fr
219.x.x.62 has unknown host information

""", 'children':{}},
      'location':{'name':'location', 'callback':command_callbacks.show_location, 'help_text':"""
show location

Uses a geo-IP location service to return information about the position of the
nodes in the current group.

Example:
exampleuser@browsegood !> show ip
192.x.x.2
193.x.x.42
219.x.x.62
exampleuser@browsegood !> show location
%1(192.x.x.2): Location unknown
%3(193.x.x.42): Cesson-svign, France
%4(219.x.x.62): Beijing, China

""", 'children':{}},
      'coordinates':{'name':'coordinates', 'callback':command_callbacks.show_coordinates, 'help_text':"""
show coordinates

Uses a geo-IP location service to get approximate latitude and longitude 
information about nodes in the current group.

Example:
exampleuser@browsegood !> show location
%1(192.x.x.2): Location unknown
%3(193.x.x.42): Cesson-svign, France
%4(219.x.x.62): Beijing, China
exampleuser@browsegood !> show coordinates
%1(192.x.x.2): Location unknown
%3(193.x.x.42): 48.1167, 1.6167
%4(219.x.x.62): 39.9289, 116.3883

""", 'children':{}},
      'owner':{'name':'owner', 'callback':command_callbacks.show_owner, 'help_text':"""
show owner

Displays the owner key (or identity if known) for the vessels in the default
group.

Example:
exampleuser@ !> show targets
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%4 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v12']
%3 ['193.x.x.42:1224:v18']
%2 ['192.x.x.2:1224:v3']
exampleuser@ !> on browsegood
exampleuser@browsegood !> show owner
192.x.x2:1224:v12 exampleuser pubkey
192.x.x.2:1224:v3 65537 127603...
193.x.x.42:1224:v18 65537 163967...
219.x.x.62:1224:v4 65537 952875...

""", 'children':{}},
      'targets':{'name':'targets', 'callback':command_callbacks.show_targets, 'help_text':"""
show targets

Lists the known targets (groups and individual nodes) that commands may be 
run on.

Example:
exampleuser@ !> show targets
%all (empty)
exampleuser@ !> browse
['192.x.x.2:1224', '219.x.x.62:1224', '193.x.x.42:1224']
Added targets: %3(193.x.x.42:1224:v18), %4(219.x.x.62:1224:v4), %1(192.x.x.2:1224:v12), %2(192.x.x.2:1224:v3)
Added group 'browsegood' with 4 targets
yaluen@ !> show targets
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%4 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v12']
%3 ['193.x.x.42:1224:v18']
%2 ['192.x.x.2:1224:v3']

""", 'children':{}},
      'identities':{'name':'identities', 'callback':command_callbacks.show_identities, 'help_text':"""
show identities

Lists the identities loaded into the shell and whether the public or private
keys are loaded.   This does not display the keys themselves (see 'show keys').

Example:
 !> show identities
 !> loadkeys exampleuser
 !> loadkeys guest0
 !> loadkeys guest1
 !> show identities
guest2 PRIV
exampleuser PUB PRIV
guest0 PUB PRIV
guest1 PUB PRIV

""", 'children':{}},
      'keys':{'name':'keys', 'callback':command_callbacks.show_keys, 'help_text':"""
show keys

List the actual keys loaded by the shell.   To see identity information, see
'show identities'.

Example:
 !> show keys
 !> loadkeys yaluen
 !> loadpub guest0
 !> loadpriv guest1
 !> show keys
exampleuser {'e': 65537L, 'n': 967699203053798948061567293973111925102424779L} {'q': 130841985099129780748709L, 'p': 739593793918579524787167931524344434698161314501292256851220768397231L, 'd': 9466433905223884723074560052831388470409993L}
guest0 {'e': 65537L, 'n': 9148459067481753275566379538357634516166379961L} None
guest1 None {'q': 121028014346935113507847L, 'p': 107361553689073802754887L, 'd': 127298628609806695961451784003754746302524139001L}

""", 'children':{}},
      'log':{'name':'log', 'callback':command_callbacks.show_log, 'help_text':"""
show log [to filename]

Lists the log of operations from the vessel.   This log is populated by print
statements and exceptions from the program running in the vessel.
""", 'children':{
          'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
              '[FILENAME]':{'name':'filename', 'callback':command_callbacks.show_log_to_file, 'help_text':'', 'children':{}},
          }},
      }},
      'files':{'name':'files', 'callback':command_callbacks.show_files, 'help_text':"""
show files

Lists the names of the files loaded into vessels in the default groups.   
This is similar to dir or ls.

Example:
exampleuser@browsegood !> show files
Files on '192.x.x.2:1224:v3': ''
Files on '193.x.x.42:1224:v18': ''
Files on '219.x.x.62:1224:v4': ''
exampleuser@browsegood !> upload example.1.1.repy
exampleuser@browsegood !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.repy'
Files on '193.x.x.42:1224:v18': 'example.1.1.repy'
Files on '219.x.x.62:1224:v4': 'example.1.1.repy'

""", 'children':{}},
      'resources':{'name':'resources', 'callback':command_callbacks.show_resources, 'help_text':"""
show resources

Lists the resources allotted to vessels in the default group.
""", 'children':{}},
      'offcut':{'name':'offcut', 'callback':command_callbacks.show_offcut, 'help_text':"""
show offcut

This lists the amount of resources that will be lost by splitting a vessel or
gained by joining two vessels.   This is shown on a per-node basis amongst
all vessels in the default group
""", 'children':{}},
      'timeout':{'name':'timeout', 'callback':command_callbacks.show_timeout, 'help_text':"""
show timeout

This shows the amount of time the shell will wait for a command to timeout.   
Note that commands like 'run' and 'upload' will use both this value and the
uploadrate setting

Example:
 !> show timeout
10

""", 'children':{}},
      'uploadrate':{'name':'uploadrate', 'callback':command_callbacks.show_uploadrate, 'help_text':"""
show uploadrate

This lists the minimum rate at which the shell should allow uploads to occur.
Uploads to vessels that go slower than this will be aborted.   Note that this
is used in combination with the timeout setting.

Example:
 !> show uploadrate
102400

""", 'children':{}},
  }},


  'run':{'name':'run', 'callback':None, 'help_text':"""
run programname [arg1, arg2, ...]

Uploads programname to a vessel and starts it running.   (This command is 
actually just a short-cut for the 'upload' and 'start' commands).   The 
arguments listed will be passed to the command when it is started.

Example:
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':

Log from '193.x.x.42:1224:v18':

Log from '219.x.x.62:1224:v4':

Log from '192.x.x.2:1224:v12':

exampleuser@browsegood !> run example.1.1.repy
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':
Hello World

Log from '193.x.x.42:1224:v18':
Hello World

Log from '219.x.x.62:1224:v4':
Hello World

Log from '192.x.x.2:1224:v12':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.run_localfn, 'help_text':'','children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.run_localfn_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'add':{'name':'add', 'callback':None, 'help_text':"""
add target [to group]
add to group

Adds a target (a vessel name or group) a group.   If the group does not exist,
it is created.   This can be used to control which vessels are manipulated by 
different commands.   The short form 'add target' adds the target to the 
default group.   The short form 'add to group' adds the default group to
the target.

If the target is already in the group, an error message will be printed.

Example:
exampleuser@%1 !> on new_group
Invalid command input: Target does not exist
exampleuser@%1 !> add to new_group
exampleuser@%1 !> add %2 to new_group
exampleuser@%1 !> on new_group
exampleuser@new_group !> list
  ID Own                      Name     Status              Owner Information
  %1  *        192.x.x.178:1224:v3      Fresh                               
  %2  *         192.x.x.2:1224:v12      Fresh    

""", 'children':{
      '[TARGET]':{'name':'target', 'callback':command_callbacks.add_target, 'help_text':'', 'children':{
          'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.add_target_to_group, 'help_text':'', 'children':{}},
          }},
      }},
      'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.add_to_group, 'help_text':'', 'children':{}},
      }},
  }},


  'move':{'name':'move', 'callback':None, 'help_text':"""
move target to group

This is essentially a shortcut for removing the target from the default group
and adding it to group.   See 'add' and 'remove' for more information.
""", 'children':{
      '[TARGET]':{'name':'target', 'callback':None, 'help_text':'', 'children':{
          'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
              '[GROUP]':{'name':'group', 'callback':command_callbacks.move_target_to_group, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'remove':{'name':'remove', 'callback':None, 'help_text':"""
remove target [from group]
remove from group

This command removes a target (vesselname or group) from a group.   This means
that future group operations will not include the listed vesselname or group.
The short form 'remove target' removes the target from the default group.
The short form 'remove from group' removes the default group from group.

If the target is not in the group, an error message will be printed.

Example:
exampleuser@new_group !> list
  ID Own                      Name     Status              Owner Information
  %1  *        192.x.x.178:1224:v3      Fresh                               
  %2  *         192.x.x.2:1224:v12      Fresh    
  %3             192.x.x.2:1224:v3      Fresh      
exampleuser@new_group !> on %1
exampleuser@%1 !> remove from new_group
exampleuser@%1 !> remove %2 from new_group
exampleuser@%1 !> on new_group
exampleuser@new_group !> list
  ID Own                      Name     Status              Owner Information
  %3             192.x.x.2:1224:v3      Fresh   

""", 'children':{
      '[TARGET]':{'name':'target', 'callback':command_callbacks.remove_target, 'help_text':'', 'children':{
          'from':{'name':'from', 'callback':None, 'help_text':'', 'children':{
              '[GROUP]':{'name':'group', 'callback':command_callbacks.remove_target_from_group, 'help_text':'', 'children':{}},
          }},
      }},
      'from':{'name':'from', 'callback':None, 'help_text':'', 'children':{
          '[GROUP]':{'name':'group', 'callback':command_callbacks.remove_from_group, 'help_text':'', 'children':{}},
      }},
  }},


  'set':{'name':'set', 'callback':command_callbacks.set, 'help_text':"""
Commands requiring owner credentials on a vessel:
set users [ identity ... ]  -- Change a vessel's users
set ownerinfo [ data ... ]    -- Change owner information for the vessels
set advertise [ on | off ] -- Change advertisement of vessels
set owner identity        -- Change a vessel's owner

Shell settings:
set timeout count  -- Sets the time that seash is willing to wait on a node
set uploadrate speed -- Sets the upload rate which seash will use to estimate
                        the time needed for a file to be uploaded to a vessel.
                        The estimated time would be set as the temporary 
                        timeout count during actual process. Speed should be 
                        in bytes/sec.
set autosave [ on | off ] -- Sets whether to save the state after every command.
                             Set to 'off' by default. The state is saved to a
                             file called 'autosave_keyname', where keyname is 
                             the name of the current key you're using.
""", 'children':{
      'users':{'name':'users', 'callback':None, 'help_text':"""
set users [identity1, identity2, ...]

Sets the user keys for vessels in the default group.   The current identity
must own the vessels.

Example:
exampleuser@%1 !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
exampleuser@%1 !> show users
192.x.x.2:1224:v12 65537 136475...
exampleuser@%1 !> set users guest0 guest1 guest2
exampleuser@%1 !> update
exampleuser@%1 !> show users
192.x.x.2:1224:v12 guest0 guest1 guest2
exampleuser@%1 !> on %2
exampleuser@%2 !> show owner
192.x.x.2:1224:v3 65537 127603...
exampleuser@%2 !> set users guest0 guest1
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_users_arg, 'help_text':'', 'children':{}},
      }},
      'ownerinfo':{'name':'ownerinfo', 'callback':None, 'help_text':"""
set ownerinfo 'string'

This command sets the owner information for each vessel in the default group.
The default identity must own the vessels.

Example:
exampleuser@browsegood !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
192.x.x.2:1224:v3 65537 127603...
exampleuser@browsegood !> show ownerinfo
192.x.x.2:1224:v12 ''
192.x.x.2:1224:v3 ''
exampleuser@browsegood !> set ownerinfo Example owner info
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3
Added group 'ownerinfogood' with 1 targets and 'ownerinfofail' with 1 targets
exampleuser@browsegood !> update
exampleuser@browsegood !> show ownerinfo
192.x.x.2:1224:v12 'Example owner info'
192.x.x.2:1224:v3 ''

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_ownerinfo_arg, 'help_text':'', 'children':{}},
      }},
      'advertise':{'name':'advertise', 'callback':None, 'help_text':"""
set advertise [on/off]

This setting is changable only by the vessel owner and indicates whether or
not the node's IP / port should be advertised under the owner and user keys.
The default value is on.   With this turned off, the 'browse' command will
be unable to discover the vessel.

exampleuser@%1 !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
exampleuser@%1 !> show advertise
192.x.x.2:1224:v12 on
exampleuser@%1 !> set advertise off
exampleuser@%1 !> update
exampleuser@%1 !> show advertise
192.x.x.2:1224:v12 off
exampleuser@%1 !> on %2
exampleuser@%2 !> show owner
192.x.x.2:1224:v3 65537 127603...
exampleuser@%2 !> show advertise
192.x.x.2:1224:v3 on
exampleuser@%2 !> set advertise off
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_advertise_arg, 'help_text':'', 'children':{}},
      }},
      'owner':{'name':'owner', 'callback':None, 'help_text':"""
set owner identity

This changes the owner key for all vessels in the default group to the
identity specified.   This command may only be issued by the vessels' current
owner.

Example:
exampleuser@%1 !> show identities
exampleuser PUB PRIV
guest0 PUB PRIV
guest1 PUB PRIV
exampleuser@%1 !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
exampleuser@%1 !> set owner guest0
exampleuser@%1 !> update
exampleuser@%1 !> show owner
192.x.x.2:1224:v12 guest0 pubkey
exampleuser@%1 !> on %2
exampleuser@%2 !> show owner
192.x.x.2:1224:v3 65537 127603...
exampleuser@%2 !> set owner exampleuser
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_owner_arg, 'help_text':'', 'children':{}},
      }},
      'timeout':{'name':'timeout', 'callback':None, 'help_text':"""
set timeout timeoutval

This sets the timeout for network related commands.   Most commands will then
be aborted on nodes if they are not completed withing the timeoutval number of
seconds.   Note that the upload and run commands also use the uploadrate 
setting to determine their timeout.

Example:
exampleuser@%1 !> set timeout 1
exampleuser@%1 !> show timeout
1
exampleuser@%1 !> start example.1.1.repy
Failure 'signedcommunicate failed on session_recvmessage with error 'recv() timed out!'' uploading to 193.x.x.42:1224:v18
exampleuser@%1 !> set timeout 10
exampleuser@%1 !> start example.1.1.repy
exampleuser@%1 !> show log
Log from '193.x.x.42:1224:v18':
Hello World

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_timeout_arg, 'help_text':'', 'children':{}},
      }},
      'uploadrate':{'name':'uploadrate', 'callback':None, 'help_text':"""
set uploadrate rate_in_bps

This value is used along with the timeout value to determine when to declare an
upload or run command as failed.   The wait time is computed as:
   timeout + filesize / rate_in_bps

Thus if the timeout is 10 seconds and rate_in_bps is 102400 (100 KB / s), a 1MB 
will attempt to upload for 20 seconds.

Example:
exampleuser@%1 !> set uploadrate 99999999999999
exampleuser@%1 !> set timeout 1
exampleuser@%1 !> upload example.1.1.repy
Failure 'signedcommunicate failed on session_recvmessage with error 'recv() timed out!'' uploading to 193.x.x.42:1224:v18
exampleuser@%1 !> set uploadrate 102400
exampleuser@%1 !> upload example.1.1.repy
exampleuser@%1 !> 

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_uploadrate_arg, 'help_text':'', 'children':{}},
      }},
      'autosave':{'name':'autosave', 'callback':None, 'help_text':"""
set autosave [on/off]

When turned on, the shell settings such as keys, targets, timeout value, etc.
will all be persisted to disk after every operation.   These are saved in a
file called 'autosave_(user's keyname)', which is encrypted with the default identity.   The user
can then restore the shell's state by typing 'loadstate identity'.

Example:
exampleuser@%1 !> set autosave on
exampleuser@%1 !> exit
(restart seash.py)
 !> loadkeys exampleuser
 !> as exampleuser
exampleuser@ !> loadstate autosave_exampleuser
exampleuser@%1 !>

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_autosave_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'browse':{'name':'browse', 'callback':command_callbacks.browse, 'help_text':"""
browse [advertisetype]

This command will use the default identity to search for vessels that can
be controlled.   Any vessel with the advertise flag set will be advertised
in at least one advertise service.   browse will look into these services
and add any vessels it can contact.

Setting advertisetype will restrict the advertise lookup to only use that 
service.   Some permitted values for advertisetype are central, DHT, and DOR.

Example:
exampleuser@ !> show targets
%all (empty)
exampleuser@ !> browse
['192.x.x.2:1224', '193.x.x.42:1224', '219.x.x.62:1224']
Added targets: %2(193.x.x.42:1224:v18), %3(219.x.x.62:1224:v4), %1(192.x.x.2:1224:v3)
Added group 'browsegood' with 3 targets
exampleuser@ !> show targets
browsegood ['192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%3 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v3']
%2 ['193.x.x.42:1224:v18']

""", 'children':{
      '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.browse_arg, 'help_text':'', 'children':{}},
  }},


  'genkeys':{'name':'genkeys', 'callback':None, 'help_text':"""
genkeys keyprefix [as identity]

Generates a new set of keys, writing them to files keyprefix.publickey and
keyprefix.privatekey.   It also adds the identity under the name given.  If
identity is not specified, keyprefix is used.

Example:
 !> genkeys userA as userB
Created identity 'userB'
 !> show identities
userB PUB PRIV
 !> loadkeys userA
 !> show identities
userB PUB PRIV
userA PUB PRIV

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.genkeys_filename, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.genkeys_filename_len, 'help_text':'', 'children':{
              'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
                  '[ARGUMENT]':{'name':'keyname', 'callback':command_callbacks.genkeys_filename_len_as_identity, 'help_text':'', 'children':{}},
              }},
          }},
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'keyname', 'callback':command_callbacks.genkeys_filename_as_identity, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'loadkeys':{'name':'loadkeys', 'callback':None, 'help_text':"""
loadkeys keyprefix [as identity]

Loads a public key named keyprefix.publickey and a private key named
keyprefix.privatekey.   This is a shortcut for the 'loadpub' and 'loadpriv'
operations.   If identity is specified, the shell refers to the keys using
this.   If not, keyprefix is the identity.

Example:
 !> loadkeys exampleuser
 !> show identities
exampleuser PUB PRIV
 !> as exampleuser
exampleuser@ !>

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadkeys_keyname, 'help_text':'', 'children':{
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.loadkeys_keyname_as, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'loadpub':{'name':'loadpub', 'callback':None, 'help_text':"""
loadpub pubkeyfile [as identity]

Loads a public key named keyprefix.publickey.  If identity is specified, the 
shell refers to the keys using this.   If not, keyprefix is the identity.

Example:
 !> loadpub exampleuser
 !> show identities
exampleuser PUB

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadpub_filename, 'help_text':'', 'children':{
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.loadpub_filename_as, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'loadpriv':{'name':'loadpriv', 'callback':None, 'help_text':"""
loadpriv privkeyfile [as identity]

Loads a private key named keyprefix.privatekey.  If identity is specified, the 
shell refers to the keys using this.   If not, keyprefix is the identity.

Example:
 !> loadpriv exampleuser
 !> show identities
exampleuser PRIV

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadpriv_filename, 'help_text':'', 'children':{
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.loadpriv_filename_as, 'help_text':'', 'children':{}},
          }},
      }},
  }},

  
  'list':{'name':'list', 'callback':command_callbacks.list, 'help_text':"""
list

Display status information about a set of vessels.   This indicates whether
the vessels are running programs, if the default identity is the owner or
just a user, along with other useful information.

Example:
exampleuser@browsegood !> list
  ID Own                      Name     Status              Owner Information
  %1  *        192.x.x.178:1224:v3      Fresh                               
  %2  *         192.x.x.2:1224:v12      Fresh                               
  %3             192.x.x.2:1224:v3      Fresh  

""", 'children':{}},


  'upload':{'name':'upload', 'callback':None, 'help_text':"""
upload srcfilename [destfilename]

Uploads a file into all vessels in the default group.   The file name that is
created in those vessels is destfilename (or srcfilename by default).

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': ''
exampleuser@%1 !> upload example.1.1.repy
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.repy'

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.upload_filename, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.upload_filename_remotefn, 'help_text':'', 'children':{}}
      }},
  }},


  'download':{'name':'download', 'callback':None, 'help_text':"""
download srcfilename [destfilename]

Retrieves a copy of srcfilename from every vessel in the default group.   The
file is written as the destfilename.vesselname (with ':' replaced with '_').
If the destfilename is not specified, srcfilename is used instead.

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.repy'
exampleuser@%1 !> download example.1.1.repy
Wrote files: example.1.1.repy.192.x.x.2_1224_v3 
yaluen@%1 !> download example.1.1.repy test_download
Wrote files: test_download.192.x.x.2_1224_v3 

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.download_filename, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.download_filename_localfn, 'help_text':'', 'children':{}}
      }},
  }},


  'delete':{'name':'delete', 'callback':None, 'help_text':"""
delete filename

Erases filename from every vessel in the default group.

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.repy'
exampleuser@%1 !> delete example.1.1.repy
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': ''

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.delete_remotefn, 'help_text':'', 'children':{}},
  }},

  'cat':{'name':'cat', 'callback':None, 'help_text':"""
cat filename

Displays the content of filename from every vessel in the default group.

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.repy'
exampleuser@%1 !> cat example.1.1.repy

File 'example.1.1.repy' on '192.168.1.2:1224:v3': 
if callfunc == 'initialize':
  print "Hello World"

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.cat_filename, 'help_text':'', 'children':{}},
  }},


  'reset':{'name':'reset', 'callback':command_callbacks.reset, 'help_text':"""
reset

Clears the log, stops any programs, and deletes all files from every vessel
in the default group.

Example:
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1           192.x.x.2:1224:v3 Terminated                               
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.repy'
exampleuser@%1 !> reset
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':

exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1           192.x.x.2:1224:v3      Fresh                               
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': '' 

""", 'children':{}},


  'start':{'name':'start', 'callback':None, 'help_text':"""
start programname [arg1 arg2 ...]

Begins executing a file in the vessel named programname with the given 
arguments.   This program must first be uploaded to the vessel (the 'run'
command does this for the user).

Example:
exampleuser@%1 !> upload example.1.1.repy
exampleuser@%1 !> start example.1.1.repy
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.start_remotefn, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.start_remotefn_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'stop':{'name':'stop', 'callback':command_callbacks.stop, 'help_text':"""
stop

Stops executing the running program in every vessel in the default group.   
The program will halt as though it were killed / interrupted.   The status
for these vessels will become 'Stopped'.

Example:
exampleuser@%1 !> run endless_loop.repy 
exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1             192.x.x.2:1224:v3    Started                               
exampleuser@%1 !> stop
exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1             192.x.x.2:1224:v3    Stopped                                

""", 'children':{}},


  'split':{'name':'split', 'callback':None, 'help_text':"""
split resourcefile

Divides the vessels in the default group into two new vessels.   The first
vessel will have the size specified in the resource file.   The second will
have the remaining size, minus the size of the offcut resources.   The new
vessels will be known to the shell. 

You must be the owner of the vessel to use the split command.

Example:
exampleuser@browsegood !> show targets
browsegood (empty)
joingood ['192.x.x.192:1224:v3', '192.x.x.192:1224:v4']
joinfail (empty)
%all ['192.x.x.192:1224:v11']
%3 ['192.x.x.192:1224:v11']
exampleuser@browsegood !> on %3
exampleuser@%3 !> split resources.offcut
192.x.x.192:1224:v11 -> (192.x.x.192:1224:v12, 192.x.x.192:1224:v13)
Added group 'split1' with 1 targets and 'split2' with 1 targets
exampleuser@%3 !> show targets
split2 ['192.x.x.192:1224:v13']
split1 ['192.x.x.192:1224:v12']
browsegood (empty)
joingood ['192.x.x.192:1224:v3', '192.x.x.192:1224:v4']
joinfail (empty)
%5 ['192.x.x.192:1224:v13']
%4 ['192.x.x.192:1224:v12']
%all ['192.x.x.192:1224:v12', '192.x.x.192:1224:v13']

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.split_resourcefn, 'help_text':'', 'children':{}},
  }},


  'join':{'name':'join', 'callback':command_callbacks.join, 'help_text':"""
join

Joins any vessels in the default group that are on the same node.   The 
resulting vessel will have a size equal to the two other vessels plus the
offcut resource amount.  The new vessels will be known to the shell. 

You must be the owner of the vessels to join them.

Example:
exampleuser@browsegood !> join
Traceback (most recent call last):
  File "seash.py", line 222, in command_loop
  File "/home/user/seattle_test/seash_dictionary.py", line 1458, in command_dispatch
  File "/home/user/seattle_test/command_callbacks.py", line 2485, in join
KeyError: 'ownerkey'
exampleuser@browsegood !> update
exampleuser@browsegood !> show owner
192.x.x.192:1224:v3 guest0 pubkey
192.x.x.192:1224:v4 guest0 pubkey
exampleuser@browsegood !> join
192.x.x.192:1224:v11 <- (192.x.x.192:1224:v3, 192.x.x.192:1224:v4)
Added group 'joingood' with 2 targets
exampleuser@browsegood !> show targets
browsegood (empty)
joingood ['192.x.x.192:1224:v3', '192.x.x.192:1224:v4']
joinfail (empty)
%all ['192.x.x.192:1224:v11']
%3 ['192.x.x.192:1224:v11']

""", 'children':{}},


  'exit':{'name':'exit', 'callback':command_callbacks.exit, 'help_text':"""
exit

Exits seash.
""", 'children':{}},


  'loadstate':{'name':'loadstate', 'callback':None, 'help_text':"""
loadstate filename

Loads state information from filename using the default identity to decrypt
the file.   This will restore all identities, keys, groups, etc. from a 
previous seash run.  See also 'set autosave on/off.'

Example:
exampleuser@%1 !> savestate testing_state
exampleuser@%1 !> exit
(restart seash.py)
 !> loadkeys exampleuser
 !> as exampleuser
exampleuser@ !> loadstate testing_state
exampleuser@%1 !>

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadstate_filename, 'help_text':'', 'children':{}},
  }},


  'savestate':{'name':'savestate', 'callback':None, 'help_text':"""
savestate filename

Saves state information into a filename, encrypting the data with the default 
identity's private key.  This can be later used to restore the shell's 
settings, groups, and other information.   See also 'set autosave on/off.'

Example:
exampleuser@%1 !> savestate testing_state
exampleuser@%1 !> exit
(restart seash.py)
 !> loadkeys exampleuser
 !> as exampleuser
exampleuser@ !> loadstate testing_state
exampleuser@%1 !>

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.savestate_filename, 'help_text':'', 'children':{}},
  }},


  'update':{'name':'update', 'callback':command_callbacks.update, 'help_text':"""
update

Reacquire cached state from the vessels.   This state is used for many of the
'show' commands to prevent every operation from needing to contact all vessels.

Example:
exampleuser@%1 !> show info
192.x.x.2:1224:v3 has no information (try 'update' or 'list')
exampleuser@%1 !> update
exampleuser@%1 !> show info
192.x.x.2:1224:v3 {'nodekey': {'e': 65537L, 'n': 924563171010915569497668794725930165347860823L}, 'version': '0.1t', 'nodename': '192.x.x.2'}

""", 'children':{}},


  'contact':{'name':'contact', 'callback':None, 'help_text':"""
contact IP:port[:vesselname]

Add the specified vessel to the shell.   This bypasses advertise lookups and
directly contacts the node manager.   If the vesselname argument is omitted,
all vessels that can be controlled by the default identity are added.

Example:
exampleuser@ !> contact 192.x.x.2:1224
Added targets: %1(192.x.x.2:1224:v3)

""", 'children':{
      '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.contact, 'help_text':'', 'children':{}},
  }},

}


# A dictionary to be built to keep track of the different variations of commands users will input
commandvariationdict = {
  'users':['user'],
  'hostname':['hostnames'],
  'location':['locations'],
  'coordinates':['coordinate'],
  'owner':['owners'],
  'timeout':['timeouts'],
  'targets':['target'],
  'uploadrate':['uploadrates'],
  'identities':['identity'],
  'ip':['ips'],
  'keys':['key'],
  'files':['file'],
  'resources':['resource'],
  'offcut':['offcuts'],
  'genkeys':['genkey'],
  'loadkeys':['loadkey'],
  'exit':['quit']
}


##### All methods that adds to the seash command dictionary #####


# Creates a deep copy of the seash dictionary while avoiding any of the 
# commands in the passed list.
# Only works in the first level of the dictionary. Will not search for the 
# existence of the avoided command in deeper levels of the dictionary.
def _deep_copy_main_dict(avoided_cmds_list):

  command_dict_copy = seashcommanddict.copy()

  # For every command pattern found in the passed list,
  # the function will delete it from
  for cmd in avoided_cmds_list:

    if cmd in command_dict_copy:

      del command_dict_copy[cmd]
  

  return command_dict_copy




# Returns a copy of a command's dictionary with an empty dictionary for its children
def _shallow_copy(cmd_dict):
  cmd_dict_copy = cmd_dict.copy()
  cmd_dict_copy['children'] = {}
  return cmd_dict_copy





# Returns the seash command dictionary after making any necessary additions to it

def return_command_dictionary():
  
  # Sets the entire seash command dictionary as 'on target' children except itself
  seashcommanddict['on']['children']['[TARGET]']['children'] = _deep_copy_main_dict(['on'])
  
  # Sets the entire seash command dictionary as 'as keyname' children except itself
  seashcommanddict['as']['children']['[KEYNAME]']['children'] = _deep_copy_main_dict(['as'])

  # Sets the entire seash command dictionary as 'help' children except itself
  seashcommanddict['help']['children'] = _deep_copy_main_dict(['help'])

  return seashcommanddict





##### User input parsing related methods #####

"""
seash's command parser:
The parser receives the string of commands the user inputted and proceeds
to iterate through seashcommanddict to verify that the each of the command
string corresponds to a key of seash's command dictionary, and each subsequent 
string corresponds to a command key of the current command dictionary's 
dictionary of children. 

At the same time, a sub-dictionary of seashcommanddict is being built that holds 
only the chain of dictionaries that corresponds to the user's input, with the only
difference being that any user-inputted argument will replace the command key of the 
command dictionary associated with it. Thus, instead of '[TARGET]', the key to the 
command dictionary would instead be '%1'. 

Targets and Group name arguments will be checked to see if the name specified
actually exists, and general Argument command dictionaries with no children will
have the corresponding user input string and any string that follows be spliced
into a single string with spaces in between each word.

A ParseError will be raised if the argument given for Target or Group does not
exist, and also if the user inputted command word does not correspond to any of the
command keys of the current dictionaries of dictionaries the iterator is looking
at and there are no argument keys to suggest the inputted word is an user argument.
"""
def parse_command(userinput):

  userinput = userinput.strip()

  userstringlist = userinput.split()


  # Dictionary of dictionaries that gets built corresponding to user input
  input_dict = {}
  # Iterator that builds the input_dict
  input_dict_builder = input_dict

  # The iterator that runs through the command dictionary
  seash_dict_mark = return_command_dictionary()


  # Cycles through the user's input string by string
  for user_string in userstringlist:

    # First, an initial check to see if user's input matches a specified command word
    for cmd_pattern in seash_dict_mark.iterkeys():

      if user_string == cmd_pattern or (cmd_pattern in commandvariationdict.keys() and user_string in commandvariationdict[cmd_pattern]):

        # Appends a copy to avoid changing the master list of dictionaries
        input_dict_builder[cmd_pattern] = _shallow_copy(seash_dict_mark[cmd_pattern])

        # Moves the input dictionary builder into the next empty children dictionary
        input_dict_builder = input_dict_builder[cmd_pattern]['children']

        # Iterates into the children dictionary of the next level of command that may follow
        seash_dict_mark = seash_dict_mark[cmd_pattern]['children']

        break


    # If the user's input string does not match the any of the command pattern directly,
    # looks through the command's children for the possibility of being an
    # user inputed argument, generally denoted by starting with a '['
    else:
      for cmd_pattern in seash_dict_mark.iterkeys():

        # Checks if the input is listed as a valid target, and appends
        # the command dictionary to the input_dict
        if cmd_pattern.startswith('['):
          if cmd_pattern == '[TARGET]' or cmd_pattern == '[GROUP]':
            
            # Compares input with current list of targets and/or groups
            # Raise exception if not found in list of targets
            if user_string not in seash_global_variables.targets:
              raise seash_exceptions.ParseError("Target does not exist")
          
          # Necessity of checking existence of keynames yet to be determined
          #elif cmd_pattern == '[KEYNAME]':
          #  pass

          # Necessity of verifying existence of file yet to be determined
          #elif cmd_pattern == '[FILENAME]':
          #  pass
          
          # simply appends to input_dict
          elif cmd_pattern == '[ARGUMENT]':

            # If ARGUMENT doesn't have any children, joins the rest of the user's input
            # into a single string
            if not seash_dict_mark[cmd_pattern]['children']:
              arg_string = " ".join(userstringlist[userstringlist.index(user_string):])
              for string in userstringlist[userstringlist.index(user_string):]:
                userstringlist.remove(string)

              # Resets the user_string as arg_string for consistency in rest of code
              user_string = arg_string
              userstringlist.append(user_string)
  

          # Appends a copy of the dictionary to avoid changing the master list of command dictionaries
          # Also sets the name of the target specified by the user as the key of the command's dictionary
          # for later use by the command's callback
          input_dict_builder[user_string] = _shallow_copy(seash_dict_mark[cmd_pattern])
          
          # Sets itself as the recently-added command dictionary's children to be ready to
          # assign the next command dictionary associated with the next user's input string
          input_dict_builder = input_dict_builder[user_string]['children']
            
          # sets the next list of command dictionaries
          seash_dict_mark = seash_dict_mark[cmd_pattern]['children']

          break



      # If the user input doesn't match any of the pattern words and there's no
      # pattern that suggest it may be a user input argument, raise an exception
      # for going outside of seash's command dictionary
      else:
        raise seash_exceptions.ParseError("Command not understood")



  return input_dict



"""
seash's command dispatcher:
Taking in the input dictionary of dictionaries, input_dict, the dispatcher iterates
through the series of dictionaries and executes the command callback function of
any command dictionaries that has the key 'priority' while keeping reference of the
last callback function of the command dictionary that had one. After completing
the iteration, if the referenced command callback function has not been executed
already from priority status, the dispatcher proceeds to executes the function. 

Each callback function will be passed a copy of the input_dict for access to 
user-inputted arguments and the environment_dict that keeps track of the current 
state of seash.

A DispatchError will be raised if at the end of the iteration there are no valid command
callbacks to be executed.
"""
def command_dispatch(input_dict, environment_dict):
  
  # Iterator through the user command dictionary
  dict_mark = input_dict


  # Sets the command callback method to be executed
  current_callback = None

  
  # Sets the last 'interrupt' command's callback method that was executed.
  # Used to avoid having current_callback execute the same command function again
  interrupt_callback = None


  # First, general check for any command dictionaries with the 'priority' key
  # Execute the callback methods of those commands
  
  while dict_mark.keys():


    # Pulls out the command word, which also serves as the key to the command's dictionary
    # It should be the only key in the key list of the children's dictionary
    command_key = dict_mark.keys()[0]


    # Sets the callback method reference if command's 'callback' isn't set to None
    if dict_mark[command_key]['callback'] is not None:
      current_callback = dict_mark[command_key]['callback']


    # Executes the callback method of all commands that contains the 'priority' key
    if 'priority' in dict_mark[command_key]:
      interrupt_callback = dict_mark[command_key]['callback']
      interrupt_callback(input_dict.copy(), environment_dict)

      # In the case of 'help', breaks out of the dispatch loop to avoid executing any other
      # command's function
      if command_key == 'help':
        break


    # Iterates into the next dictionary of children commands
    dict_mark = dict_mark[command_key]['children']



  # Raises an exception if current_callback is still None
  if current_callback is None:
    raise seash_exceptions.DispatchError("Invalid command. Please check that the command has been inputted correctly.")


  # Executes current_callback's method if it's not the same one as interrupt_callback
  elif not interrupt_callback == current_callback:
    current_callback(input_dict.copy(), environment_dict)
