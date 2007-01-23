############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_pages.py                                                        #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
# This file contains the definition of the class to handle the tabbed text #
# controls and all functions relating to the subpanel of the MainWindow    #
# class implimented in MainWindow.py. It will also manage and create the   #
# editra controls for the MainWindow.                                      #
#                                                                          #
# METHODS:                                                                 #
# - ED_Pages: Main instance of class. tracks page numbers                  #
# - NewPage: Creates a new empty page w/text control                       #
# - OpenPage: Opens a new page with an existing file                       #
# - GoCurrentPage: Sets focus to currentyl selected page                   #
# - OnPageChanging:                                                        #
# - OnPageChanged: Captures page change and switches context to the        #
#                  new page                                                #
# - ClosePage: Closes a page in the notebook                               #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies

import os			 # Python Modules
import sys
import re
import wx			 # wxPython Modules
# import wx.py
from ed_glob import CONFIG, version, prog_name
import ed_stc 			 # Editra Styled Text Control
import dev_tool			 # Editra Debug tools
import extern.FlatNotebook as FNB
#---- Class Globals ----#
IMG = {}

#--------------------------------------------------------------------------#
class ED_Pages(FNB.FlatNotebook):
    """ Editra tabbed pages class """
    def __init__(self, parent, id_num):
        """Initialize a notebook with a blank text control in it"""
        FNB.FlatNotebook.__init__(self, parent, id_num, 
                                  style=FNB.FNB_FANCY_TABS | 
                                        FNB.FNB_X_ON_TAB | 
                                        FNB.FNB_SMART_TABS |
                                        FNB.FNB_BACKGROUND_GRADIENT
                            )

        # Notebook attributes
        self.pg_num = -1              # Track page numbers for ID creation
        self.control = ed_stc.EDSTC   # Current Control page
        self.frame = parent           # MainWindow
        self.tab_close = -1           # Tab icon

        # Set Additional Style Parameters
        self.SetNonActiveTabTextColour(wx.ColourRGB(666666))

        # Notebook Events
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        self._pages.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        self.CreateImageList()

        # Add a blank page
        self.NewPage()

    #---- End Init ----#

    #---- Function Definitions ----#
    def AddPage(self, control, title):
        """Adds a page to the notebook"""
        FNB.FlatNotebook.AddPage(self, control, title, imageId=self.tab_close)

    def NewPage(self):
        """Create a new notebook page with a blank text control"""
        self.pg_num += 1
        # Create a new blank page and put it in the notebook
        self.control = ed_stc.EDSTC(self, self.pg_num,
                                    style=wx.TE_MULTILINE|wx.TE_RICH2)
        dev_tool.DEBUGP("[nb_evt] Page Creation ID: " + str(self.control.GetId()))
        self.AddPage(self.control, "Untitled - " + str(self.pg_num))
        self.SetPageImage(self.GetSelection(), IMG['TXT'])

    def OpenPageType(type=0):
        """A Generic Page open Function to allow pages to contain
        more than just text controls.

        """
        
    def OpenPage(self, path, filename):
        """Open a File Inside of a New Page"""
        # build path and check type
        path2file = os.path.join(path, filename)
        # Check if file exists and is actually a file
        if os.path.exists(path2file) and (not os.path.isfile(path2file)):
            return

        self.pg_num += 1

        # Create control to place text on
        self.control = ed_stc.EDSTC(self, self.pg_num,
                                    style = wx.TE_MULTILINE|wx.TE_RICH2)

        # Pass directory and file name info to control object to save reference
        self.control.dirname = path
        self.control.filename = filename

        # Put control into page an place page in notebook
        self.AddPage(self.control, self.control.filename)

        # Open file and put text into the control
        if os.path.exists(path2file):
            file_handle = open(path2file,'r')
            self.control.SetText(file_handle.read())
            file_handle.close()
        else:
            # Set Tab title for blank new file
            self.SetPageText(self.pg_num, self.control.filename)

        # Add file to history list
        self.frame.filehistory.AddFileToHistory(path2file)

        dev_tool.DEBUGP("[nb_evt] Opened Page: ID = " + str(self.GetSelection()))

        # Set style
        self.control.FindLexer()

        # Clear Undo Buffer of this control
        self.control.EmptyUndoBuffer()

        # Set tab image
        ftype = self.control.filename.split(".")
        ftype = ftype[-1].upper()
        pg_num = self.GetSelection()
        if ftype in IMG:
            dev_tool.DEBUGP("[nb_info] Set Page Image to: " + ftype)
            self.SetPageImage(pg_num, IMG[ftype])
        else:
            self.SetPageImage(pg_num, IMG['TXT'])

        # Refocus on selected page
        self.GoCurrentPage()

    def GoCurrentPage(self):
        """Move Focus to Currently Selected Page"""
        current_page = self.GetSelection()

        if current_page < 0:
            return current_page

        dev_tool.DEBUGP("[nb_info] Current Page = " + str(current_page))

        control = self.GetPage(current_page)
        control.SetFocus()
        self.control = control

        return current_page

    #---- Event Handlers ----#
    def OnLeftUp(self, evt):
        """Traps clicks sent to page close buttons and 
        redirects the action to the ClosePage function

        """
        cord, tabIdx = self._pages.HitTest(evt.GetPosition())
        if cord == FNB.FNB_X:
           # Make sure that the button was pressed before
           if self._pages._nXButtonStatus != FNB.FNB_BTN_PRESSED:
               return
           self._pages._nXButtonStatus = FNB.FNB_BTN_HOVER
           self.ClosePage()
        elif cord == FNB.FNB_TAB_X:
           # Make sure that the button was pressed before
           if self._pages._nTabXButtonStatus != FNB.FNB_BTN_PRESSED:
               return 
           self._pages._nTabXButtonStatus = FNB.FNB_BTN_HOVER
           self.ClosePage()
        else:
           evt.Skip()

    def OnPageChanging(self, evt):
        """Page changing event handler."""
        dev_tool.DEBUGP("[nb_evt] Page Changed to " + str(evt.GetSelection())) 
        evt.Skip()

    def OnPageChanged(self, evt):
        """Actions to do after a page change"""
        current = evt.GetSelection()
        window = self.GetPage(current) #returns current stc
        window.SetFocus()
        self.control = window

        if self.control.filename == "":
            self.control.filename = "Untitled - " + str(window.GetId())

        self.frame.SetTitle(self.control.filename + " - " + "file://" + 
                      self.control.dirname + self.control.path_char + 
                      self.control.filename + " - " + prog_name + " v" + version)

        matchstrn = re.compile('Untitled*')

        if matchstrn.match(self.control.filename):
            self.control.filename = ""

        self.control.Bind(wx.EVT_KEY_UP, self.frame.OnKeyUp)

        dev_tool.DEBUGP("[nb_evt] Control Changing from Page: " + str(evt.GetOldSelection()) + 
                        " to Page: " + str(evt.GetSelection()) + "\n" +
                        "[nb_info] It has file named: " + self.control.filename + "\n" +
                        "[nb_info] In DIR: " + self.control.dirname)
        self.frame.UpdateToolBar()
        evt.Skip()

    def OnPageClosing(self, evt):
        """Checks page status to flag warnings before closing"""
        dev_tool.DEBUGP("[nb_evt] Closing Page: #" + str(self.GetSelection()))
        evt.Skip()

    def OnPageClosed(self, evt):
        """Handles Paged Closed Event"""
        dev_tool.DEBUGP("[nb_evt] Closed Page: #" + str(self.GetSelection()))
        evt.Skip()
    #---- End Event Handlers ----#

    def ClosePage(self):
        """Closes Currently Selected Page"""
        self.GoCurrentPage()
        pg_num = self.GetSelection()
        result = wx.ID_OK
        if self.control.GetModify():
            result = self.frame.ModifySave()
            if result != wx.ID_CANCEL:
                self.DeletePage(pg_num)
                self.GoCurrentPage()
            else:
                pass
        else:
            self.DeletePage(pg_num)
            self.GoCurrentPage()

        return result

    def CreateImageList(self):
        """Creates the image list for the tabs buttons."""
        #HACK should have a mime type provider to handle filetypes/images ect
        # Get Images
        img_dir = CONFIG['MIME_DIR']
        IMG["C"] = wx.Bitmap(img_dir + "c.png", wx.BITMAP_TYPE_PNG)
        IMG["CPP"] = wx.Bitmap(img_dir + "cpp.png", wx.BITMAP_TYPE_PNG)
        IMG["CSS"] = wx.Bitmap(img_dir + "css.png", wx.BITMAP_TYPE_PNG)
        IMG["H"] = wx.Bitmap(img_dir + "header.png", wx.BITMAP_TYPE_PNG)
        IMG["HTML"] = wx.Bitmap(img_dir + "html.png", wx.BITMAP_TYPE_PNG)
        IMG["JAVA"] = wx.Bitmap(img_dir + "java.png", wx.BITMAP_TYPE_PNG)
        IMG["MAKEFILE"] = wx.Bitmap(img_dir + "makefile.png", wx.BITMAP_TYPE_PNG)
        IMG["PL"] = wx.Bitmap(img_dir + "perl.png", wx.BITMAP_TYPE_PNG)
        IMG["PHP"] = wx.Bitmap(img_dir + "php.png", wx.BITMAP_TYPE_PNG)
        IMG["PY"] = wx.Bitmap(img_dir + "python.png", wx.BITMAP_TYPE_PNG)
        IMG["RB"] = wx.Bitmap(img_dir + "ruby.png", wx.BITMAP_TYPE_PNG)
        IMG["SH"] = wx.Bitmap(img_dir + "shell.png", wx.BITMAP_TYPE_PNG)
        IMG["TEX"] = wx.Bitmap(img_dir + "tex.png", wx.BITMAP_TYPE_PNG)
        IMG["TXT"] = wx.Bitmap(img_dir + "text.png", wx.BITMAP_TYPE_PNG)

        # Create Image List
        il = wx.ImageList(16, 16)

        # Add Images to List and restore indexs to IMG dictionary
        IMG["C"] = il.Add(IMG["C"])
        IMG["CPP"] = il.Add(IMG["CPP"])
        IMG["CSS"] = il.Add(IMG["CSS"])
        IMG["H"] = il.Add(IMG["H"])
        IMG["HTML"] = il.Add(IMG["HTML"])
        IMG["JAVA"] = il.Add(IMG["JAVA"])
        IMG["MAKEFILE"] = il.Add(IMG["MAKEFILE"])
        IMG["PL"] = il.Add(IMG["PL"])
        IMG["PHP"] = il.Add(IMG["PHP"])
        IMG["PY"] = il.Add(IMG["PY"])
        IMG["RB"] = il.Add(IMG["RB"])
        IMG["SH"] = il.Add(IMG["SH"])
        IMG["TEX"] = il.Add(IMG["TEX"])
        IMG["TXT"] = il.Add(IMG["TXT"])

        # Set duplicate indexs
        IMG["CSH"] = IMG["SH"]
        IMG["KSH"] = IMG["SH"]

        self.SetImageList(il)
        dev_tool.DEBUGP("[nb_info] Created Image List: Size = " + str(self.GetImageList().GetImageCount()))
        return 0

    def UpdatePageImage(self):
        """Updates the page tab image"""
        pg_num = self.GetSelection()
        ftype = self.control.filename.split(".")
        ftype = ftype[-1].upper()
        dev_tool.DEBUGP("[nb_info] Updating Page Image: Page " + str(pg_num))
        if ftype in IMG:
            self.SetPageImage(pg_num, IMG[ftype])
        else:
            self.SetPageImage(pg_num, IMG["TXT"])

#---- End Function Definitions ----#
