############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
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

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import glob
import re
import wx
import ed_glob
import ed_event
import ed_stc
import syntax.synglob as synglob
import ed_search
import util
import doctools
import wx.lib.flatnotebook as FNB

#---- Class Globals ----#
# HACK till proper artprovider can be written
IMG = {}

_ = wx.GetTranslation

# Compatibility for wxPython versions before 2.8.4
if hasattr(FNB, 'FNB_FF2'):
    TAB_STYLE = FNB.FNB_FF2
else:
    TAB_STYLE = FNB.FNB_FANCY_TABS
#--------------------------------------------------------------------------#
class ED_Pages(FNB.FlatNotebook):
    """ Editra tabbed pages class """
    def __init__(self, parent, id_num):
        """Initialize a notebook with a blank text control in it"""
        FNB.FlatNotebook.__init__(self, parent, id_num, 
                                  style=TAB_STYLE |
                                        FNB.FNB_X_ON_TAB | 
                                        FNB.FNB_SMART_TABS |
                                        FNB.FNB_BACKGROUND_GRADIENT
                            )

        # Notebook attributes
        self.LOG = wx.GetApp().GetLog()
        self.FindService = ed_search.TextFinder(self, self.GetCurrentCtrl)
        self.DocMgr = doctools.DocPositionMgr(ed_glob.CONFIG['CACHE_DIR'] + \
                                              util.GetPathChar() + u'positions')
        self.pg_num = 0               # Track page numbers for ID creation
        self.control = ed_stc.EDSTC   # Current Control page
        self.frame = parent.GetParent() # MainWindow
        self._index = dict()          # image list index

        # Set Additional Style Parameters
        self.SetNonActiveTabTextColour(wx.ColourRGB(long("666666", 16)))

        # Setup the ImageList and the default image
        il = wx.ImageList(16,16)
        txtbmp = wx.ArtProvider.GetBitmap(str(synglob.ID_LANG_TXT), wx.ART_MENU)
        self._index[synglob.ID_LANG_TXT] = il.Add(txtbmp)
        self.SetImageList(il)

        # Notebook Events
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        self.Bind(ed_event.EVT_UPDATE_TEXT, self.OnUpdatePageText)
        self._pages.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Add a blank page
        self.NewPage()

    #---- End Init ----#

    #---- Function Definitions ----#
    def AddPage(self, control, title):
        """Adds a page to the notebook"""
        self.pg_num += 1
        FNB.FlatNotebook.AddPage(self, control, title)

    def GetCurrentCtrl(self):
        """Returns the control of the currently selected
        page in the notebook.

        """
        if hasattr(self, 'control'):
            return self.control
        else:
            return None

    def NewPage(self):
        """Create a new notebook page with a blank text control"""
        self.control = ed_stc.EDSTC(self, self.pg_num)
        self.LOG("[nb_evt] Page Creation ID: %d" % self.control.GetId())
        self.AddPage(self.control, u"Untitled - %d" % self.pg_num)
        self.SetPageImage(self.GetSelection(), str(self.control.lang_id))

    def OpenPageType(self, page, title):
        """A Generic Page open Function to allow pages to contain
        any type of widget.

        """
        self.AddPage(page, title)

    def OpenPage(self, path, filename):
        """Open a File Inside of a New Page"""
        path2file = os.path.join(path, filename)

        # If file is non-existant or not a file give up
        if os.path.exists(path2file) and (not os.path.isfile(path2file)):
            return

        # Check if file is open already and ask if it should be opened again
        if self.HasFileOpen(path2file):
            mdlg = wx.MessageDialog(self,
                                    _("File is already open in an existing page."
                                      "\nDo you wish to open it again?"),
                                    _("Open File") + u"?", 
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
            result = mdlg.ShowModal()
            mdlg.Destroy()
            if result == wx.ID_NO:
                return

        # Create new control to place text on if necessary
        new_pg = True
        if self.GetPageCount():
            if self.control.GetModify() or self.control.GetLength() or \
               self.control.filename != u'':
                control = ed_stc.EDSTC(self, self.pg_num)
                control.Hide()
            else:
                new_pg = False
        else:
            control = ed_stc.EDSTC(self, self.pg_num)
            control.Hide()

        # Open file and get contents
        err = False
        in_txt = u''
        if os.path.exists(path2file):
            try:
                reader = util.GetFileReader(path2file)
                in_txt = reader.read()
                reader.close()
            except Exception, msg:
                # File could not be opened/read give up
                reader.close()
                err = wx.MessageDialog(self, _("Editra could not properly open %s\n") \
                                       % path2file, _("Error Opening File"),
                                       style=wx.OK | wx.CENTER | wx.ICON_ERROR)
                err.ShowModal()
                err.Destroy()

                if new_pg:
                    control.Destroy()
                return

        # Put control into page an place page in notebook
        if new_pg:
            control.Show()
            self.control = control
        self.control.SetText(in_txt)
        # Pass directory and file name info to control object to save reference
        self.control.dirname = path
        self.control.filename = filename
        self.frame.filehistory.AddFileToHistory(path2file)
        self.control.modtime = util.GetFileModTime(path2file)
        if new_pg:
            self.AddPage(self.control, self.control.filename)
            self.SetPageText(self.GetSelection(), self.control.filename)
        else:
            self.SetPageText(self.GetSelection(), self.control.filename)
            self.frame.SetTitle("%s - file://%s%s%s" % (self.control.filename, 
                                                        self.control.dirname, 
                                                        self.control.path_char, 
                                                        self.control.filename))
        self.LOG("[nb_evt] Opened Page: ID = %d" % self.GetSelection())

        # Set style
        self.control.FindLexer()

        # Check EOL characters
        self.control.CheckEOL()

        # Clear Undo Buffer of this control
        self.control.EmptyUndoBuffer()

        if ed_glob.PROFILE['SAVE_POS']:
            self.control.GotoPos(self.DocMgr.GetPos(self.control.GetFileName()))

        # Set tab image
        ftype = self.control.filename.split(".")
        ftype = ftype[-1].upper()
        pg_num = self.GetSelection()
        self.SetPageImage(pg_num, str(self.control.lang_id))

        # Refocus on selected page
        self.GoCurrentPage()

    def GoCurrentPage(self):
        """Move Focus to Currently Selected Page"""
        current_page = self.GetSelection()
        if current_page < 0:
            return current_page

        self.LOG("[nb_info] Current Page = %d" % current_page)

        control = self.GetPage(current_page)
        control.SetFocus()
        self.control = control
        return current_page

    def GetPageText(self, pg_num):
        """Gets the tab text from the given page number, stripping
        the * mark if there is one.

        """
        txt = FNB.FlatNotebook.GetPageText(self, pg_num)
        if txt[0] != u"*":
            return txt
        else:
            return txt[1:]

    def GetTextControls(self):
        """Gets all the currently opened text controls"""
        children = self.GetChildren()
        controls = list()
        for child in children:
            if hasattr(child, '__name__') and child.__name__ == u"EditraTextCtrl":
                controls.append(child)
        return controls

    def HasFileOpen(self, fpath):
        """Checks if one of the currently active buffers has
        the named file in it.

        """
        ctrls = self.GetTextControls()
        for ctrl in ctrls:
            if fpath == os.path.join(ctrl.dirname, ctrl.filename):
                return True
        return False

    #---- Event Handlers ----#
    def OnDrop(self, files):
        """Opens drop files"""
        # Check file properties and make a "clean" list of file(s) to open
        valid_files = list()
        for fname in files:
            self.LOG("[fdt_evt] File(s) Dropped: %s" % fname)
            if not os.path.exists(fname):
                self.frame.PushStatusText(_("Invalid file: %s") % fname, ed_glob.SB_INFO)
            elif os.path.isdir(fname):
                dcnt = glob.glob(os.path.join(fname, '*'))
                dcnt = util.FilterFiles(dcnt)
                if not len(dcnt):
                    dlg = wx.MessageDialog(self, _("There are no files that Editra"
                                                   " can open in %s") % fname,
                                           _("No Valid Files to Open"),
                                           style=wx.OK|wx.CENTER|wx.ICON_INFORMATION)
                else:
                    dlg = wx.MessageDialog(self, _("Do you wish to open all %d"
                                           " files in this directory?\n\nWarning opening"
                                           " many files at once may cause the"
                                           " editor to temporarly freeze.") % len(dcnt),
                                           _("Open Directory?"),
                                           style = wx.YES|wx.NO|wx.ICON_INFORMATION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_YES:
                    valid_files.extend(dcnt)
                else:
                    pass
            else:
                valid_files.append(fname)

        for fname in valid_files:
            pathname = util.GetPathName(fname)
            the_file = util.GetFileName(fname)
            self.OpenPage(pathname, the_file)
            self.frame.PushStatusText(_("Opened file: %s") % fname, ed_glob.SB_INFO)
        return

    def OnIdle(self, evt):
        """Update tabs and check if files have been modified"""
        if ed_glob.PROFILE['CHECKMOD'] and \
           wx.GetApp().IsActive() and self.GetPageCount():
            cfile = os.path.join(self.control.dirname, self.control.filename)
            lmod = util.GetFileModTime(cfile)
            if self.control.modtime and not lmod and not os.path.exists(cfile):
                def PromptToReSave(cfile):
                    mdlg = wx.MessageDialog(self.frame,
                                            _("%s has been deleted since its "
                                              "last save point.\n\nWould you "
                                              "like to save it again?") % cfile,
                                            _("Resave File?"), 
                                            wx.YES_NO | wx.ICON_INFORMATION)
                    mdlg.CenterOnParent()
                    result = mdlg.ShowModal()
                    mdlg.Destroy()
                    if result == wx.ID_YES:
                        self.control.SaveFile(cfile)
                    else:
                        self.control.modtime = 0
                wx.CallAfter(PromptToReSave, cfile)

            elif self.control.modtime < lmod:
                def AskToReload(cfile):
                    mdlg = wx.MessageDialog(self.frame, 
                                            _("%s has been modified by another "
                                              "application.\n\nWould you like to "
                                              "Reload it?") % cfile, _("Reload File?"),
                                              wx.YES_NO | wx.ICON_INFORMATION)
                    mdlg.CenterOnParent()
                    result = mdlg.ShowModal()
                    mdlg.Destroy()
                    if result == wx.ID_YES:
                        self.control.ReloadFile()
                    else:
                        self.control.modtime = util.GetFileModTime(cfile)
                wx.CallAfter(AskToReload, cfile)
            else:
                evt.Skip()
                                          
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
        self.LOG("[nb_evt] Page Changed to %d" % evt.GetSelection())
        evt.Skip()

    def OnPageChanged(self, evt):
        """Actions to do after a page change"""
        current = evt.GetSelection()
        window = self.GetPage(current) #returns current stc
        window.SetFocus()
        self.control = window

        if self.control.filename == "":
            self.control.filename = "Untitled - %d" % window.GetId()

        self.frame.SetTitle("%s - file://%s%s%s" % (self.control.filename,
                                                    self.control.dirname,
                                                    self.control.path_char,
                                                    self.control.filename))

        matchstrn = re.compile('Untitled*')
        if matchstrn.match(self.control.filename):
            self.control.filename = ""

        self.control.Bind(wx.EVT_KEY_UP, self.frame.OnKeyUp)
        self.control.Bind(wx.EVT_LEFT_UP, self.frame.OnKeyUp)

        self.LOG(("[nb_evt] Control Changing from Page: %d to Page: %d\n"
                 "[nb_info] It has file named: %s\n"
                 "[nb_info] In DIR: %s") % (evt.GetOldSelection(), evt.GetSelection(), 
                                            self.control.filename, self.control.dirname))
        self.frame.UpdateToolBar()
        evt.Skip()

    def OnPageClosing(self, evt):
        """Checks page status to flag warnings before closing"""
        self.LOG("[nb_evt] Closing Page: #%d" % self.GetSelection())
        pg = self.GetCurrentPage()
        if len(pg.GetFileName()) > 1:
            self.DocMgr.AddRecord([pg.GetFileName(), pg.GetCurrentPos()])
        evt.Skip()

    def OnPageClosed(self, evt):
        """Handles Paged Closed Event"""
        self.LOG("[nb_evt] Closed Page: #%d" % self.GetSelection())
        # wxMAC Bug? 
        # Make sure tab area is refreshed mostly for when all pages have been
        # closed to make sure that the last tab is removed from the view after
        # deletion.
        self.Update()
        self.Refresh()
        evt.Skip()
    #---- End Event Handlers ----#

    def CloseAllPages(self):
        """Closes all open pages"""
        for page in range(self.GetPageCount()):
            result = self.ClosePage()
            if result == wx.ID_CANCEL:
                break
            
    def ClosePage(self):
        """Closes Currently Selected Page"""
        self.GoCurrentPage()
        pg_num = self.GetSelection()
        result = wx.ID_OK
        try:
            act = self.control.GetModify()
        except AttributeError:
            act = False

        if act:
            result = self.frame.ModifySave()
            if result != wx.ID_CANCEL:
                self.DeletePage(pg_num)
                self.GoCurrentPage()
            else:
                pass
        else:
            self.DeletePage(pg_num)
            self.GoCurrentPage()

        # TODO this causes some flashing
        if not self.GetPageCount() and not wx.GetApp().GetMainWindow().IsExiting():
            self.NewPage()
        return result

    def SetPageImage(self, pg_num, lang_id):
        """Sets the page image by querying the ArtProvider based
        on the language id associated with the type of open document.
        Any unknown filetypes are associated with the plaintext page
        image.

        """
        il = self.GetImageList()
        if not self._index.has_key(lang_id):
            bmp = wx.ArtProvider.GetBitmap(lang_id, wx.ART_MENU)
            if bmp.IsNull():
                self._index.setdefault(lang_id, self._index[synglob.ID_LANG_TXT])
            else:
                self._index[lang_id] = il.Add(wx.ArtProvider.GetBitmap(lang_id, wx.ART_MENU))
        FNB.FlatNotebook.SetPageImage(self, pg_num, self._index[lang_id])

    def UpdatePageImage(self):
        """Updates the page tab image"""
        pg_num = self.GetSelection()
        ftype = self.control.filename.split(".")
        ftype = ftype[-1].upper()
        self.LOG("[nb_info] Updating Page Image: Page %d" % pg_num)
        self.SetPageImage(pg_num, str(self.control.lang_id))

    def OnUpdatePageText(self, evt):
        """Update the title text of the current page"""
        pg_num = self.GetSelection()
        if isinstance(self.control, ed_stc.EDSTC):
            title = self.control.filename
            if title == wx.EmptyString:
                title = self.GetPageText(pg_num)
            if self.control.GetModify():
                title = u"*" + title
            wx.CallAfter(self.SetPageText, pg_num, title)
            
    def UpdateTextControls(self):
        """Updates all text controls to use any new settings that have
        been changed since initialization.

        """
        for control in self.GetTextControls():
            control.UpdateAllStyles()
            control.Configure()

#---- End Function Definitions ----#

