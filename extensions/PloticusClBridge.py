import os, os.path

import wx

from pwiki.TempFileSet import createTempFile
from pwiki.StringOps import mbcsEnc

WIKIDPAD_PLUGIN = (("InsertionByKey", 1), ("Options", 1))

def describeInsertionKeys(ver, app):
    """
    API function for "InsertionByKey" plugins
    Returns a sequence of tuples describing the supported
    insertion keys. Each tuple has the form (insKey, exportTypes, handlerFactory)
    where insKey is the insertion key handled, exportTypes is a sequence of
    strings describing the supported export types and handlerFactory is
    a factory function (normally a class) taking the wxApp object as
    parameter and returning a handler object fulfilling the protocol
    for "insertion by key" (see EqnHandler as example).

    ver -- API version (can only be 1 currently)
    app -- wxApp object
    """
    return (
            (u"ploticus", ("html_single", "html_preview", "html_multi"), PltHandler),
            )


class PltHandler:
    """
    Base class fulfilling the "insertion by key" protocol.
    """
    def __init__(self, app):
        self.app = app
        self.extAppExe = None
        
    def taskStart(self, exporter, exportType):
        """
        This is called before any call to createContent() during an
        export task.
        An export task can be a single HTML page for
        preview or a single page or a set of pages for export.
        exporter -- Exporter object calling the handler
        exportType -- string describing the export type
        
        Calls to createContent() will only happen after a 
        call to taskStart() and before the call to taskEnd()
        """
        # Find Ploticus executable by configuration setting
        self.extAppExe = self.app.getGlobalConfig().get("main",
                "plugin_ploticus_exePath", "")
        
    def taskEnd(self):
        """
        Called after export task ended and after the last call to
        createContent().
        """
        pass


    def createContent(self, exporter, exportType, insToken):
        """
        Handle an insertion and create the appropriate content.

        exporter -- Exporter object calling the handler
        exportType -- string describing the export type
        insToken -- insertion token to create content for (see also 
                PageAst.Insertion)

        An insertion token has the following member variables:
            key: insertion key (unistring)
            value: value of an insertion (unistring)
            appendices: sequence of strings with the appendices

        Meaning and type of return value is solely defined by the type
        of the calling exporter.
        
        For HtmlXmlExporter a unistring is returned with the HTML code
        to insert instead of the insertion.        
        """
        # Retrieve quoted content of the insertion
        bstr = mbcsEnc(insToken.value, "replace")[0]

        if not bstr:
            # Nothing in, nothing out
            return u""
        
        if self.extAppExe == "":
            # No path to MimeTeX executable -> show message
            return "<pre>[Please set path to Ploticus executable]</pre>"

        # Get exporters temporary file set (manages creation and deletion of
        # temporary files)
        tfs = exporter.getTempFileSet()

        dstFullPath = tfs.createTempFile("", ".gif", relativeTo="")
        url = tfs.getRelativeUrl(None, dstFullPath)
        
        baseDir = os.path.dirname(exporter.getMainControl().getWikiConfigPath())

        # Store token content in a temporary file
        srcfilepath = createTempFile(bstr, ".plt")
        try:
            # Run external application
            childIn, childOut, childErr = os.popen3(r'%s -dir "%s" "%s" -gif -o "%s"' % 
                    (self.extAppExe, baseDir, srcfilepath, dstFullPath), "b")

            errResponse = childErr.read()
        finally:
            os.unlink(srcfilepath)
            
        if errResponse != "":
            return "<pre>[Ploticus error: %s]</pre>" % errResponse

        # Return appropriate HTML code for the image
        if exportType == "html_preview":
            # Workaround for internal HTML renderer
            return u'<img src="%s" border="0" align="bottom" />&nbsp;' % url
        else:
            return u'<img src="%s" border="0" align="bottom" />' % url


    def getExtraFeatures(self):
        """
        Returns a list of bytestrings describing additional features supported
        by the plugin. Currently not specified further.
        """
        return ()
        

def registerOptions(ver, app):
    """
    API function for "Options" plugins
    Register configuration options and their GUI presentation
    ver -- API version (can only be 1 currently)
    app -- wxApp object
    """
    # Register option
    app.getDefaultGlobalConfigDict()[("main", "plugin_ploticus_exePath")] = u""
    # Register panel in options dialog
    app.addOptionsDlgPanel(PloticusOptionsPanel, u"  Ploticus")


class PloticusOptionsPanel(wx.Panel):
    def __init__(self, parent, optionsDlg, app):
        """
        Called when "Options" dialog is opened to show the panel.
        Transfer here all options from the configuration file into the
        text fields, check boxes, ...
        """
        wx.Panel.__init__(self, parent)
        self.app = app
        
        pt = self.app.getGlobalConfig().get("main", "plugin_ploticus_exePath", "")
        
        self.tfPath = wx.TextCtrl(self, -1, pt)

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        inputsizer = wx.BoxSizer(wx.HORIZONTAL)
        inputsizer.Add(wx.StaticText(self, -1, "Path to Ploticus:"), 0,
                wx.ALL | wx.EXPAND, 5)
        inputsizer.Add(self.tfPath, 1, wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(inputsizer, 0, wx.EXPAND)
        
        self.SetSizer(mainsizer)
        self.Fit()

    def setVisible(self, vis):
        """
        Called when panel is shown or hidden. The actual wxWindow.Show()
        function is called automatically.
        
        If a panel is visible and becomes invisible because another panel is
        selected, the plugin can veto by returning False.
        When becoming visible, the return value is ignored.
        """
        return True

    def checkOk(self):
        """
        Called when "OK" is pressed in dialog. The plugin should check here if
        all input values are valid. If not, it should return False, then the
        Options dialog automatically shows this panel.
        
        There should be a visual indication about what is wrong (e.g. red
        background in text field). Be sure to reset the visual indication
        if field is valid again.
        """
        return True

    def handleOk(self):
        """
        This is called if checkOk() returned True for all panels. Transfer here
        all values from text fields, checkboxes, ... into the configuration
        file.
        """
        pt = self.tfPath.GetValue()
        
        self.app.getGlobalConfig().set("main", "plugin_ploticus_exePath", pt)


