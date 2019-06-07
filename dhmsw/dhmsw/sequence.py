import os
import numpy as np

LEGACY_VER_0 = 0 # Koala produced data indicated by the existance of the 'Holograms' directory and the 'timestamps.txt' file
LEGACY_VER_1 = 1 # Produced by the DHMSW
LEGACY_VER_UNKNOWN = 2

class Sequence(object):
    def __init__(self, tsfname='timestamps.txt', tsdelimeter=" "):
        self.tsfname = tsfname
        self.tsdelimeter = tsdelimeter
        pass

    def read_timestamp_file(self, tsfile):
        ### is_koala_legacy:  True if 'Holograms' directory exists, False if it doesn't
        ### Line 1:    Timestamp time YY.MM.DD absolute_ms
        ### Line N+1:  Counter time YY.MM.DD offset_ms

        rec = []
        with open(tsfile, "r") as f:
            line = f.readline().rstrip()
            while line:
                rec.append(line.split(self.tsdelimeter))
                line = f.readline().rstrip()

        #Sort
        b = [int(col[0]) for col in rec]
        #b = sorted(b, key=int)
        sortidx = np.argsort(b)

        sortrec = {}
        sortrec['records'] = rec.copy()
        for i,v in enumerate(sortidx):
            sortrec['records'][i] = rec[v]

        print(sortrec)
        return sortrec

    def get_sequence_filepaths(self, path):

        ### Ensure the path is a string
        if type(path) is not str:
            raise ValueError('The path must be a string')

        ### Determine that the path is a directory and not a file
        if not os.path.isdir(path):
            raise IOError('The path [%s] is not a directory.'%(path))

        ### Ensure there is a file named 'timestamps.txt' in the directory
        tsfile = path + '/' + self.tsfname
        if not os.path.exists(tsfile):
            raise IOError('The file [%s] does not exist in this directory and is required to exist.'%(tsfile))

        ### Determine if we are looking at Koala legacy or dhmsw legacy.
        # Koala ==> if 'Hologram' directory exists.
        data_dir = path + '/' + 'Holograms'
        if not os.path.isdir(data_dir):
            raise IOError('The "Holograms" directory does not exist in [%s] and is required to exist.'%(path))

        rec = self.read_timestamp_file(tsfile)

        filepaths = []
        pathroot = data_dir
        postfix = '_holo'

        for r in rec['records']:
            fpath = pathroot + '/' + '%s%s.tif'%(r[0], postfix)
            print(fpath)
            filepaths.append(fpath)
        
        return filepaths

if __name__ == "__main__":
    ## Koala version
    path = '/proj/dhm/sfregoso/data/legacy/2018.08.01 15-25/'
    path = '/proj/dhm/sfregoso/git_repos/dhm_streaming/2018.11.07/2018.11.07_33.37'
    path = '/proj/dhm/sfregoso/git_repos/dhm_streaming/2018.11.08/2018.11.08_45.59'
    a = Sequence()
    a.get_sequence_filepaths(path)
