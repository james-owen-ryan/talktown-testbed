from setuptools import setup
import py2exe
import os
import glob

def find_data_files(source,target,patterns):
  """Locates the specified data-files and returns the matches
  in a data_files compatible format.
  source is the root of the source data tree.
    Use '' or '.' for current directory.
  target is the root of the target data tree.
    Use '' or '.' for the distribution directory.
  patterns is a sequence of glob-patterns for the
    files you want to copy.
  """
  if glob.has_magic(source) or glob.has_magic(target):
    raise ValueError("Magic not allowed in src, target")
  ret = {}
  for pattern in patterns:
    pattern = os.path.join(source,pattern)
    for filename in glob.glob(pattern):
      if os.path.isfile(filename):
        targetpath = os.path.join(target,os.path.relpath(filename,source))
        path = os.path.dirname(targetpath)
        ret.setdefault(path,[]).append(filename)
  return sorted(ret.items())

def get_cefpython_path():
  import cefpython3 as cefpython

  path = os.path.dirname(cefpython.__file__)
  return "%s%s" % (path, os.sep)

def get_data_files():
  cefp = get_cefpython_path()
  cefdeps= [('', [
    '%s/cefclient.exe' % cefp,
    '%s/subprocess.exe' % cefp,
    '%s/icudt.dll' % cefp,
    '%s/d3dcompiler_43.dll' % cefp,
    '%s/d3dcompiler_46.dll' % cefp,
    '%s/libcef.dll' % cefp,
    '%s/cef.pak' % cefp,
    '%s/devtools_resources.pak' % cefp,
    '%s/ffmpegsumo.dll' % cefp,
    '%s/libEGL.dll' % cefp,
    '%s/libGLESv2.dll' % cefp,]),
    ('locales', ['%s/locales/en-US.pak' % cefp]),
  ]
  data_files = cefdeps + find_data_files(os.getcwd(),'',[
  'content/*','corpora/*','js/*','templates/*',
  'american_names_by_decade_with_fitted_probability_distributions.dat',
  'sources.txt','README.md'])
  return data_files

setup(
  data_files = get_data_files(),
  console=['browser.py','ceftt.py','server.py'],
  options={
    "py2exe": {
       "packages":['jinja2'],
       "includes": ['eventlet.queue','engineio.async_eventlet', 'cefpython3.cefpython_py27', 'server','browser']
	}
  }
)