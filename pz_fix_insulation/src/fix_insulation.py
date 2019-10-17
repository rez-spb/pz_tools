"""
Set insulation for those items that lack the property to 1.0.
Used for build 41.12 as no insulation is implemented yet.
"""

__version__ = '0.0.1'
__author__ = 'rez_spb'
__date__ = '2019-10-17'


import os
import argparse as ap
import logging as log


p = ap.ArgumentParser(description='Set insulation to 1.0 for clothing that '
                                  'lacks insulation.\n'
                                  'For version 41.12.',
                      epilog="v{} ({}) by {}".format(__version__, __date__,
                                                     __author__),
                      formatter_class=ap.RawDescriptionHelpFormatter)
p.add_argument('-d', '--directory', metavar='PATH', required=True,
               help='path to Zomboid installation')
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

clothing_path = 'media/scripts/clothing'


def file2obj(path):
    """
    Read file from path and return dictionary object.

    :param path: full path to file
    :return module: dictionary object that describes the module
    """
    with open(path) as f:
        file = f.read()
        modules = file.split('module ')[1:]
        module_dict = {}
        for module in modules:
            items = module.split('item ')[1:]
            item_dict = {}
            for item in items:
                item_name, properties = item.split('{')  # remove first {
                item_name = item_name.strip()
                properties = properties.split(',')[:-1]  # remove last }
                props_dict = {}
                for prop in properties:
                    pair = prop.strip()
                    try:
                        k, v = pair.split('=')
                    except ValueError as e:
                        log.debug('BUG in', repr(pair))
                        # hello there devs, you finished it with ; instead of ,
                        bug_pairs = pair.split(';\n')
                        for bp in bug_pairs:
                            try:
                                k, v = bp.split('=')
                            except:
                                log.debug('skipping')
                            else:
                                log.debug('bug fixed')
                                props_dict[k.strip()] = v.strip()
                    else:
                        props_dict[k.strip()] = v.strip()
                item_dict[item_name] = props_dict
            module_dict['Base'] = item_dict
    return module_dict


def obj2file(module, file):
    """
    Write module dictionary to file.

    :param module: dictionary object that describes the module
    :param file: full path to file
    """
    with open(file, 'w') as f:
        log.info('Writing {}'.format(file))
        for module_name, module_values in module.items():
            f.write('module {}\n{{\n'.format(module_name))
            for item_name, item_values in module_values.items():
                f.write('\titem {}\n\t{{\n'.format(item_name))
                for prop_name, prop_value in item_values.items():
                    line = '\t\t{} = {},\n'.format(prop_name, prop_value)
                    f.write(line)
                f.write('\t}\n')
            f.write('}\n')


with os.scandir(os.path.join(args.directory, clothing_path)) as cd:
    for file in cd:
        needs_fix = False
        if file.is_dir():
            log.debug('{} is is a directory, skipping'.format(file.name))
        else:
            full_path = os.path.normpath(file.path)
            module = file2obj(full_path)
            for m in module.values():
                for i, items in m.items():
                    if 'Insulation' in items.keys():
                        log.debug('{} has insulation'.format(i))
                    else:
                        needs_fix = True
                        # no insulation, adding 1.0
                        module['Base'][i]['Insulation'] = '1.0'
            if needs_fix is True:
                obj2file(module, full_path)
            else:
                log.info('All items in {} already have insulation'.format(
                    file.name))
