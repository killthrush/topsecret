import sys
import getopt
from data_import.process import Processor
from web.api import app

if __name__ == '__main__':
    opts = getopt.getopt(sys.argv[1:], 'rp')
    if ('-p', '') in opts[0]:
        processor = Processor()
        processor.process_all()
        processor.print_stats()
    if ('-r', '') in opts[0]:
        app.run('localhost', 8080, debug=True)