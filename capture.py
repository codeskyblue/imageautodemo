# coding: utf-8
#

import os
import sys
import subprocess
import uiautomator2 as u2
import clipboard


if len(sys.argv) <= 1:
    print("Usage: PROGRAM <output-filename>")
    sys.exit(1)

filename = sys.argv[1]
_, ext = os.path.splitext(filename)
if ext not in ['.jpg', '.png']:
    filename = filename + ".jpg"
print("Filename: ", filename)

d = u2.connect("bf755cab")
d.session().screenshot().save(filename)
gen_code = 't.click("{}")'.format(filename)
clipboard.copy(gen_code)
print("Copy '{}' to clipboard".format(gen_code))
subprocess.call(["open", filename])  # 打开截图
