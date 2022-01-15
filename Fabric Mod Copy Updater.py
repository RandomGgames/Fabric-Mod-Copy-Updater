import os
import shutil
import configparser
from zipfile import ZipFile
import json
from datetime import datetime


#FUNCTIONS
def log(text, write_timestamp = True):
	with open("fabric mod copy updater log.txt", "a", encoding="UTF-8") as file:
		if write_timestamp:
			file.write(f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} - {text}\n")
		else:
			file.write(f"{text}\n")

log("Running mods cleanup...")

#READ 'MOD UPDATER.INI' CONFIG
print("Reading 'mod updater.ini' config... ", end = "")
config = configparser.ConfigParser()
if os.path.isfile("mod updater.ini"):
	config.read("mod updater.ini")
else:
	config['1.18.1'] = {"Directories": [], "disable_instead_of_delete": False}
	with open("mod updater.ini", "w") as configfile:
		config.write(configfile)
print("Done")


#SORT OUT DIRECTORIES INTO DICTIONARY
print("Caching directories into dictionary... ", end = "")
directories = {}  # {version: [directories]}
for version in config.sections():
	directories[version] = []
	for dir in eval(config[version]['directories']):
		directories[version].append(dir)
print("Done")

#print(f"{directories = }")
log(f"Directories: {directories}", False)


#CACHE ALL MODS
print("Caching mods into dictionary... ", end = "")
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
								"tmodified": os.path.getmtime(f"{dir}/{mod}")
							})
			except Exception as e:
				print(f"ERR: Something went wrong trying to load the data for {dir}/{mod}. {e}")
				log(f"ERR: Something went wrong trying to load the data for {dir}/{mod}. {e}", False)
print("Done")

#print(f"{cached_mods = }")
log(f"Cached mods: {cached_mods}", False)


#CREATE LIST OF MOST RECENTLY MODIFIED MODS AND OUTDATED MODS
print("Creating list of most recently updated mods... ", end = "")
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
print("Done")

#print(f"{most_uptodate_mods = }")
#print(f"{outdated_mods = }")
log(f"Most recently modified mods: {most_uptodate_mods}", False)
log(f"Outdated mods: {outdated_mods}", False)


#CREATE 'DISABLED' FOLDERS
created_disabled_folder_locations = []
for version in outdated_mods:
	if config[version]['disable_instead_of_delete'].lower == "true":
		print(f"Creating 'DISABLED' folders for {version} mods... ", end = "")
		for outdated_mod in outdated_mods[version]:
			if not os.path.exists(f"{outdated_mod['dir']}/DISABLED"):
				try:
					os.makedirs(f"{outdated_mod['dir']}/DISABLED")
					created_disabled_folder_locations.append(f"{outdated_mod['dir']}/DISABLED")
				except Exception as e:
					print(f"ERR: Something went wrong trying to create DISABLED folder for directory {outdated_mod['dir']}/DISABLED. {e}")
					log(f"ERR: Something went wrong trying to create DISABLED folder for directory {outdated_mod['dir']}/DISABLED. {e}", False)
		print("Done")
		log(f"Created disabled folder locations: {created_disabled_folder_locations}", False)


#MOVE/DELETE OLD MODS INTO THEIR RESPECTIVE DISABLED FOLDERS
for version in outdated_mods:
	if config[version]['disable_instead_of_delete'].lower() == "false": # Delete
		print(f"Deleting {version}'s mods... ", end = "")
		for mod in outdated_mods[version]:
			try:
				os.remove(mod['location'])
			except Exception as e:
				print(f"ERR: Something went wrong trying to delete file in location {mod['location']}. {e}")
				log(f"ERR: Something went wrong trying to delete file in location {mod['location']}. {e}", False)
		print("Done")
	else: # Disable
		print(f"Disabling {version}'s mods... ", end = "")
		for mod in outdated_mods[version]:
			try:
				shutil.move(mod['location'], f"{mod['dir']}/DISABLED")
			except Exception as e:
				print(f"ERR: Something went wrong trying to move file in location {mod['location']}/DISABLED. {e}")
				log(f"ERR: Something went wrong trying to move file in location {mod['location']}/DISABLED. {e}", False)
		print("Done")


#COPYING MOST RECENTLY UPDATED MODS INTO WHERE OUTDATED MODS WERE
print("Updating mods... ", end = "")
for version in outdated_mods:
	for mod in outdated_mods[version]:
		if not mod['dir'] == most_uptodate_mods[version][mod['id']]['dir']:
			shutil.copy(most_uptodate_mods[version][mod['id']]['location'], f"{mod['dir']}")
print("Done")


log("Done\n")
