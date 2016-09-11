from cx_Freeze import setup, Executable

productName = "dep_rest_cl"

build_exe_options = {"packages": ["requests",
                                  "os",
                                  "sys",
                                  "imp",
                                  "opster",
                                  "cPickle",
                                  "locale",
                                  "gettext"],
                     "includes" : "atexit"}

base = None
exe = Executable("dep_rest_cl.py")

setup(
      name="dep_rest_cl",
      version="0.1",
      author="oldbay",
      description="Deploy RESP Client",
      long_description="""
      Client for Debian deploy server
      """,
      options = {"build_exe": build_exe_options},
      executables=[exe])
