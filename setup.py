import sys, os, shutil
from distutils.core import setup, Extension


shutil.copyfile("Framinator.py", "Framinator/Framinator")

setup  (name        = 'Framinator',
        version     = '0.1',
        description = 'A MITM tool that steals login credentials via script injection',
        author = 'Raul Gonzalez',
        author_email = 'graulito@hushmail.com',
        license = 'GPL',
        packages  = ["Framinator"],
        package_dir = {'Framinator' : 'Framinator'},
        scripts = ['Framinator/Framinator'],
        data_files = [('/Framinator', ['README', 'COPYING'])],
       )

print "Cleaning up..."
try:
    removeall("build/")
    os.rmdir("build/")
except:
    pass

try:
    os.remove("Framinator/Framinator")
except:
    pass

def capture(cmd):
    return os.popen(cmd).read().strip()

def removeall(path):
	if not os.path.isdir(path):
		return

	files=os.listdir(path)

	for x in files:
		fullpath=os.path.join(path, x)
		if os.path.isfile(fullpath):
			f=os.remove
			rmgeneric(fullpath, f)
		elif os.path.isdir(fullpath):
			removeall(fullpath)
			f=os.rmdir
			rmgeneric(fullpath, f)

def rmgeneric(path, __func__):
	try:
		__func__(path)
	except OSError, (errno, strerror):
		pass
