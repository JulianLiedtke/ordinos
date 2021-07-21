import threading
class Print_Synch:
    #just use this for checking correctness of the implementation
    #it could heavily increase the runtime
    id = 0
    lock = threading.Lock()

    @classmethod
    def log.info(cls, s, s_id):
        #the printer needs the string s to be printed
        #s_id is a list (not allowed to change outside this method, initialized by [0])
        cls.lock.acquire()

        if s_id[0] == cls.id:
            #string s was not printed before
            cls.id += 1
            log.info(s)

        cls.lock.release()
        s_id[0] += 1
        return

    @classmethod
    def acquire(cls):
        cls.lock.acquire()

    @classmethod
    def release(cls):
        cls.lock.release()