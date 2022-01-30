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
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Running mods cleanup...")


"""READ 'MOD UPDATER.INI' CONFIG"""
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - INFO: READING CONFIG FILE...")
config = configparser.ConfigParser()
# If the config file exists already, read it
if os.path.isfile("mod updater.ini"):
	config.read("mod updater.ini")
# If the config file doesn't exist, set it up with these default settings
else:
	config['1.18 Mods'] = {
		"updated_mods_directory": '',
		"mods_to_update_directories": ''
	}
	with open("mod updater.ini", "w") as configfile:
		config.write(configfile)


"""BUILD MOST UP TO DATE MOD CACHE"""
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - INFO: BUILDING MOST UP TO DATE MOD CACHE...")
most_updated_mods_cache = {}
try:
	for version in config.sections():
		most_updated_mods_cache[version] = {}
		for mod_to_cache in [mod for mod in os.listdir(config[version]['updated_mods_directory']) if mod.endswith(".jar")]:
			path = Path(f"{config[version]['updated_mods_directory']}\\{mod_to_cache}")
			modzip = ZipFile(path, "r")
			modinfo = modzip.open("fabric.mod.json", "r")
			info_json = json.load(modinfo, strict=False)
			mod_ID = info_json["id"]
			modinfo.close()
			modzip.close()

			if mod_ID in most_updated_mods_cache[version]: # If the mod is already in the mod cache
				# Remove the mod since there are two different versions
				most_updated_mods_cache[version].pop(mod_ID)
				log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: Duplicate mod '{mod_ID}' found in most updated mods directory '{path}'. Delete one!")
			else: # The mod is not already in the cache
				# Add it to the cache
				most_updated_mods_cache[version][mod_ID] = {
					"id": mod_ID,
					"path": str(path)
				}
except Exception as e:
	log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: {e}")
#print(f"{most_updated_mods_cache = }")


"""UPDATING MODS"""
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - INFO: UPDATING MODS...", print_to_console = False)
count_mods_updated = 0
try:
	for version in config.sections():
		for directory in config[version]['mods_to_update_directories'].split(', '):
			log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Updating mods in {directory}")
			for mod in [mod for mod in os.listdir(directory) if mod.endswith(".jar")]:
				path = Path(f"{directory}\\{mod}")
				modzip = ZipFile(path, "r")
				modinfo = modzip.open("fabric.mod.json", "r")
				info_json = json.load(modinfo, strict=False)
				mod_ID = info_json["id"]
				modinfo.close()
				modzip.close()

				if mod_ID in most_updated_mods_cache[version]:
					# If files are named the same, assume version is same already even though tmodified is different
					if mod != os.path.basename(most_updated_mods_cache[version][mod_ID]['path']):
						# Remove outdated mod
						os.remove(str(path))
						# Replace with more up to date version
						shutil.copy2(most_updated_mods_cache[version][mod_ID]['path'], path.parent)
						count_mods_updated += 1
						log(f"INFO: Updated '{str(path)}'", print_to_console = False)
				else:
					log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: Mod '{path}' does not have a copy within most up to date mods directory. It will be ignored.")
except Exception as e:
	log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - WARN: {e}")


log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Updated {count_mods_updated} mod(s)")
log(f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S:%f')}] - Done\n", print_to_console = False)
