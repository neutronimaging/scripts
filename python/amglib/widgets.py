import os
from ipyfilechooser import FileChooser
import ipywidgets as widgets
import sys
import amglib.readers as rd

class FileSelector:
    FILE_PATTERNS = ['*.png', '*.jpg', '*.npy', '*.fits', '*.tif', '*.tiff']
    
    @property
    def file_name(self) :
        return self._fileinfo["name"]
    
    @property 
    def file_path(self) :
        return self._fileinfo["path"]
    
    @property 
    def file_mask(self) :
        return self._fileinfo["mask"]
    
    @property 
    def first_index(self) :
        return self._fileinfo["first"]
    
    @property
    def last_index(self) :
        return self._fileinfo["last"]
    
    @property
    def info(self) :
        return self._fileinfo

    def __init__(self, start_dir='.'):
        self.file_chooser = FileChooser(
            os.path.realpath(start_dir),
            show_only_dirs=False,
            select_desc="Browse file",
            change_desc="Change file",
#             filter_pattern=";".join(self.FILE_PATTERNS)
        )
        self.file_chooser.layout = widgets.Layout(width='800px')
        self.file_chooser._select.layout = widgets.Layout(width="200px")
        self.file_chooser.register_callback(self.on_file_selected)

    def on_file_selected(self, chooser):
        selected = chooser.selected
        if selected:
            self.analyze_file(selected)

    def analyze_file(self, filename):
        # Implement your analysis logic here
        selected_file      = self.file_chooser.selected
        path       = os.path.dirname(selected_file)
        fname      = os.path.basename(selected_file)

        ext        = selected_file.split('.')[-1]
        flist      = rd.list_matching_files(path,r'_'.join(fname.split('_')[:-1])+'*.'+ext)
        fmask      = rd.make_file_mask(selected_file)
        first,last = rd.find_first_last_indices(flist)

        self._fileinfo = { "name" : selected_file,
                           "mask" : fmask,
                           "path" : path,
                           "ext"  : ext,
                           "first": first,
                           "last" : last,
                           "files": flist}

    def display(self):
        display(self.file_chooser)
