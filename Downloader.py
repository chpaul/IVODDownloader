# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from PyQt4.QtGui import *
import iVodMain
def main():    
    app = QApplication(sys.argv)
    widget = iVodMain.iVodMain()    
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()