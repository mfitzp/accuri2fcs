#!/usr/bin/python

'''
Convert Accuri format files to .fcs by extracting internal .fcs format files and renaming
under folder structure to match the input regexp. If provided output filename will be
constructed from named variables.

^(?P<treatment>\d+oC)\s+?(?P<patient>SI?R?[0-9]+)\s+?(?P<timepointd1>Pre Op\d+|D\d+|M\d+|\d+)\s+?(?P<timepointd2>Pre Op\d+|D\d+|M\d+|\d+)$
~/Scripts/accuri2fcs.py -n '^(?P<treatment>\d+oC)\s+?(?P<patient>SI?R?[0-9]+)\s+?(?P<timepointd1>Pre Op\d+|D\d+|M\d+|\d+)\s+?(?P<timepointd2>Pre Op\d+|D\d+|M\d+|\d+)$' --op '%(patient)s' --on '%(treatment)s_%(timepointd1)s_%(timepointd2)s_(%(id)s)_%(file)s.fcs' --discard -t '/Volumes/USB-HDD/MM/fcs' -f '*.c6' 
~/Scripts/accuri2fcs.py -f '*.c6' -n '^(?P<treatment>\d+oC)\s+?(?P<patient>S[IR]?[0-9]+)\s+?(?P<timepointd1>Pre Op\d+|D\d+|M\d+|\d+)\s+?(?P<timepointd2>Pre Op\d+|D\d+|M\d+|\d+)$' --op '%(patient)s' --on '%(treatment)s_%(timepointd1)s_%(timepointd2)s_(%(id)s)_%(file)s.fcs' --discard -t '/Volumes/USB-HDD/MM/fcs'
'''

import os, errno, re, glob, shutil
import tempfile
import operator

from optparse import OptionParser
from collections import defaultdict
from zipfile import ZipFile


def makedirsp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise
        # Got the folder            

def sort_row(s):     
    return s[0] 

def sort_col(s):     
    return s[1] 

def sorted_by(list, sort_type):
    if sort_type == 'c':
        return sorted( sorted(list, key=sort_col), key=sort_row)
    elif sort_type == 'r':
        return sorted( sorted(list, key=sort_row), key=sort_col)
        
        
        
def main():

    parser = OptionParser()

    parser.add_option("-f", "--filename", dest="filename", default='*.c6',
                      help="match to find filename(s) to convert supports wildcards", metavar="FILE.c6")

    #parser.add_option("-s", "--sample-regexp", dest="sample_regexp", default='\$SAMPLEIDENTIFIER/(?P<id>[A-Z][0-9])/\$SAMPLENAME/(?P<name>.*?)/',
    #                  help="regexp pattern match to get Sample Name/Identifier")

    parser.add_option("-n", "--name-regexp", dest="name_regexp", default='^(?P<all>.*)$',
                      help="regexp pattern match to split Sample Name (customise this together with output path pattern to file in subfolders)")

    parser.add_option("--op", dest="output_path_pattern", default='',
                      help="pattern for resulting output path (based on named strings in -n regexp)")

    parser.add_option("--on", dest="output_name_pattern", default='%(file)s_[%(id)s].fcs',
                      help="pattern for resulting output filename (based on named strings in -n regexp)")

    parser.add_option("-t", "--target", dest="target", default='./fcs',
                      help="target folder in current folder to copy resulting fcs files")
                      
    parser.add_option("-d", "--direction", dest="direction", default='c',
                      help="process data (c)olumn wise or (r)ow wise")

    parser.add_option("--fill", dest="fill_in", action='store_true', default=False,
                      help="fill in data from previous column/row contents (e.g. header will apply to all subsequent in column)")

    parser.add_option("--fill-all", dest="fill_all", action='store_true', default=False,
                      help="fill in data from any previous cell (first header will apply to all subsequent)")

    parser.add_option("--discard", dest="discard", action='store_true', default=False,
                      help="discard samples where no name regex matches")
                      
        
    (options, args) = parser.parse_args()
        
    # --name-regexp
    # /Wash sir60 D32 090112/
    # /(?P<treatment>)\s(?P<patient>)\s(?P<day>)\s(?P<date>)/
    
    cols = range(1,13)
    rows = "ABCDEFGH"

    if options.direction == 'r':
        fidx = 1
    else:
        fidx = 0
    last_fidx = ''
    
    # Get a list of all matching files from current folder
    files = glob.glob(options.filename)

    temppath = os.path.join( tempfile.gettempdir(), 'accuri2fcs') 
    
    sample_re = re.compile('\$SAMPLEIDENTIFIER/(?P<id>[A-Z][0-9])/\$SAMPLENAME/(?P<name>.*?)/', re.IGNORECASE)
    
    # Support multiple patterns for incomplete labels (AARGH!)
    name_res = []
    for pattern in options.name_regexp.split(','):
        name_res.append( re.compile(pattern, re.IGNORECASE) )
    
    makedirsp(temppath)
    makedirsp(options.target)

    # Extract zip to temporary directory; get a list of files
    for n, file in enumerate(files):
        print "Extracting from `%s`... (%d/%d)" % ( file, n, len(files ) )
        # Make folder for this zip
        filetemppath = os.path.join(temppath, file)
        makedirsp(filetemppath)
        
        with ZipFile(file, 'r') as myzip:
            # Extract data to temporary folder
            myzip.extractall(filetemppath)
    
            # Match against collectManager.txt file to get a list of samples (.fcs files), names, etc.
            with open ( os.path.join(filetemppath,'collectManager.txt'), 'r') as myfile:
                data=myfile.read().replace('\n', '')
        
                # Process list of names using name-regexp to split data for folder structure
                matches = dict( sample_re.findall(data) )
                
                # Process columnwise / rowwise
                keys = matches.keys()
                keys = sorted_by(keys, options.direction)
                
                # Reset names data; defaultdict allows optional match on formatting string
                names = defaultdict(str)
            
                # For each sample ID copy .fcs file to target folder directory
                for id in keys:
                    name = matches[id] #id,name in matches.items():
                
                    # Check we haven't shifted column/row (if we mind)
                    if ( not options.fill_in or id[fidx] != last_fidx ) and not options.fill_all:
                        names.clear()
                        last_fidx = id[fidx]
                    
                    matched = False
                    for name_re in name_res:
                        name_match = name_re.search( name )
                        if name_match != None:
                            names.update(  dict( [(m,v) for m,v in name_match.groupdict().items()] ) )
                            matched = True
                            break # Stop trying patterns
                            
                    if options.discard and matched == False:
                        continue # Skip writeout, continue loop
                    
                    # Defaults, always available regardless of the labeling
                    names['all' ] = name
                    names['id' ] = id
                    names['file' ] = file

                    from_name = 'Sample %s%02d.fcs' % (id[0], int(id[1:]))
                    to_name = options.output_name_pattern % names
                    to_path = options.output_path_pattern % names
                    
                    (origin, dest ) = os.path.join(filetemppath,from_name), os.path.join( options.target, to_path, to_name)
                    if os.path.exists(origin):
                        makedirsp( os.path.join( options.target, to_path) )
                        print "%s -> %s" % (name, dest)
                        shutil.move( origin, dest )
                        
            # Delete temporary files
            shutil.rmtree( filetemppath, ignore_errors=True )

if __name__ == "__main__":
    main()