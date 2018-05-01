"""
hjcOutputFile -- OutputFile class for Hack Jack compiler
"""

class OutputFile(object):
    def __init__(self, outputName, xml=None):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.xml = xml
        self.file = open(outputName, 'w')
        if (self.xml):
            self.file.write('<'+self.xml+'>\n')


    def Close(self):
        """
        Write the epilog and close the file.
        """
        if (self.xml):
            self.file.write('</'+self.xml+'>\n')
        self.file.close()


    def Write(self, string):
        self.file.write(string)
        

    def WriteLine(self, string):
        self.file.write(string + '\n')


    def WriteXml(self, tag, value):
        self.file.write('<'+tag+'> ')
        self.file.write(self._XmlEsc(value))
        self.file.write(' </'+tag+'>\n')


    def _XmlEsc(self, line):
        line = line.replace('&', '&amp;')
        line = line.replace('<', '&lt;')
        line = line.replace('>', '&gt;')
        line = line.replace('"', '&quot;')
        return line
