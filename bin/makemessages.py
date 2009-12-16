#!/usr/bin/python -W ignore::DeprecationWarning

import re, os, sys
from tornado.options import define, options, parse_command_line
import logging

# reference: django.core.management.commands.makemessages
def make_messages(locale, basedir, srcdirs, outdir, extensions, verbose=False):
    (_stdin, stdout, stderr) = os.popen3('xgettext --version', 't')
    match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', stdout.read())
    
    if match:
        extensions = ['.html', '.py', '.pypo'] if not extensions else extensions
        
        outdir = os.path.join(basedir, outdir)
        pofile = os.path.join(outdir, '%s.po' % locale)
        potfile = os.path.join(outdir, '%s.pot' % locale)

        if os.path.exists(potfile):
            os.unlink(potfile)

        all_files = []
        for srcdir in srcdirs:
            srcdir = os.path.join(basedir, srcdir)
            logging.info(srcdir + " ...")
            for (dirpath, _dirnames, filenames) in os.walk(srcdir):
                all_files.extend([(dirpath, f) for f in filenames])
        all_files.sort()
        
        logging.info("Updating translation string...\n")
        for dirpath, file in all_files:
            _file_base, file_ext = os.path.splitext(file)
            
            if file_ext in extensions:
                cmd = 'xgettext  -L Python -F  -w=20 --omit-header --from-code UTF-8 --debug -o - "%s"' %  os.path.join(dirpath, file)
                if verbose:
                    logging.info('processing %s\n' % os.path.join(dirpath, file))

                (_stdin, stdout, stderr) = os.popen3(cmd, 't')
                msgs = stdout.read()
                errors = stderr.read()
                if errors: pass
                if msgs:
                    open(potfile, 'ab').write(msgs)

        if os.path.exists(potfile):
            (_stdin, stdout, stderr) = os.popen3('msguniq --to-code=utf-8 "%s"' % potfile, 't')
            msgs = stdout.read()
            errors = stderr.read()
            if errors:
                raise Exception("Errors happened while running msguniq\n%s" % errors)
            open(potfile, 'w').write(msgs)
            if os.path.exists(pofile):
                (_stdin, stdout, stderr) = os.popen3('msgmerge -q "%s" "%s"' % (pofile, potfile), 't')
                msgs = stdout.read()
                errors = stderr.read()
                if errors:
                    raise Exception("Errors happened while running msgmerge\n%s" % errors)
            open(pofile, 'wb').write(msgs)
            convert_to_csv(pofile)
            os.unlink(potfile)
    else:
        raise Exception("You need to install xgettext")

def po_to_csv(pofile):
    """ Convert .po to .csv format requied by Tornado"""
    
    lines = open(pofile).readlines()
    clines, msgid, in_msg = [], [], False
    
    logging.info("Converting .po to .csv...\n")
    for line in lines:
        if line.startswith("#: "):
            continue
        elif line.startswith("msgid "):
            line = re.sub("^msgid ","", line)
            msgid.append(line.strip())
            in_msg = True
        elif line.startswith("msgstr"):
            line = re.sub("^msgstr ","", line).strip()
            if line.strip('"'):
                msgid = '"%s"' % "".join([m.strip('"') for m in msgid])
                clines.append(msgid + "," + line + "\n")
            msgid, in_msg = [], False
        else:
            if in_msg:
                msgid.append(line.strip())
    
    dir,file = os.path.split(pofile)
    filebase, _ext = os.path.splitext(file)
    output = os.path.join(dir, filebase) + ".csv"
    open(output, "wb").write("".join(clines))
    

if __name__ == "__main__":
    define("locale", default='id_ID')
    define("basedir", default='')
    define("srcdir", default=['templates', 'handlers', 'translations/strings'], multiple=True)
    define("outdir", default='translations')
    define("verbose", default=False, type=bool)
    define("ext", default=[],help="Extensions of file to process (eg. .html,.js)",multiple=True)
    args = parse_command_line()
    
    basedir = os.path.curdir if not options.basedir else options.basedir
    basedir = os.path.abspath(basedir)
    cmd = set(args).pop() if args else 'makemessage'
    if cmd == 'makemessage':
        make_messages(options.locale, basedir, options.srcdir, options.outdir, options.ext, options.verbose)
    elif cmd == "makecsv":
        po_to_csv(os.path.join(basedir, options.outdir, options.locale + ".po"))
