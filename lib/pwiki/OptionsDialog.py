import re

import wx, wx.xrc
# from wxPython.wx import *
# import wxPython.xrc as xrc

from wxHelper import *

from StringOps import uniToGui, guiToUni, htmlColorToRgbTuple,\
        rgbToHtmlColor

from AdditionalDialogs import DateformatDialog, FontFaceDialog

import WikiHtmlView


class PredefinedOptionsPanel(wx.Panel):
    def __init__(self, parent, resName):
        p = wx.PrePanel()
        self.PostCreate(p)
#         self.optionsDlg = optionsDlg
        res = wx.xrc.XmlResource.Get()

        res.LoadOnPanel(self, parent, resName)
        
    def setVisible(self, vis):
        return True

    def checkOk(self):
        return True

    def handleOk(self):
        pass


class EmptyOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

    def setVisible(self, vis):
        return True

    def checkOk(self):
        return True

    def handleOk(self):
        pass



class OptionsDialog(wx.Dialog):
    # List of tuples (<configuration file entry>, <gui control name>, <type>)
    # Supported types: b: boolean checkbox, i0+: nonnegative integer, t: text
    #    tre: regular expression,  f0+: nonegative float, seli: integer position
    #    of a selection in dropdown list, selt: Chosen text in dropdown list
    #    color0: HTML color code or empty

    OPTION_TO_CONTROL = (
            # application-wide options
            
            ("auto_save", "cbAutoSave", "b"),
            ("auto_save_delay_key_pressed", "tfAutoSaveDelayKeyPressed", "i0+"),
            ("auto_save_delay_dirty", "tfAutoSaveDelayDirty", "i0+"),

            ("showontray", "cbShowOnTray", "b"),
            ("minimize_on_closeButton", "cbMinimizeOnCloseButton", "b"),

            ("hideundefined", "cbHideUndefinedWords", "b"),
            ("pagestatus_timeformat", "tfPageStatusTimeFormat", "t"),
            ("log_window_autoshow", "cbLogWindowAutoShow", "b"),
            ("log_window_autohide", "cbLogWindowAutoHide", "b"),
            ("clipboardCatcher_suffix", "tfClipboardCatcherSuffix", "t"),
            ("clipboardCatcher_filterDouble", "cbClipboardCatcherFilterDouble",
                    "b"),
            ("single_process", "cbSingleProcess", "b"),

            ("process_autogenerated_areas", "cbProcessAutoGenerated", "b"),
            ("insertions_allow_eval", "cbInsertionsAllowEval", "b"),
            ("script_security_level", "chScriptSecurityLevel", "seli"),

            ("collation_order", "chCollationOrder", "selt"),
            ("collation_uppercaseFirst", "cbCollationUppercaseFirst", "b"),

            ("mainTree_position", "chMainTreePosition", "seli"),
            ("viewsTree_position", "chViewsTreePosition", "seli"),

            ("tree_auto_follow", "cbTreeAutoFollow", "b"),
            ("tree_update_after_save", "cbTreeUpdateAfterSave", "b"),
            ("tree_no_cycles", "cbTreeNoCycles", "b"),
            
            ("start_browser_after_export", "cbStartBrowserAfterExport", "b"),
            ("facename_html_preview", "tfFacenameHtmlPreview", "t"),
            ("html_preview_proppattern_is_excluding",
                    "cbHtmlPreviewProppatternIsExcluding", "b"),
            ("html_preview_proppattern", "tfHtmlPreviewProppattern", "tre"),
            ("html_export_proppattern_is_excluding",
                    "cbHtmlExportProppatternIsExcluding", "b"),
            ("html_export_proppattern", "tfHtmlExportProppattern", "tre"),
            ("html_preview_pics_as_links", "cbHtmlPreviewPicsAsLinks", "b"),
            ("html_export_pics_as_links", "cbHtmlExportPicsAsLinks", "b"),
            ("html_preview_renderer", "chHtmlPreviewRenderer", "seli"),
            ("export_table_of_contents", "chTableOfContents", "seli"),
            
            ("html_body_link", "tfHtmlLinkColor", "color0"),
            ("html_body_alink", "tfHtmlALinkColor", "color0"),
            ("html_body_vlink", "tfHtmlVLinkColor", "color0"),
            ("html_body_text", "tfHtmlTextColor", "color0"),
            ("html_body_bgcolor", "tfHtmlBgColor", "color0"),
            ("html_body_background", "tfHtmlBgImage", "t"),
            ("html_header_doctype", "tfHtmlDocType", "t"),

            ("editor_plaintext_color", "tfEditorPlaintextColor", "color0"),
            ("editor_link_color", "tfEditorLinkColor", "color0"),
            ("editor_attribute_color", "tfEditorAttributeColor", "color0"),
            ("editor_bg_color", "tfEditorBgColor", "color0"),
            ("editor_selection_fg_color", "tfEditorSelectionFgColor", "color0"),
            ("editor_selection_bg_color", "tfEditorSelectionBgColor", "color0"),
            ("editor_caret_color", "tfEditorCaretColor", "color0"),
            ("sync_highlight_byte_limit", "tfSyncHighlightingByteLimit", "i0+"),
            ("async_highlight_delay", "tfAsyncHighlightingDelay", "f0+"),
            ("editor_autoUnbullets", "cbAutoUnbullets", "b"),

            ("mouse_middleButton_withoutCtrl", "chMouseMiddleButtonWithoutCtrl", "seli"),
            ("mouse_middleButton_withCtrl", "chMouseMiddleButtonWithCtrl", "seli"),

            ("search_wiki_context_before", "tfWwSearchContextBefore", "i0+"),
            ("search_wiki_context_after", "tfWwSearchContextAfter", "i0+"),
            ("search_wiki_count_occurrences", "cbWwSearchCountOccurrences", "b"),
            ("incSearch_autoOffDelay", "tfIncSearchAutoOffDelay", "i0+"),

            # wiki specific options

            ("footnotes_as_wikiwords", "cbFootnotesAsWws", "b"),
            ("first_wiki_word", "tfFirstWikiWord", "t"),

            ("wikiPageTitlePrefix", "tfWikiPageTitlePrefix", "t"),
            ("export_default_dir", "tfExportDefaultDir", "t"),

            ("fileStorage_identity_modDateMustMatch", "cbFsModDateMustMatch", "b"),
            ("fileStorage_identity_filenameMustMatch", "cbFsFilenameMustMatch", "b"),
            ("fileStorage_identity_modDateIsEnough", "cbFsModDateIsEnough", "b")
    )

    DEFAULT_PANEL_LIST = (
            ("OptionsPageApplication", u"Application"),    
            ("OptionsPageSecurity", u"  Security"),
            ("OptionsPageTree", u"  Tree"),
            ("OptionsPageHtml", u"  HTML preview/export"),
            ("OptionsPageHtmlHeader", u"    HTML header"),
            ("OptionsPageAutosave", u"  Autosave"),
            ("OptionsPageEditor", u"  Editor"),
            ("OptionsPageMouse", u"  Mouse"),
            ("OptionsPageSearching", u"  Searching"),            
            ("OptionsPageCurrentWiki", u"Current Wiki")
    )

    def __init__(self, pWiki, ID, title="Options",
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.NO_3D):
        d = wx.PreDialog()
        self.PostCreate(d)
        
        self.pWiki = pWiki
        res = wx.xrc.XmlResource.Get()
        res.LoadOnDialog(self, self.pWiki, "OptionsDialog")

        self.ctrls = XrcControls(self)

        self.emptyPanel = None

        self.panelList = []
        self.ctrls.lbPages.Clear()
        
        
        mainsizer = LayerSizer()  # wx.BoxSizer(wx.VERTICAL)
        
        for pn, pt in wx.GetApp().getOptionsDlgPanelList():
            if isinstance(pn, basestring):
                if pn != "":
                    panel = PredefinedOptionsPanel(self.ctrls.panelPages, pn)
