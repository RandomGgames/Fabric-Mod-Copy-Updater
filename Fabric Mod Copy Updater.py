import os
import shutil
import configparser
from zipfile import ZipFile
import json
from datetime import datetime
from pathlib import Path


def log(text, print_to_console: bool = True, print_to_log: bool = True):
	"""Prints a message to console and send it to the log file"""
	if print_to_console:
		print(text)
	if print_to_log:
		log_file = open("fabric mod copy updater.log", "a", encoding="UTF-8")
		log_file.write(f"{text}\n")
	return


"""LOG START TIME"""
###log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Running mods cleanup...")


"""READ 'MOD UPDATER.INI' CONFIG"""
###log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - INFO: READING CONFIG FILE...")
config = configparser.ConfigParser()
# If the config file exists already, read it
if os.path.isfile("mod updater.ini"):
	config.read("mod updater.ini")
# If the config file doesn't exist, set it up with these default settings
else:
	config['1.18 Mods'] = {
		"updated_mods_directory": '',
		"directories_to_keep_updated": ''
	}
	with open("mod updater.ini", "w") as configfile:
		config.write(configfile)


"""BUILD MOST UP TO DATE MOD CACHE"""
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - INFO: BUILDING MOST UP TO DATE MOD CACHE...", print_to_log = False)
most_updated_mods = {}
try:
	for section in config.sections():
		most_updated_mods[section] = {}
		most_updated_mods_directory = Path(config.get(section, "updated_mods_directory"))
		for mod in [file for file in os.listdir(str(most_updated_mods_directory)) if file.endswith(".jar")]:
			path = Path(f"{str(most_updated_mods_directory)}\\{mod}")
			tmodified = os.path.getmtime(str(path))
			with ZipFile(path, "r") as modzip:
				with modzip.open("fabric.mod.json", "r") as modinfo:
					mod_id = json.load(modinfo, strict=False)["id"]
				modinfo.close()
			modzip.close()
			
			if mod_id not in most_updated_mods[section]:
				most_updated_mods[section][mod_id] = {
					"id": mod_id,
					"path": str(path),
					"tmodified": tmodified
				}
			else:
				# If currently cached mod is older, replace with the new looped one.
				current_tmodified = most_updated_mods[section][mod_id]['tmodified']
				if current_tmodified < tmodified: #If the file cached is older
					log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: Outdated mod: {mod_id}, '{os.path.basename(most_updated_mods[section][mod_id]['path'])}'.")
					most_updated_mods[section][mod_id] = {
						"id": mod_id,
						"path": str(path),
						"tmodified": tmodified
					}
				else: #Current looped mod is outdated
					log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: Outdated mod: {mod_id}, '{os.path.basename(path)}'.")


except Exception as e:
	log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: {e}")
#print(f"{most_updated_mods = }")


"""UPDATING MODS"""
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - INFO: UPDATING MODS...", print_to_log = False)
count_mods_updated = 0
try:
	for section in config.sections():
		directories_to_keep_updated = config[section]['directories_to_keep_updated'].split(', ')
		for i, directory in enumerate(directories_to_keep_updated):
			directories_to_keep_updated[i] = Path(directory)
		for directory in directories_to_keep_updated:
			log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Updating mods in {directory}")
			for mod in [mod for mod in os.listdir(directory) if mod.endswith(".jar")]:
				path = Path(f"{str(directory)}\\{mod}")
				tmodified = os.path.getmtime(str(path))
				with ZipFile(path, "r") as modzip:
					with modzip.open("fabric.mod.json", "r") as modinfo:
						mod_id = json.load(modinfo, strict=False)["id"]
					modinfo.close()
				modzip.close()

				if mod_id in most_updated_mods[section]:
					# If files are named the same, assume version is same already even though tmodified is different
					if mod != os.path.basename(most_updated_mods[section][mod_id]['path']):
						# Remove outdated mod
						os.remove(str(path))
						# Replace with more up to date version
						shutil.copy2(most_updated_mods[section][mod_id]['path'], path.parent)
						count_mods_updated += 1
						log(f"INFO: Replaced '{str(path.name)}' with '{Path(most_updated_mods[section][mod_id]['path']).name}'")
				else:
					log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: Mod '{path}' does not have a copy within most up to date mods directory. It will be ignored.")
except Exception as e:
	log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: {e}")


log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Updated {count_mods_updated} mod(s)")
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Done\n")
