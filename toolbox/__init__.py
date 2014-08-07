import glob
tools = []
for module_name in glob.glob("plugins/redstoner-utils.py.dir/toolbox/*.py"):
  tools.append(__import__(module_name))
