python3-filelock
================

Python module for very simple flock-based file locking.

Features
--------
* Uses Python's ```with``` syntax.
* Doesn't complain if the lock file already exists but is stale.
* Cleans up the lock file after itself.
* Supports a timeout.

Example
-------
```python
import fbfilelock

with fbfilelock.FileLock("/tmp/foolock.txt", 'r', encoding='UTF-8') as f:
   # Do something.
   pass

# Raises an IOError in 3 seconds if unable to acquire the lock.
with fbfilelock.FileLock("/tmp/foolock.txt", 'r', encoding='UTF-8', timeout=3, delay=0.5) as f:
   # Do something.
   pass
```

BUGS
----
Unknown.

Contributing
------------
Contributions welcome!
