#pip install Send2Trash

import sys
import os
import shutil
import configparser
from zipfile import ZipFile
from send2trash import send2trash
import json


"""
READ 'MOD UPDATER.INI' CONFIG
"""
print("Reading 'mod updater.ini' config...")
config = configparser.ConfigParser()
if os.path.isfile("mod updater.ini"):
	config.read("mod updater.ini")
else:
	config['1.18.1'] = {"Directories": [], "disable_instead_of_delete": False}
	with open("mod updater.ini", "w") as configfile:
		config.write(configfile)


"""
SORT OUT DIRECTORIES INTO DICTIONARY
"""
print("Caching directories into dictionary...")
directories = {}  # {version: [directories]}
for version in config.sections():
	directories[version] = []
	for dir in eval(config[version]['directories']):
		directories[version].append(dir)

#print(f"{directories = }")


"""
CACHE ALL MODS
"""
print("Caching mods into dictionary...")
cached_mods = {} # {"version#": [{"id": "mod_id...", "location": "file_location...", "tmodified": "last modified time..."}]}
for version in directories:
	cached_mods[version] = []
	for dir in directories[version]:
		mods = [mod for mod in os.listdir(dir) if mod.endswith(".jar")]
		for mod in mods:
			try:
				with ZipFile(f"{dir}/{mod}", "r") as zip:
					with zip.open("fabric.mod.json", "r") as modinfo:
						info_json = json.load(modinfo, strict=False)
						cached_mods[version].append(
							{
								"id": info_json['id'],
								"dir": dir,
								"location": f"{dir}/{mod}",
								"tmodified": os.path.getmtime(f"{dir}/{mod}"),
							})
			except Exception as e:
				print(f"Something went wrong trying to load the data for {dir}/{mod}. {e}")

#print(f"{cached_mods = }")


"""
CREATE LIST OF MOST RECENTLY MODIFIED MODS AND OUTDATED MODS
"""
print("Creating list of most recently updated mods...")
most_uptodate_mods = {}  # {"version#": {id: {id, location, tmodified}}}
outdated_mods = {}  # {"version#": [{id, location, tmodified}]}
for version in cached_mods:
	most_uptodate_mods[version] = {}
	outdated_mods[version] = []
	for cached_mod in cached_mods[version]:
		if cached_mod['id'] not in most_uptodate_mods[version]:
			most_uptodate_mods[version][cached_mod['id']] = cached_mod
		else:
			if most_uptodate_mods[version][cached_mod['id']]['tmodified'] > cached_mod['tmodified']:
				outdated_mods[version].append(cached_mod)
			else:
				outdated_mods[version].append(
					most_uptodate_mods[version][cached_mod['id']])
				most_uptodate_mods[version][cached_mod['id']] = cached_mod

#print(f"{most_uptodate_mods = }")
#print(f"{outdated_mods = }")


"""
CREATE 'DISABLED' FOLDERS
"""
created_disabled_folder_locations = []
for version in outdated_mods:
	if config[version]['disable_instead_of_delete'].lower == "true":
		print(f"Creating 'DISABLED' folders for {version} mods...")
		for outdated_mod in outdated_mods[version]:
			if not os.path.exists(f"{outdated_mod['dir']}/DISABLED"):
				try:
					os.makedirs(f"{outdated_mod['dir']}/DISABLED")
					created_disabled_folder_locations.append(
						f"{outdated_mod['dir']}/DISABLED")
				except Exception as e:
					print(f"Something went wrong trying to create DISABLED folder for directory {outdated_mod['dir']}/DISABLED. {e}")

"""
MOVE/DELETE OLD MODS INTO THEIR RESPECTIVE DISABLED FOLDERS
"""
for version in outdated_mods:
	if config[version]['disable_instead_of_delete'].lower() == "false": # Delete
		print(f"Deleting {version}'s mods...")
		for mod in outdated_mods[version]:
			#os.remove(mod['location'])
			send2trash(mod['location'])
	else: # Disable
		print(f"Disabling {version}'s mods...")
		for mod in outdated_mods[version]:
			shutil.move(mod['location'], f"{mod['dir']}/DISABLED")


"""
COPYING MOST RECENTLY UPDATED MODS INTO WHERE OUTDATED MODS WERE
"""
print("Updating mods...")
for version in outdated_mods:
	for mod in outdated_mods[version]:
		if not mod['dir'] == most_uptodate_mods[version][mod['id']]['dir']:
			shutil.copy(most_uptodate_mods[version][mod['id']]['location'], f"{mod['dir']}")
