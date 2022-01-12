# Fabric Mod Copy Updater

## What does it do?
#### Short version:
This is a python script that copies an updated mod into other folders where older versions are located. 
#### Long version:
What this script does is, when you download a new version of a mod manually and run the script, the script will search though all the configured folders, than for every mod you have downloaded, select the most recently modified one, than copy it into any location that same mod id is located, affectively allowing you to download a mod update in one place and automatically copy it into other folders the mod is also already located. 

## Requirements
 - Python3. Written using v3.9.6, but I'm guessing any python3 will work...? Could be wrong though.
 - Python library Send2Trash. ```pip install Send2Trash```. Tested using version 1.8.0, but any should work I assume.

## Planned updates/fixes
(Sorted by highest priority at the top)
- [ ] Fix issue where up to date mods of the same version are being deleted/disabled and re-copied due to different file modified times
- [ ] Add log file
- [ ] Make it forge mod compatable too (MAYBE, no promises)
