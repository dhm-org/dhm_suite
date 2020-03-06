"""
###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software,
#  the user agrees to comply with all applicable U.S. export laws and regulations.
#  User has the responsibility to obtain export licenses, or other export authority
#  as may be required before exporting such information to foreign countries or providing
#  access to foreign persons.
#
#  file:	sequence.py
#  author:	S. Felipe Fregoso
#  description:	Functions for execution sequence of holograms
###############################################################################
"""
import os
import numpy as np

LEGACY_VER_0 = 0 # Koala produced data indicated by the existance of the 'Holograms'
                 # directory and the 'timestamps.txt' file
LEGACY_VER_1 = 1 # Produced by the DHMSW
LEGACY_VER_UNKNOWN = 2

class Sequence():
    """
    Sequence Mode Class
    """
    def __init__(self, tsfname='timestamps.txt', tsdelimeter=" "):
        """
        Constructor
        """
        self.tsfname = tsfname
        self.tsdelimeter = tsdelimeter

    def read_timestamp_file(self, tsfile):
        """
        Read the timestamp file
        ### is_koala_legacy:  True if 'Holograms' directory exists, False if it doesn't
        ### Line 1:    Timestamp time YY.MM.DD absolute_ms
        ### Line N+1:  Counter time YY.MM.DD offset_ms
        """

        rec = []
        with open(tsfile, "r") as fid:
            line = fid.readline().rstrip()
            while line:
                rec.append(line.split(self.tsdelimeter))
                line = fid.readline().rstrip()

        #Sort
        rec_list = [int(col[0]) for col in rec]
        #b = sorted(b, key=int)
        sortidx = np.argsort(rec_list)

        sortrec = {}
        sortrec['records'] = rec.copy()
        for idx, value in enumerate(sortidx):
            sortrec['records'][idx] = rec[value]

        print(sortrec)
        return sortrec

    def get_sequence_filepaths(self, fpath):
        """
        Get the sequence filepaths
        """
        ### Ensure the path is a string
        if not isinstance(fpath, str):
            raise ValueError('The path must be a string')

        ### Determine that the path is a directory and not a file
        if not os.path.isdir(fpath):
            raise IOError('The path [%s] is not a directory.'%(fpath))

        ### Ensure there is a file named 'timestamps.txt' in the directory
        tsfile = fpath + '/' + self.tsfname
        if not os.path.exists(tsfile):
            raise IOError('The file [%s] does not exist in this directory and'\
                          ' is required to exist.'%(tsfile))

        ### Determine if we are looking at Koala legacy or dhmsw legacy.
        # Koala ==> if 'Hologram' directory exists.
        data_dir = fpath + '/' + 'Holograms'
        if not os.path.isdir(data_dir):
            raise IOError('The "Holograms" directory does not exist in [%s] and'\
                          ' is required to exist.'%(fpath))

        rec = self.read_timestamp_file(tsfile)

        filepaths = []
        pathroot = data_dir
        postfix = '_holo'

        for name in rec['records']:
            fullpath = pathroot + '/' + '%s%s.tif'%(name[0], postfix)
            print(fullpath)
            filepaths.append(fullpath)

        return filepaths

if __name__ == "__main__":
    ## Koala version
    PATH = '/proj/dhm/sfregoso/data/legacy/2018.08.01 15-25/'
    PATH = '/proj/dhm/sfregoso/git_repos/dhm_streaming/2018.11.07/2018.11.07_33.37'
    PATH = '/proj/dhm/sfregoso/git_repos/dhm_streaming/2018.11.08/2018.11.08_45.59'
    SEQ = Sequence()
    SEQ.get_sequence_filepaths(PATH)
