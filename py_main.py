import sysconfig
from distutils.sysconfig import get_python_inc
print(sysconfig.get_makefile_filename())
print("="*80)
print(sysconfig.get_config_var('PY_CFLAGS'))
print("="*80)
print(sysconfig.get_config_var('PY_LDFLAGS'))
print("="*80)
print(sysconfig.get_config_var('LIBS'))
print("="*80)
print(sysconfig.get_config_var('LINKFORSHARED'))
print("="*80)
print(get_python_inc())
