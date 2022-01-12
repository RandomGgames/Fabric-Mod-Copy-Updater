# Fabric Mod Copy Updater
A python script which copies mods between folders depending on the most recently modified/downloaded to help keep mods in multiple folders up to date


# Config Default
This python script will auto-generate a 'mod updater.ini' file which by default contains:

```ini
[1.18.1]
directories = []
disable_instead_of_delete = False
```

```[1.18.1]``` - This is the name of a section, mainly used to seperate mod versions, though can be named anything at your convience.

```directories``` - A list of directories (mod folders) containing fabric mods to search through and automatically attempt to copy most recent versions of mods into/out of.

```disable_instead_of_delete``` - booleen option for creating a folder in the mods folders in directories and moving outdated mods into it instead of deleting them into the system's recyling bin.


# Config Example:
```ini
[1.18.1]
directories = [".../.minecraft/1.18/mods", ".../.minecraft/1.18 Modded/mods", ".../fabric servers/1.18/Server 1/mods", ".../fabric servers/1.18/Server 2/mods"]
disable_instead_of_delete = True
```
