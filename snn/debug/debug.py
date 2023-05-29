class Debug:
    DEBUG_VERBOSE = 0
    DEBUG_INFO = 1
    DEBUG_WARN = 2
    DEBUG_ERROR = 3

    debug_level = DEBUG_ERROR

    @staticmethod
    def log(msg, level):
        if level >= Debug.debug_level:
            print(msg)