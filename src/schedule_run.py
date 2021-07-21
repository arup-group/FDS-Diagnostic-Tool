import subprocess
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
p = subprocess.Popen(os.path.join(dir_path, 'start.bat'))
