import os
import shutil
import configparser
from zipfile import ZipFile
import json
from datetime import datetime


def log(text, print_to_console: bool = True, print_to_log: bool = True):
	"""Prints a message to console and send it to the log file"""
	if print_to_console:
		print(text)
	if print_to_log:
		log_file = open("fabric mod copy updater.log", "a", encoding="UTF-8")
		log_file.write(f"{text}\n")
	return


"""LOG START TIME"""
start_time = datetime.now()
log(f"{start_time.strftime('%m/%d/%Y, %H:%M:%S')} - Running mods cleanup...", print_to_console = False)


"""READ 'MOD UPDATER.INI' CONFIG"""
log("INFO: READING CONFIG FILE...")
config = configparser.ConfigParser()
# If the config file exists already, read it
if os.path.isfile("mod updater.ini"):
	config.read("mod updater.ini")
# If the config file doesn't exist, set it up with these default settings
else:
	config['1.18 Mods'] = {
		"updated_mods_directory": '"./1.18 Mods"',
		"mods_to_update_directories": list()
	}
	with open("mod updater.ini", "w") as configfile:
		config.write(configfile)


"""BUILD MOST UP TO DATE MOD CACHE"""
log("INFO: BUILDING MOST UP TO DATE MOD CACHE...")
most_updated_mods_cache = {}
for version in config.sections():
	most_updated_mods_cache[version] = {}
	try:
		for mod_to_cache in [mod for mod in os.listdir(config[version]['updated_mods_directory']) if mod.endswith(".jar")]:
			try:
				path = f"{config[version]['updated_mods_directory']}\\{mod_to_cache}"

				with ZipFile(path, "r") as modzip:
					with modzip.open("fabric.mod.json", "r") as modinfo:
						info_json = json.load(modinfo, strict=False)
						mod_ID = info_json["id"]
						
						if mod_ID in most_updated_mods_cache[version]: # If the mod is already in the mod cache
							# Remove the mod since there are two different versions
							most_updated_mods_cache[version].pop(mod_ID)
							log(f"WARN: Duplicate mod '{mod_ID}' found in most updated mods directory '{path}'. Delete one!")
						else: # The mod is not already in the cache
							# Add it to the cache
							most_updated_mods_cache[version][mod_ID] = {
								"id": mod_ID,
								"path": path
							}

			except Exception as e:
				log(f"WARN: Error while caching most up to date mod '{mod_to_cache}'. {e}")

	except Exception as e:
		log(f"WARN: Unable to access most up to date mods directory '{config[version]['updated_mods_directory']} for'. {e}")
#print(f"{most_updated_mods_cache = }")


log("INFO: UPDATING MODS...")
count_mods_updated = 0
for version in config.sections():
	for directory in config[version]['mods_to_update_directories'].split(', '):
		try:
			for mod in [mod for mod in os.listdir(directory) if mod.endswith(".jar")]:
				try:
					path = f"{directory}\\{mod}"

					with ZipFile(path, "r") as modzip:
						with modzip.open("fabric.mod.json", "r") as modinfo:
							info_json = json.load(modinfo, strict=False)
							mod_ID = info_json["id"]

						if mod_ID in most_updated_mods_cache[version]:
							# If files are named the same, assume version is same already even though tmodified is different
							if mod != os.path.basename(most_updated_mods_cache[version][mod_ID]['path']):
								# Remove outdated mod
								os.remove(path)
								# Replace with more up to date version
								shutil.copy2(most_updated_mods_cache[version][mod_ID]['path'], path)
								count_mods_updated += 1
								log(f"INFO: Updated '{path}'", print_to_console = False)
						else:
							log(f"WARN: Mod '{mod}' located at '{path}' does not have a copy within most up to date mods directory. It will be ignored.")

				except Exception as e:
					log(f"WARN: Error while processing '{directory}/{mod}'. {e}")

		except Exception as e:
			log(
				f"WARN: Unable to access mods to update directory '{directory}'")
log(f"Updated {count_mods_updated} mod(s)")

log(f"Done. ({(datetime.now() - start_time).total_seconds()}s)\n", print_to_console = False)
log(f"Done.", print_to_log = False)