#                     panel.Fit()
                else:
                    if self.emptyPanel is None:
                        # Necessary to avoid a crash        
                        self.emptyPanel = EmptyOptionsPanel(self.ctrls.panelPages)
#                         self.emptyPanel.Fit()
                    panel = self.emptyPanel
            else:
                # Factory function or class
                panel = pn(self.ctrls.panelPages, self, wx.GetApp())

            self.panelList.append(panel)
            self.ctrls.lbPages.Append(pt)
            mainsizer.Add(panel)
        
        
        self.ctrls.panelPages.SetSizer(mainsizer)
        self.ctrls.panelPages.SetMinSize(mainsizer.GetMinSize())


#         minw = 0
#         minh = 0        
#         for pn, pt in wxGetApp().getOptionsDlgPanelList():
#             if isinstance(pn, basestring):
#                 if pn != "":
#                     panel = PredefinedOptionsPanel(self.ctrls.panelPages, pn)
#     #                 res.LoadPanel(self.ctrls.panelPages, pn)
#                 else:
#                     if self.emptyPanel is None:
#                         # Necessary to avoid a crash        
#                         self.emptyPanel = EmptyOptionsPanel(self.ctrls.panelPages)
#                         self.emptyPanel.Fit()
#                     panel = self.emptyPanel
#             else:
#                 # Factory function or class
#                 panel = pn(self.ctrls.panelPages, self, wxGetApp())
# 
#             self.panelList.append(panel)
#             self.ctrls.lbPages.Append(pt)
#             mins = panel.GetSize()
#             minw = max(minw, mins.width)
#             minh = max(minh, mins.height)
# 
#         self.ctrls.panelPages.SetMinSize(wxSize(minw + 10, minh + 10))


        self.ctrls.panelPages.Fit()
        self.Fit()

        self.ctrls.btnOk.SetId(wx.ID_OK)
        self.ctrls.btnCancel.SetId(wx.ID_CANCEL)

        # Transfer options to dialog
        for o, c, t in self.OPTION_TO_CONTROL:
            if t == "b":   # boolean field = checkbox
                self.ctrls[c].SetValue(
                        self.pWiki.getConfig().getboolean("main", o))
            elif t in ("t", "tre", "i0+", "f0+", "color0"):  # text field or regular expression field
                self.ctrls[c].SetValue(
                        uniToGui(self.pWiki.getConfig().get("main", o)) )
            elif t == "seli":   # Selection -> transfer index
                self.ctrls[c].SetSelection(
                        self.pWiki.getConfig().getint("main", o))
            elif t == "selt":   # Selection -> transfer content string
                self.ctrls[c].SetStringSelection(
                        uniToGui(self.pWiki.getConfig().get("main", o)) )

        # Options with special treatment
        self.ctrls.cbLowResources.SetValue(
                self.pWiki.getConfig().getint("main", "lowresources") != 0)

        self.ctrls.cbNewWindowWikiUrl.SetValue(
                self.pWiki.getConfig().getint("main",
                "new_window_on_follow_wiki_url") != 0)

        self.ctrls.chHtmlPreviewRenderer.Enable(
                WikiHtmlView.WikiHtmlViewIE is not None)

        self.activePageIndex = -1
        for panel in self.panelList:
            panel.Show(False)
            panel.Enable(False)

        self.ctrls.lbPages.SetSelection(0)
        self._refreshForPage()

        wx.EVT_LISTBOX(self, GUI_ID.lbPages, self.OnLbPages)

        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOk)
        wx.EVT_BUTTON(self, GUI_ID.btnSelectFaceHtmlPrev, self.OnSelectFaceHtmlPrev)

        wx.EVT_BUTTON(self, GUI_ID.btnSelectHtmlLinkColor,
                lambda evt: self.selectColor(self.ctrls.tfHtmlLinkColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectHtmlALinkColor,
                lambda evt: self.selectColor(self.ctrls.tfHtmlALinkColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectHtmlVLinkColor,
                lambda evt: self.selectColor(self.ctrls.tfHtmlVLinkColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectHtmlTextColor,
                lambda evt: self.selectColor(self.ctrls.tfHtmlTextColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectHtmlBgColor,
                lambda evt: self.selectColor(self.ctrls.tfHtmlBgColor))

        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorPlaintextColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorPlaintextColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorLinkColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorLinkColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorAttributeColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorAttributeColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorBgColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorBgColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorSelectionFgColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorSelectionFgColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorSelectionBgColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorSelectionBgColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectEditorCaretColor,
                lambda evt: self.selectColor(self.ctrls.tfEditorCaretColor))
        wx.EVT_BUTTON(self, GUI_ID.btnSelectExportDefaultDir,
                lambda evt: self.selectDirectory(self.ctrls.tfExportDefaultDir))


        wx.EVT_BUTTON(self, GUI_ID.btnSelectPageStatusTimeFormat,
                self.OnSelectPageStatusTimeFormat)


    def _refreshForPage(self):
        if self.activePageIndex > -1:
            panel = self.panelList[self.activePageIndex]
            if not panel.setVisible(False):
                self.ctrls.lbPages.SetSelection(self.activePageIndex)
                return
            
            panel.Show(False)
            panel.Enable(False)

        self.activePageIndex = self.ctrls.lbPages.GetSelection()

        panel = self.panelList[self.activePageIndex]
        panel.setVisible(True)  # Not checking return value here

        # Enable appropriate addit. options panel
        panel.Enable(True)
        panel.Show(True)


    def OnLbPages(self, evt):
        self._refreshForPage()
        evt.Skip()


    def OnOk(self, evt):
        fieldsValid = True
        # First check validity of field contents
        for o, c, t in self.OPTION_TO_CONTROL:
            if t == "tre":
                # Regular expression field, test if re is valid
                try:
                    rexp = guiToUni(self.ctrls[c].GetValue())
                    re.compile(rexp, re.DOTALL | re.UNICODE | re.MULTILINE)
                    self.ctrls[c].SetBackgroundColour(wx.WHITE)
                except:   # TODO Specific exception
                    fieldsValid = False
                    self.ctrls[c].SetBackgroundColour(wx.RED)
            elif t == "i0+":
                # Nonnegative integer field
                try:
                    val = int(guiToUni(self.ctrls[c].GetValue()))
                    if val < 0:
                        raise ValueError
                    self.ctrls[c].SetBackgroundColour(wx.WHITE)
                except ValueError:
                    fieldsValid = False
                    self.ctrls[c].SetBackgroundColour(wx.RED)
            elif t == "f0+":
                # Nonnegative float field
                try:
                    val = float(guiToUni(self.ctrls[c].GetValue()))
                    if val < 0:
                        raise ValueError
                    self.ctrls[c].SetBackgroundColour(wx.WHITE)
                except ValueError:
                    fieldsValid = False
                    self.ctrls[c].SetBackgroundColour(wx.RED)
            elif t == "color0":
                # HTML Color field or empty field
                val = guiToUni(self.ctrls[c].GetValue())
                rgb = htmlColorToRgbTuple(val)
                
                if val != "" and rgb is None:
                    self.ctrls[c].SetBackgroundColour(wx.RED)
                    fieldsValid = False
                else:
                    self.ctrls[c].SetBackgroundColour(wx.WHITE)

        if not fieldsValid:
            self.Refresh()
            return
            
        # Check each panel
        for i, panel in enumerate(self.panelList):
            if not panel.checkOk():
                # One panel has a problem (probably invalid data)
                self.ctrls.lbPages.SetSelection(i)
                self._refreshForPage()
                return

        # Then transfer options from dialog to config file
        for o, c, t in self.OPTION_TO_CONTROL:
            # TODO Handle unicode text controls
            if t == "b":
                self.pWiki.getConfig().set("main", o, repr(self.ctrls[c].GetValue()))
            elif t in ("t", "tre", "i0+", "f0+", "color0"):
                self.pWiki.getConfig().set(
                        "main", o, guiToUni(self.ctrls[c].GetValue()) )
            elif t == "seli":   # Selection -> transfer index
                self.pWiki.getConfig().set(
                        "main", o, unicode(self.ctrls[c].GetSelection()) )
            elif t == "selt":   # Selection -> transfer content string
                self.pWiki.getConfig().set(
                        "main", o, guiToUni(self.ctrls[c].GetStringSelection()) )

        # Options with special treatment
        if self.ctrls.cbLowResources.GetValue():
            self.pWiki.getConfig().set("main", "lowresources", "1")
        else:
            self.pWiki.getConfig().set("main", "lowresources", "0")

        if self.ctrls.cbNewWindowWikiUrl.GetValue():
            self.pWiki.getConfig().set("main", "new_window_on_follow_wiki_url", "1")
        else:
            self.pWiki.getConfig().set("main", "new_window_on_follow_wiki_url", "0")

        # Ok for each panel
        for panel in self.panelList:
            panel.handleOk()

        self.pWiki.getConfig().informChanged()

        evt.Skip()


    def OnSelectFaceHtmlPrev(self, evt):
        dlg = FontFaceDialog(self, -1, self.ctrls.tfFacenameHtmlPreview.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrls.tfFacenameHtmlPreview.SetValue(dlg.GetValue())
        dlg.Destroy()
        
    def OnSelectPageStatusTimeFormat(self, evt):
        dlg = DateformatDialog(self, -1, self.pWiki, 
                deffmt=self.ctrls.tfPageStatusTimeFormat.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrls.tfPageStatusTimeFormat.SetValue(dlg.GetValue())
        dlg.Destroy()


    def selectColor(self, tfield):
        rgb = htmlColorToRgbTuple(tfield.GetValue())
        if rgb is None:
            rgb = 0, 0, 0

        color = wx.Colour(*rgb)
        colordata = wx.ColourData()
        colordata.SetColour(color)

        dlg = wx.ColourDialog(self, colordata)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                color = dlg.GetColourData().GetColour()
                if color.Ok():
                    tfield.SetValue(
                            rgbToHtmlColor(color.Red(), color.Green(),
                            color.Blue()))
        finally:
            dlg.Destroy()


    def selectDirectory(self, tfield):        
        seldir = wx.DirSelector(u"Select Directory",
                tfield.GetValue(),
                style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON, parent=self)
            
        if seldir:
            tfield.SetValue(seldir)
