# Introduction

Accuri2svg is a command line program for the conversion of Accuri `.c6` flow cytometry data
files to the standard `.fcs` format. 

# Basic usage

Usage is not *exactly* straightforward, however it is quite powerful. The best approach is
to gradually build up the matching regular expressions to get to your target files. If your
sample naming is particularly weird, you might need to do >1 run.

In it's standard configuration it will find all `.c6` files in the current directory,
match every sample name outputting `.fcs` files named [filename.c6]_[row|column].fcs.
This is probably perfectly fine for most uses.

Usage: accuri2fcs.py [options]

    Options:
      -h, --help            show this help message and exit
      -f FILE.c6, --filename=FILE.c6
                            match to find filename(s) to convert supports
                            wildcards
      -n NAME_REGEXP, --name-regexp=NAME_REGEXP
                            regexp pattern match to split Sample Name (customise
                            this together with output path pattern to file in
                            subfolders)
      --op=OUTPUT_PATH_PATTERN
                            pattern for resulting output path (based on named
                            strings in -n regexp)
      --on=OUTPUT_NAME_PATTERN
                            pattern for resulting output filename (based on named
                            strings in -n regexp)
      -t TARGET, --target=TARGET
                            target folder in current folder to copy resulting fcs
                            files
      -d DIRECTION, --direction=DIRECTION
                            process data (c)olumn wise or (r)ow wise
      --fill                fill in data from previous column/row contents (e.g.
                            header will apply to all subsequent in column)
      --fill-all            fill in data from any previous cell (first header will
                            apply to all subsequent)
      --discard             discard samples where no name regex matches

# More complicated usage

Named [regular expression][regularexpressions] matching can be used to extract variables from the Sample Names. 
For example, you may want to search for a particular condition and then use this for the 
destination folder of the resulting `.fcs` file, or to build the output file name. 

Additionally, you can use the fill options together with direction, to pre-fill data not
present for a given sample. This is useful if you've labelled your first sample in a row
but then only labelled subsequent changes.

A few examples are listed below (indented for clarity)

    ~/Scripts/accuri2fcs.py 
        -n '^(?P<treatment>\d+TT)\s+?(?P<patient>SI?R?[0-9]+)\s+?(?P<timepoint>Pre Op\d+|D\d+|M\d+|\d+)$'
        --op '%(patient)s'
        --on '%(treatment)s_%(timepoint)s_(%(id)s)_%(file)s.fcs'
        --discard
        -t '/Volumes/USB-HDD/MM/fcs'
        -f '*.c6' 

    0TT  S32 D14

In the above example we get all `.c6` files in the current folder. We match possible variables
in the target sample names, extracting 3 variables 'treatment', 'patient' and 'timepoint'.
The patient identifier is used for the output path, the treatment and timepoint (together with
the row/column identifier e.g. A6 from the Accuri file and the origin filename - two 
always available variables). Non-matching samples are discarded (rather than moved to a 'everything else' folder)
on the target volume.

While it looks horrendous, if you build it up bit by bit it's really very logical.

# License

GPML2SVG is available free for any use under the [New BSD license][newbsd].


 [accuri2fcs-github]: https://github.com/mfitzp/accuri2fcs
 [accuri2fcs-github-issues]: https://github.com/mfitzp/accuri2fcs/issues

 [regularexpressions]: http://www.zytrax.com/tech/web/regex.htm
 [newbsd]: http://en.wikipedia.org/wiki/BSD_licenses#3-clause
 