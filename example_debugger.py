import rivr

def view(request):
    raise Exception, "Debugger example"

if __name__ == '__main__':
    rivr.serve(rivr.DebugMiddleware(view))
