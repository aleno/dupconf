#!/usr/bin/python

import sys
import subprocess
from optparse import OptionParser
from dirconfig import DirConfiguration

parser = OptionParser(usage='usage: %prog [options] config-dir', version='1.0')
parser.add_option('-v', '--verbose', dest='verbosity', help='verbosity level of duplicity (overrides args file)', type='int')
parser.add_option('-d', '--debug', dest='debug', help='turn on the debugger for the configuration parser', action='store_true', default=False)
parser.add_option('', '--dry-run', dest='dryrun', help='calculate what would be done, but do not perform any action', action='store_true', default=False)
parser.add_option('', '--force', dest='force', help='force duplicity to complete an action (most likely cleanup)', action='store_true', default=False)
parser.add_option('-a', '--action', dest='action', help='action duplicity ought to take', default='incremental', type='choice', choices=['full', 'incremental', 'restore', 'verify', 'collection-status', 'list-current-files', 'cleanup', 'remove-older-than', 'remove-all-but-n-full'])
parser.add_option('-f', '--file-to-restore', dest='restore_path', help='if restore is the action, this can determine which file specifically is restored', type='string')
parser.add_option('-r', '--restore-to', dest='restore_to', help='if restore is the action, this can determine where the restored files are stored', type='string')
parser.add_option('', '--allow-source-mismatch', dest='allow_mismatch', help='if the backup source changed, but you still want to use the same backup destination, and duplicity is complaining, use this', action='store_true', default=False)

(options, args) = parser.parse_args()

if len(args) < 1:
    raise ValueError('Error: only one extra argument required, to indicate the path for the backup configuration directory.')

configuration = DirConfiguration(args[0], True, options.debug).config

up_actions = ['full', 'incremental']
down_actions = ['restore', 'verify']
remote_actions = ['collection-status', 'list-current-files', 'cleanup', 'remove-older-than', 'remove-all-but-n-full']

duplicity_opts = []

if not configuration.has_key('binary'):
    raise ValueError('Error: backup directory has no binary file.')

duplicity_opts.extend(configuration.get('binary'))
duplicity_opts.append(options.action)

if configuration.has_key('args'):
    duplicity_opts.extend(configuration.get('args'))

if options.verbosity:
    duplicity_opts.extend(['-v', str(options.verbosity)])

if options.dryrun:
    duplicity_opts.append('--dry-run')

if options.force:
    duplicity_opts.append('--force')

if options.allow_mismatch:
    duplicity_opts.append('--allow-source-mismatch')

if not configuration.has_key('location'):
    raise ValueError('Error: configuration directory has no location directory.')

elif not configuration.get('location').has_key('local'):
    raise ValueError("Error: configuration's location directory has no local file.")

elif not configuration.get('location').has_key('remote'):
    raise ValueError("Error: configuration's location directory has no remote file.")

local_path = configuration.get('location').get('local')[0]
remote_path = configuration.get('location').get('remote')[0]

if options.action == 'restore':
    if options.restore_to:
        local_path = options.restore_to
    if options.restore_path:
        duplicity_opts.extend(['--file-to-restore', options.restore_path])

if configuration.has_key('inclusion-rules.d') and options.action in up_actions or options.action == 'verify':
    for rule_cat, rules in sorted(configuration['inclusion-rules.d'].items()):
        for rule_type, values in sorted(rules.items()): # excludes always comes before includes
            if rule_type != 'include' and rule_type != 'exclude':
                sys.stderr.write('Warning: in category ' + str(rule_cat) + ', unkown rule type: ' + str(rule_type) + '\n')
                continue

            for value in values:
                if not value.startswith('#') and value.strip() != '':
                    duplicity_opts.extend(['--'+rule_type, value.replace('%%local%%', local_path)])

if options.action in up_actions:
    duplicity_opts.append(local_path)
    duplicity_opts.append(remote_path)
elif options.action in down_actions:
    duplicity_opts.append(remote_path)
    duplicity_opts.append(local_path)
elif options.action in remote_actions:
    duplicity_opts.append(remote_path)
else:
    raise ValueError('Error: incorrect action. This is a bug: it should have been caught before now!')

if configuration.has_key('pre-run.d'):
    for script, script_contents in sorted(configuration['pre-run.d'].items()):
        print 'Calling pre-run script: ' + args[0]+'/pre-run.d/' + script
        return_code = subprocess.call(['sh', args[0]+'/pre-run.d/' + script, local_path, remote_path, options.action])
        if return_code != 0:
            raise Exception('subprocess returned non-zero code ' + str(return_code))

print 'Calling: ' + ' '.join(map(str, duplicity_opts))
return_code = subprocess.call(duplicity_opts)
if (return_code != 0):
    raise Exception('duplicity exited with a non-zero code: ' + str(return_code))

if configuration.has_key('post-run.d'):
    for script, script_contents in sorted(configuration['post-run.d'].items()):
        print 'Calling post-run script: ' + args[0]+'/post-run.d/' + script
        return_code = subprocess.call(['sh', args[0]+'/post-run.d/' + script, local_path, remote_path, options.action])
        if return_code != 0:
            raise Exception('subprocess returned non-zero code ' + str(return_code))

