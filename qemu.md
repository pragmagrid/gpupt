### QEMU notes 

Enabled features and how they are expressed in XML

#### kvm=off option to the -cpu command

QEMU 2.1 added support for the kvm=off option to the -cpu command,
allowing the KVM hypervisor signature to be hidden from the guest.
This enables disabling of some paravirualization features in the
guest as well as allowing certain drivers which test for the
hypervisor to load.  Domain XML syntax is as follows:

```xml
<domain type='kvm'>
  ...
  <features>
    ...
    <kvm>
      <hidden state='on'/>
    </kvm>
  </features>
```

#### CPU mode for host-passthrough syntax

Syntax for cpu mode has to be specific when using domain type `qemu`


VM start fails with an error 

```bash
unsupported configuration: CPU mode 'host-passthrough' is only supported with kvm
<domain type='qemu' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
```

when cpu mode is specified as :

```xml
<cpu mode='host-passthrough'></cpu>
```
Have to specify as

```xml
<cpu>
  <mode>host-passthrough</mode>
</cpu>

```

#### Fix for rombar errors

VM start fails with error

```bash
pci-assign: Cannot read from host /sys/bus/pci/devices/0000:02:00.0/rom
Device option ROM contents are probably invalid (check dmesg).
Skip option ROM probe with rombar=0, or load from file with romfile=

To fix add in xml file

```xml
<hostdev ...>
  ...
  <rom bar='off'/>
</hostdev>
```
