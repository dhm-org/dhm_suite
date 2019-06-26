# General python 
import os, sys

# Qt5 / QML specific
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QFileDialog

## CLASS ##
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  @class
#     class CreateFileDialog(QWidget)
#  @par
#     This is DHMx's custom file dialog class and offers a few options for customization
#  @params
#      x : Int -x-axis pixel position (starting from upper left 0,0)
#      y : Int - y-axis pixel position (starting from upper left 0,0)
#      directory: String - the directory in which the file dialog will open under
#      title: The title of the filedialog's window
#      opts : String - passed in to determine what kind of file dialog window
#             to populate.  The user may execute a schedule or generic window, please
#             see more information below...
class CreateFileDialog(QWidget):

  # CONSTRUCTOR
  def __init__(self, x, y, directory, title, opts):
    super().__init__()
    self.title = title
    self.x = x
    self.y = y
    self.width = 800
    self.height = 600
    self.directory = directory
    self.filename = None
    self.opts = opts

    self.InitUI()


  ## DEFINITION (CreateFileDialog) ##
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  @class
  #     class CreateFileDialog(QWidget)
  #     @fn
  #        InitUI(self)
  #     @par
  #        Loads the file dialog window's size and position parameters and displays
  def InitUI(self):
    self.setGeometry(self.x-(self.width/2), self.y-(self.height/2), self.width, self.height)
    self.OpenFileNameDialog()
    self.show()
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


  ## DEFINITION (CreateFileDialog) ##
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  @class
  #     class CreateFileDialog(QWidget)
  #     @fn
  #        OpenFileNameDialog(self)
  #     @par
  #        Opens the file dialog window in Qt's non-native file dialog style, sets the
  #        window title, directory and mode (opts).
  def OpenFileNameDialog(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog

    if(self.opts == "save_ses"):
       self.filename, _ = QFileDialog.getSaveFileName(self,self.title, self.directory,"Session Files (*.ses);;All Files (*.*)", options=options)
    if(self.opts == "load_ses"):
       self.filename, _ = QFileDialog.getOpenFileName(self,self.title, self.directory,"Session Files (*.ses);;All Files (*.*)", options=options)
    if(self.opts == "save_cfg"):
       self.filename, _ = QFileDialog.getSaveFileName(self,self.title, self.directory,"Config Files (*.cfg);;All Files (*.*)", options=options)
    if(self.opts == "load_cfg"):
       self.filename, _ = QFileDialog.getOpenFileName(self,self.title, self.directory,"Config Files (*.cfg);;All Files (*.*)", options=options)

    # Below is for dhmxc for saving and loading camera config files
    if(self.opts == "save_camera_cfg"):
       self.filename, _ = QFileDialog.getSaveFileName(self,self.title, self.directory,"Camera Config Files (*.ccf);;All Files (*.*)", options=options)
    if(self.opts == "load_camera_cfg"):
       self.filename, _ = QFileDialog.getOpenFileName(self,self.title, self.directory,"Camera Config Files (*.ccf);;All Files (*.*)", options=options)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


  ## DEFINITION (CreateFileDialog) ##
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  @class
  #     class CreateFileDialog(QWidget)
  #     @fn
  #        GetDir(self)
  #     @par
  #        Returns the directory in where the file was chosen (after window closes)
  def GetDir(self):
    return os.path.dirname(os.path.abspath(self.filename))
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


  ## DEFINITION (CreateFileDialog) ##
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  @class
  #     class CreateFileDialog(QWidget)
  #     @fn
  #        GetFilename(self)
  #     @par
  #        Returns the directory and filename in where the file was chosen (after window closes)
  def GetFilename(self):
    #if(self.filename == ""):
    return self.filename
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
