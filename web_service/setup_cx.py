from cx_Freeze import setup, Executable
productName = "dep_rest_server"

build_exe_options = {"packages": ["requests",
                                  "os",
                                  "sys",
                                  "imp",
                                  "multiprocessing",
                                  "signal",
                                  "flask",
                                  "OpenSSL",
                                  "urllib2",
                                  "paramiko",
                                  "lxml",
                                  "urlparse",
                                  "time",
                                  "crypt",
                                  "hmac",
                                  "random",
                                  "string",
                                  "datetime",
                                  "sqlalchemy",
                                  "sqlite3"],
                     "includes" : "atexit"}

base = None
exe = Executable("dep_rest_server.py")

setup(
      name="dep_rest_server",
      version="0.1",
      author="oldbay",
      description="Deploy REST Server",
      long_description="""
      Debian deploy REST server
      """,
      options = {"build_exe": build_exe_options},
      executables=[exe])
