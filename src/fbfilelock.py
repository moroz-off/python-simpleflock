# -*- coding: UTF-8 -*-#
import time
import os
import fcntl
import errno
import io


class FileLockException(Exception):
    pass


class FileLock(object):
    """ A file locking mechanism that has context-manager support so
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """
    __slots__ = ('is_locked', '_fld', '_fd', '_path', '_lpath', '_mode', '_enc', '_buf', '_timeout', '_delay')

    def __init__(self, path, mode='r', encoding=None, buffering=-1, timeout=10, delay=.05):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        self.is_locked = False
        self._fld = None
        self._fd = None
        self._path = path
        self._lpath = os.path.join(os.path.dirname(path), "{}.lock".format(path))
        self._mode = mode
        self._enc = encoding
        self._buf = buffering
        self._timeout = timeout
        self._delay = delay

    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws
            an exception.
        """
        st = time.time()
        while True:
            try:
                fcntl.flock(self._fld, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, BlockingIOError, IOError) as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EEXIST:
                    raise
                if time.time() - st >= self._timeout:
                    raise FileLockException('Timeout occurred.')
                time.sleep(self._delay)
        self.is_locked = True

    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        if not self.is_locked:
            return None

        if self._fld is not None:
            fcntl.flock(self._fld, fcntl.LOCK_UN)
            os.close(self._fld)

        if self._fld is not None:
            self._fd.close()

        self._fd = None
        self._fld = None

        # Try to remove the lock file, but don't try too hard because it is
        # unnecessary. This is mostly to help the user see whether a lock
        # exists by examining the filesystem.
        try:
            os.unlink(self._lpath)
        except OSError:
            pass

        self.is_locked = False

    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        self._fld = os.open(self._lpath, os.O_CREAT)
        self._fd = io.open(self._path, mode=self._mode, encoding=self._enc, buffering=self._buf)
        if not self.is_locked:
            self.acquire()
        return self._fd

    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        if self.is_locked:
            self.release()


if __name__ == "__main__":
    print("Acquiring lock...")

    with FileLock("locktest.txt", 'w', encoding='UTF-8', timeout=2, delay=0.5) as f:
        print("Lock acquired.")
        f.write('FileLock')
        time.sleep(3)
    print("Lock released.")
