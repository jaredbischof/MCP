class nagasaki(object):
    actions = "start, stop"
    def start():
        print "Starting nagasaki pipeline:"
        sout, serr = run_cmd("/usr/local/bin/qstart batch")
        print "nagasaki pipeline started!"
        return 0
    def stop():
        print "Stopping nagasaki pipeline:"
        sout, serr = run_cmd("/usr/local/bin/qstop batch")
        print "nagasaki pipeline stopped!"
        return 0
