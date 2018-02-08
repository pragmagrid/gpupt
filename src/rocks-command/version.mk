NAME    = rocks-command-gpupt
RELEASE = 0

RPM.FILES = \
$(PY.ROCKS)/*egg-info \n\
$(PY.ROCKS)/rocks/commands/report/host/vm/config/* \n\
$(PY.ROCKS)/rocks/commands/report/host/gpu \n\
$(PY.ROCKS)/rocks/commands/remove/host/gpu \n\
$(PY.ROCKS)/rocks/commands/set/host/gpu \n\
$(PY.ROCKS)/rocks/commands/dump/host/gpu \n\
$(PY.ROCKS)/rocks/commands/add/host/gpu \n\
$(PY.ROCKS)/rocks/commands/list/host/gpu \n\
$(PKGROOT)/bin/*
