"""Remove old files from Project Zomboid multiplayer saves to cut sizes.

Script helps to clean older chunks which are mostly remote and prone to change
on the server, so not much point in storing them locally. However it preserves
chunks for last X days you specify regardless of how remote they are from your
character.

Script won't ever delete 'map_p.bin'.
"""

__version__ = '0.1.0'
__author__ = 'rez_spb'
__date__ = '2019-10-09'


import os
import socket
import datetime
import argparse as ap
import logging as log
from pathlib import Path


p = ap.ArgumentParser(description='Remove files older than X days from Project'
                                  ' Zomboid multiplayer saves directory\n'
                                  'with map_p.bin being an exception.\n'
                                  'Local server directories are not affected.',
                      epilog="v{} ({}) by {}".format(__version__, __date__,
                                                     __author__),
                      formatter_class=ap.RawDescriptionHelpFormatter)
p.add_argument('-d', '--days', type=int, metavar='INT', required=True,
               help='days to preserve in save (1 or more)')
p.add_argument('-f', '--faster', action='store_true', default=False,
               help='do not count freed size to speed things up')
p.add_argument('--dry-run', action='store_true', default=False,
               help='do not perform actual removal, just count files')
# either verbose or quiet, can be default
g1 = p.add_mutually_exclusive_group(required=False)
g1.add_argument('-v', '--verbose', action='store_true', default=False,
                help='verbose output')
g1.add_argument('-q', '--quiet', action='store_true', default=False,
                help='display warnings and errors only')
args, _ = p.parse_known_args()

# check passed verbosity against default value
if args.verbose:
    log_level = 'DEBUG'
elif args.quiet:
    log_level = 'WARNING'
else:
    log_level = 'INFO'
log_format = '%(asctime)s %(levelname)s %(message)s'

# override long names with short ones
for level, letter in zip((10, 20, 30, 40, 50), 'DIWEC'):
    log.addLevelName(level, letter)
log.basicConfig(format=log_format, level=log_level)
log.debug('Log level set to {lvl}'.format(lvl=log_level))
if args.dry_run:
    log.warning("--dry_run flag enabled, files won't be removed")


days_to_preserve = args.days
saves_dir = os.path.normpath(os.path.join(str(Path.home()),
                                          'Zomboid/Saves/Multiplayer'))


def remove(save_directory, file_list, faster=False, dry_run=False):
    """Remove files from a directory, count and return freed size in bytes.

    :param save_directory: directory with data
    :param file_list: list of filenames to remove
    :param faster: flag to skip additional stat for each file
    :param dry_run: flag to disable file removal
    :return bytes_freed: number of bytes bytes_freed
    """

    bytes_freed = 0
    for i, f in enumerate(file_list):
        if f == 'map_p.bin':
            log.warning("Won't remove 'map_p.bin'!")
            continue
        else:
            path = os.path.normpath(os.path.join(save_directory, f))
            if faster is not True:
                bytes_freed += os.stat(path).st_size
            if dry_run is not True:
                try:
                    os.remove(path)
                except OSError as e:
                    log.error('Could not remove file: {}'.format(path))
                    log.debug('Exception encountered: {}'.format(e))
                else:
                    log.debug("- {}".format(path))
    return bytes_freed


def valid_ip(address):
    """Check whether passed address is a valid IP.

    Solution by Maria Zverina (using 'socket' library)
      (https://stackoverflow.com/users/655183/maria-zverina)

    :param address: passed string to check
    :return: False if invalid IPv4, True otherwise
    """

    try:
        socket.inet_aton(address)
    except OSError:
        return False
    else:
        return True


if days_to_preserve < 1:
    log.warning("Not safe to preserve less than 1 day, forcing 1 day")
    days_to_preserve = 1


with os.scandir(saves_dir) as sd:
    for directory in sd:
        save_ip = directory.name.split(sep='_')[0]
        if valid_ip(save_ip):
            # this is a save directory
            log.info("Processing: {}".format(directory.name))
            if directory.is_dir():
                # now get all files inside with last modified time
                files = {}
                freshest_max = 0
                with os.scandir(directory) as sf:
                    for file in sf:
                        modified_time = file.stat().st_mtime
                        files[file.name] = modified_time
                        if modified_time > freshest_max:
                            freshest_max = modified_time
                # convert freshest to datetime
                freshest = datetime.datetime.fromtimestamp(freshest_max)

                remove_files = []
                for file_name, file_time in files.items():
                    modified_time = datetime.datetime.fromtimestamp(file_time)
                    delta = datetime.timedelta(days=days_to_preserve)
                    if freshest > modified_time + delta:
                        remove_files.append(file_name)

                if len(remove_files) > 0:
                    log.info("Removing {} / {} files".format(len(remove_files),
                                                             len(files)))
                    freed = remove(directory.path, remove_files,
                                   args.faster, args.dry_run)
                    if freed > 0:
                        log.info("Freed {:.2f} Mb".format(freed / 1024 / 1024))
                else:
                    log.debug("No files to remove")
        else:
            # server files, skip processing
            log.warning("Skipping: {}".format(directory.name))
            continue
