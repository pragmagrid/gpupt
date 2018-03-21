PKGROOT = /usr/local
NAME    = gpupt-qemu
ARCHIVENAME = qemu
VERSION = 2.10.1
RELEASE = 0
TARBALL_POSTFIX = tar.xz

RPM.FILES = \
/usr/local/bin/* \n\
/usr/local/libexec/qemu-bridge-helper \n\
/usr/local/share/locale/* \n\
/usr/local/share/qemu/* \n\
/usr/local/var \n\
/usr/local/var/run
