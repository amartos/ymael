# coding: utf-8
# This is a workaround for subprocess calls in pyinstaller --noconsole
# environment, taken from
# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
# This code is under GPLv2 or greater, see
# https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt

import subprocess
import os, os.path
import sys

# Create a set of arguments which make a ``subprocess.Popen`` (and
# variants) call work with or without Pyinstaller, ``--noconsole`` or
# not, on Windows and Linux. Typical use::
#
#   subprocess.call(['program_to_run', 'arg_1'], **subprocess_args())
#
# When calling ``check_output``::
#
#   subprocess.check_output(['program_to_run', 'arg_1'],
#                           **subprocess_args(False))
def subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret

# A simple test routine. Compare this output when run by Python, Pyinstaller,
# and Pyinstaller ``--noconsole``.
if __name__ == '__main__':
    # Save the output from invoking Python to a text file. This is the only
    # option when running with ``--noconsole``.
    with open('out.txt', 'w') as f:
        try:
            txt = subprocess.check_output(['python', '--help'],
                                          **subprocess_args(False))
            f.write(txt)
        except OSError as e:
            f.write('Failed: ' + str(e))