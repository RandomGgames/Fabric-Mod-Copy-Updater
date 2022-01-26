import os
import shutil
import configparser
from zipfile import ZipFile
import json
from datetime import datetime

log_file = open("fabric mod copy updater log.txt", "a", encoding="UTF-8")
log_file.write(f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} - Running mods cleanup...\n")

#READ 'MOD UPDATER.INI' CONFIG
print("Reading 'mod updater.ini' config...")
config = configparser.ConfigParser()
if os.path.isfile("mod updater.ini"):
	config.read("mod updater.ini")
else:
	config['1.18.1'] = {"Directories": [], "disable_instead_of_delete": False}
	with open("mod updater.ini", "w") as configfile:
		config.write(configfile)
print("Done")


#SORT OUT DIRECTORIES INTO DICTIONARY
print("Caching directories into dictionary...")
directories = {}  # {version: [directories]}
for version in config.sections():
	directories[version] = []
	for dir in config[version]['directories'].replace('[', '').replace(']', '').replace('"', '').replace("'", "").replace('\\', '/').split(', '):
		directories[version].append(dir)
print(f"{directories = }")
print("Done")


#CACHE ALL MODS
print("Caching mods into dictionary...")
cached_mods = {} # {"version#": [{id, dir, file, location, tmodified}]}
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
								"file": mod,
								"location": f"{dir}/{mod}",
								"tmodified": os.path.getctime(f"{dir}/{mod}")
							})
			except Exception as e:
				print(f"ERR: Something went wrong trying to load the data for {dir}/{mod}. {e}")
print(f"{cached_mods = }")
print("Done")


#CREATE LIST OF MOST RECENTLY MODIFIED MODS AND OUTDATED MODS
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
				if not most_uptodate_mods[version][cached_mod['id']]['file'] == cached_mod['file']:
					outdated_mods[version].append(cached_mod)
			else:
				if not most_uptodate_mods[version][cached_mod['id']]['file'] == cached_mod['file']:
					outdated_mods[version].append(most_uptodate_mods[version][cached_mod['id']])
				most_uptodate_mods[version][cached_mod['id']] = cached_mod
print(f"{most_uptodate_mods = }")
print(f"{outdated_mods = }")
print("Done")


#CREATE 'DISABLED' FOLDERS
created_disabled_folder_locations = []
for version in outdated_mods:
	if config[version]['disable_instead_of_delete'].lower == "true":
		print(f"Creating 'DISABLED' folders...")
		for outdated_mod in outdated_mods[version]:
			if not os.path.exists(f"{outdated_mod['dir']}/DISABLED"):
				try:
					os.makedirs(f"{outdated_mod['dir']}/DISABLED")
					created_disabled_folder_locations.append(f"{outdated_mod['dir']}/DISABLED")
				except Exception as e:
					print(f"ERR: Something went wrong trying to create DISABLED folder into directory {outdated_mod['dir']}. {e}")
		print("Done")


#MOVE/DELETE OLD MODS INTO THEIR RESPECTIVE DISABLED FOLDERS
for version in outdated_mods:
	if config[version]['disable_instead_of_delete'].lower() == "false": # Delete
		print(f"Deleting outdated mods for section {version}...")
		for mod in outdated_mods[version]:
			try:
				os.remove(mod['location'])
				print(f"Deleted outdated mod {mod['location']}")
				log_file.write(f"Deleted outdated mod {mod['location']}\n")
			except Exception as e:
				print(f"ERR: Something went wrong trying to delete {mod['location']}. {e}")
		print("Done")
	else: # Disable
		print(f"Disabling outdated mods for section {version}...")
		for mod in outdated_mods[version]:
			try:
				shutil.move(mod['location'], f"{mod['dir']}/DISABLED")
				print(f"Moved outdated mod {mod['location']} into {mod['dir']}/DISABLED")
				log_file.write(f"Moved outdated mod {mod['location']} into {mod['dir']}/DISABLED\n")
			except Exception as e:
				print(f"ERR: Something went wrong trying to move {mod['location']} into {mod['location']}/DISABLED. {e}")
		print("Done")


#COPYING MOST RECENTLY UPDATED MODS INTO WHERE OUTDATED MODS WERE
print("Updating mods...")
for version in outdated_mods:
	for mod in outdated_mods[version]:
		if not mod['dir'] == most_uptodate_mods[version][mod['id']]['dir']:
			try:
				shutil.copy2(most_uptodate_mods[version][mod['id']]['location'], mod['location'])
				print(f"Copied {most_uptodate_mods[version][mod['id']]['location']} into {mod['dir']}")
				log_file.write(f"Copied {most_uptodate_mods[version][mod['id']]['location']} into {mod['dir']}\n")
			except Exception as e:
				print(f"ERR: Something went wrong copying {most_uptodate_mods[version][mod['id']]['location']} to {mod['location']}. {e}")
print("Done")


log_file.write(f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} - Done\n\n")
input("Press any key to exit.")
