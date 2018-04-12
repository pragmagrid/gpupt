
Gpupt  Roll
==================

.. contents::

Introduction
---------------
This roll enables GPU pass-through to a guest VM. 
The roll installs rocks commands for GPU management a frontend and vm-container nodes. 

Assumptions
-------------

#. This roll assumes that GPU cards are NVIDIA cards that have Video/Audio function for each card
   which are designated by a function 0/1 respectively on the PCI bus.  For example, to list 
   nvidia devices :: 

      [root@gpu-1-6]# lspci -D -d 10de:
      0000:02:00.0 3D controller: NVIDIA Corporation GF100GL [Tesla T20 Processor] (rev a3)
      0000:02:00.1 Audio device: NVIDIA Corporation GF100 High Definition Audio Controller (rev a1)

#. This roll assumes that GPU cards for each physical host are given logical names with the prefix ``gpupci``
   The names are unique on a single host and the sequence starts with ``gpupci1``. The name is not 
   unique across different hosts. 
#. A single GPU card will be assigned to a VM host. The logical name for a GPU card on any VM is always ``gpupci``
   without indexes.  See example below for usage.
#. `Cuda roll`_ is installed on vm-containers and on the guest VMs.


Building
---------

To build the roll, execute : ::

    # make roll

A successful build will create  ``gpupt-*.x86_64*.iso`` file.

Installing
------------

To add this roll to existing cluster, execute these instructions on a Rocks frontend: ::

    # rocks add roll gpupt-*.x86_64.disk1.iso
    # rocks enable roll gpupt
    # (cd /export/rocks/install; rocks create distro)
    # rocks run roll gpupt > add-roll.sh
    # bash add-roll.sh

On the vm-container nodes (only GPU-enabled): :: 

    # yum clean all 
    # yum install rocks-command-gpupt gpupt-qemu

What is installed:
-------------------

#. QEMU emulator version 2.10.1, installed in ``/usr/local``.
   This version can parse variables that a current Centos7 suppliesd qemu v. 1.5.3 does not.

#. The following commands are enabled with the gpupt roll: :: 

     rocks add host gpu ...
     rocks dump host gpu ...
     rocks list host gpu ...
     rocks remove host gpu ...
     rocks report host gpu ...
     rocks set host gpu ...

#. A plugin ``plugin_device.py`` to manage guest VM GPU pass-through PCI addressing.
   Used by rocks command ``rocks report host vm config``. 

#. A command ``gpupci`` to manage GPU cards PCI addressing (list, detach, attach).
   This command is executed on the GPU-enabled hosts to get information (list) or to make GPU card
   available/non-available on the physical host PCI bus.  For more info use ``gpupci -h``

Prepare physical host for passthrough
--------------------------------------

The Intel VT-d extensions  provide hardware support for assigning a physical device to a guest VM. 
There are 2 parts in enabling extensions (assuming that the hardware provides a support for it).
The changes are done on the physical host that has GPU cards and will be hosting VMs. 

#. **Enable VT-D extensions in BIOS** 
   Verify if your processor supports VT-d extensions.  The extensions differ among manufactureres. 
   Consult the BIOS settings. 

#. **Activate Vt-d in the kernel**

   #. **CentOS 6**: Append the following flags to the end of the ``kernel`` line in boot.grub: :: 

        intel_iommu=on iommu=pt pci=realloc rdblacklist=nvidia

      The last flag is to disable loading of nvidia driver.  
   #. **CentOS 7**: 
 
      find the NVIDIA card PCI bus IDS ::

        [root@vm-container-0-15 ~]# lspci -nn | grep NVIDIA
        02:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP106 [GeForce GTX 1060 6GB] [10de:1c03] (rev a1)
        02:00.1 Audio device [0403]: NVIDIA Corporation GP106 High Definition Audio Controller [10de:10f1] (rev a1)
        03:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP106 [GeForce GTX 1060 6GB] [10de:1c03] (rev a1)
        03:00.1 Audio device [0403]: NVIDIA Corporation GP106 High Definition Audio Controller [10de:10f1] (rev a1)
        83:00.0 VGA compatible controller [0300]: NVIDIA Corporation GF110GL [Tesla C2050 / C2075] [10de:1096] (rev a1)
        84:00.0 3D controller [0302]: NVIDIA Corporation GK110GL [Tesla K20Xm] [10de:1021] (rev a1)

      The IDS are identified by ``[10de:...]``.
      Append the kernel command line parameters to the GRUB_CMDLINE_LINUX entry in ``/etc/default/grub``  and use IDS 
      in the pci-stub.ids variable ::
   
        intel_iommu=on iommu=pt pci=realloc rdblacklist=nvidia,nouveau pci-stub.ids=10de:1c03,10de:10f1,10de:1096,10de:1021
      
      generate new grub configuration with nvidia nouveau disabled ::

        grub2-mkconfig -o /boot/grub2/grub.cfg

      Regenerate initramfs with dracut :: 
      
        dracut --regenerate-all --force


#. Uninstall nvidia driver. This step is important otherwise
   when booting VMs later the following errors may be present in 
   /var/log/libvirt/qemu/VMNAME.log  and VM will not boot:: 

        Failed to assign device "hostdev0" : Device or resource busy
        2017-08-31T22:17:28.117713Z qemu-kvm: -device pci-assign,host=02:00.0,id=hostdev0, ...  Device 'pci-assign' could not be initialized

   To uninstall the driver :: 

     /opt/cuda/driver/uninstall-driver 
     /chkconfig --del nvidia

   Check ``/var/log/nvidia-uninstall.log`` file  for errors and reboot the host.


When the host is rebooted, check if the changes are enabled:  

**CentOS 6**: ::
     
     # cat /proc/cmdline
     ro root=UUID=575b0aac-0b20-4024-8a2d-26f8d3cc460b rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet intel_iommu=on iommu=pt pci=realloc  rdblacklist=nvidia

the output  should contain added flags

The following two commands shoudl show PCI-DMA and IOMMU ::

     # dmesg | grep -i PCI-DMA 
     PCI-DMA: Intel(R) Virtualization Technology for Directed I/O
     # grep -i IOMMU /var/log/messages 
     Aug 28 15:06:23 gpu-1-6 kernel: Command line: ro root=UUID=575b0aac-0b20-4024-8a2d-26f8d3cc460b rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet intel_iommu=on iommu=pt pci=realloc  rdblacklist=nvidia
     Aug 28 15:06:23 gpu-1-6 kernel: Kernel command line: ro root=UUID=575b0aac-0b20-4024-8a2d-26f8d3cc460b rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet intel_iommu=on iommu=pt pci=realloc  rdblacklist=nvidia
     Aug 28 15:06:23 gpu-1-6 kernel: Intel-IOMMU: enabled
     Aug 28 15:06:23 gpu-1-6 kernel: dmar: IOMMU 0: reg_base_addr fbffe000 ver 1:0 cap c90780106f0462 ecap f020fe
     Aug 28 15:06:23 gpu-1-6 kernel: IOMMU 0xfbffe000: using Queued invalidation
     Aug 28 15:06:23 gpu-1-6 kernel: IOMMU: hardware identity mapping for device 0000:00:00.0
     ...
     Aug 31 10:57:53 gpu-1-6 kernel: IOMMU: hardware identity mapping for device 0000:04:00.1
     Aug 31 10:57:53 gpu-1-6 kernel: IOMMU: Setting RMRR:
     Aug 31 10:57:53 gpu-1-6 kernel: IOMMU: Prepare 0-16MiB unity mapping for LPC

**CentOS 7**: ::

       cat /proc/cmdline 
       BOOT_IMAGE=/boot/vmlinuz-3.10.0-693.2.2.el7.x86_64 root=UUID=4176a996-b51d-44d0-a4d8-74dbe7db81fa ro crashkernel=auto selinux=0 ipv6.disable=1 intel_iommu=on iommu=pt pci=realloc rdblacklist=nvidia,nouveau rhgb quiet pci-stub.ids=10de:1c03,10de:10f1 LANG=en_US.UTF-8
       
       # dmesg | grep -iE "dmar|iommu"
       [    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz-3.10.0-693.2.2.el7.x86_64 root=UUID=4176a996-b51d-44d0-a4d8-74dbe7db81fa ro crashkernel=auto selinux=0 ipv6.disable=1 intel_iommu=on iommu=pt pci=realloc rdblacklist=nvidia,nouveau rhgb quiet pci-stub.ids=10de:1c03,10de:10f1 LANG=en_US.UTF-8
       [    0.000000] ACPI: DMAR 000000007e1e1ff0 000BC (v01 A M I   OEMDMAR 00000001 INTL 00000001)
       [    0.000000] Kernel command line: BOOT_IMAGE=/boot/vmlinuz-3.10.0-693.2.2.el7.x86_64 root=UUID=4176a996-b51d-44d0-a4d8-74dbe7db81fa ro crashkernel=auto selinux=0 ipv6.disable=1 intel_iommu=on iommu=pt pci=realloc rdblacklist=nvidia,nouveau rhgb quiet pci-stub.ids=10de:1c03,10de:10f1 LANG=en_US.UTF-8
       [    0.000000] DMAR: IOMMU enabled
       [    0.037839] DMAR: Host address width 46
       ...
       [    0.692358] DMAR: Ignoring identity map for HW passthrough device 0000:00:1f.0 [0x0 - 0xffffff]
       [    0.692361] DMAR: Intel(R) Virtualization Technology for Directed I/O
       [    0.692399] iommu: Adding device 0000:00:00.0 to group 0
       [    0.692415] iommu: Adding device 0000:00:01.0 to group 1
       ...

Check that nvidia driver is not loaded :: 

     lsmod | grep nvidia

should return nothing

Detach GPU from a physical host
---------------------------------

The commands to detach GPU cards from  physical hosts are run once for each GPU card on each host. 
The list below includes some informational commands.

#. Run ``gpupci -l`` command on all GPU-enabled vm-containers to get information about the GPU cards. 
   For example,  on vm-container-0-15  the output is :: 

     # gpupci -l
     gpupci1 pci_0000_02_00_0
     gpupci2 pci_0000_03_00_0
   
   The output means there are 2 GPU cards and for each there is 
   a logincal GPU name and its PCI bus info.

#. Run commands to add this information in the rocks database: ::

    # rocks add host gpu vm-container-0-15 gpupci1 pci_0000_02_00_0
    # rocks add host gpu vm-container-0-15 gpupci2 pci_0000_03_00_0

#. Verify that  GPU info now is in the database: :: 

    # rocks list host gpu
    HOST               GPU     PCI_BUS         
    vm-container-0-15: gpupci1 pci_0000_02_00_0
    vm-container-0-15: gpupci2 pci_0000_03_00_0

#. Detach the GPU cards from the physical host. This is an actual command that detaches the GPU from the
   physical host  PCI bus. This needs to be done once  for each GPU card 
   before any VM can use the GPU PCI in pass-through mode. This can be done as a single command
   for all cards :: 

    # rocks run host vm-container-0-15 "gpupci -d all"

   or using a specific logical name for a single GPU card  on a given host :: 

    # rocks run host vm-container-0-2 "gpupci -d gpupci1"


Attach GPU to a guest VM
---------------------------
Once the GPU card is detached from a physical host it is ready for use by the guest VM. 
We assume that a single GPU card is assigned to a VM and that a VM is run on a GPU-enabled vm-container. 
For example, if there is a VM rocks-33 that is created and running on a vm-container-0-15 and we want  
to assign a GPU  to it: ::  

   rocks stop host VM rocks-33
   rocks add host gpu rocks-33 gpupci pci_0000_02_00_0
   rocks report host vm config rocks-33

The first command stops VM, the ``add`` command adds a GPU attribute to the VM in the rocks database.   
The ``report`` command verifies that the xml file that describes the VM configuration has device information
for the GPU card. For this example, the output would contain: :: 

    ...
      <hostdev mode='subsystem' type='pci' managed='yes'>
        <source>
          <address domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
        </source>
      </hostdev>
    </devices>

At the next start of the VM the  GPU card  will be available to the VM. 

Checks on a VM
----------------

#. PCI bus address

   On the VM the GPU PCI bus address will be different from the GPU PCI address of the physical host. 
   For eample, a GPU card  on a physical host ::

      [root@gpu-1-6]# lspci -D -d 10de:
      0000:02:00.0 3D controller: NVIDIA Corporation GF100GL [Tesla T20 Processor] (rev a3)

   shows on a VM as ::

      root@rocce-vm3 ~]# lspci -d 10de:
      00:06.0 3D controller: NVIDIA Corporation GF100GL [Tesla T20 Processor] (rev a3)

#.  check nvidia driver is loaded ::  

      # lsmod | grep nvidia
      nvidia_uvm             63294  0 
      nvidia               8368623  1 nvidia_uvm
      i2c_core               29964  2 nvidia,i2c_piix4

#. check if the GPU card is present  :: 

      # nvidia-smi 
      Thu Aug 31 17:37:32 2017       
      +------------------------------------------------------+                       
      | NVIDIA-SMI 346.59     Driver Version: 346.59         |                       
      |-------------------------------+----------------------+----------------------+
      | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
      | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
      |===============================+======================+======================|
      |   0  Tesla M2050         On   | 0000:00:06.0     Off |                    0 |
      | N/A   N/A    P1    N/A /  N/A |      6MiB /  2687MiB |      0%   E. Process |
      +-------------------------------+----------------------+----------------------+
                                                                                     
      +-----------------------------------------------------------------------------+
      | Processes:                                                       GPU Memory |
      |  GPU       PID  Type  Process name                               Usage      |
      |=============================================================================|
      |  No running processes found                                                 |
      +-----------------------------------------------------------------------------+

#. run a few commands form nvidia toolkit to get more info about the GPU card :: 

      nvidia-smi -q
      /opt/cuda/bin/deviceQuery
      /opt/cuda/bin/deviceQueryDrv


Useful commands
---------------

The first set of commands can be run on physical and virtual hsots, the  rest
are run on aphysical host.

#. listing of pci devices ::

     lspci -D -n
     lspci -D -n -d 10de:
     lspci -D -nn -d 10de:
     lspci -vvv -s 0000:03:00.0

   For example, the output below shows info for 2 GPU cards, for video and audio components ::

     # lspci -D -n -d 10de:
     0000:02:00.0 0302: 10de:06de (rev a3)
     0000:02:00.1 0403: 10de:0be5 (rev a1)
     0000:03:00.0 0302: 10de:06de (rev a3)
     0000:03:00.1 0403: 10de:0be5 (rev a1)

   The video card component ends on ``0`` abd audio card component ends on ``1``.

#. virsh info for the devices as a tree ::  

      virsh nodedev-list --tree

   Note, that 4 devices from the above lspci command 
   in the output of this command become :: 

      +- pci_0000_00_03_0            (comment: parent pci device)
      |   |
      |   +- pci_0000_02_00_0
      |   +- pci_0000_02_00_1
      |     
      +- pci_0000_00_07_0            (comment: parent pci device)
      |   |
      |   +- pci_0000_03_00_0
      |   +- pci_0000_03_00_1

   This syntax  for pci bus is used in all ``virsh`` commands below.

#. virsh detach and reattach devices :: 

     virsh nodedev-detach pci_0000_02_00_0
     virsh nodedev-detach pci_0000_02_00_1
     virsh nodedev-reattach pci_0000_02_00_1


#. GPU cards info ::

     virsh nodedev-dumpxml pci_0000_02_00_0 > pci-gpu1
     virsh nodedev-dumpxml pci_0000_03_00_0 > pci-gpu2

#. check device  symbolic links :: 

     readlink /sys/bus/pci/devices/0000\:02\:00.0/driver

#. check xml definition of the VM :: 

     virsh dumpxml rocce-vm3 > vm3.out
   
   For a GPU-enabled VM, ``hostdev`` section described in the sections above should be in the output.

Links
---------

Useful links for enabling PCI passthrough devices

* Enabling `PCI passthrough with KVM`_
* Determine if your processor supports `Intel Virtualization Technology`_
* Red HAt `Guest VM device configuration`_


Examples if gpupt command
----------------------------

::

    [root@vm-container-0-15 ~]# gpupci -l
    gpupci1 pci_0000_02_00_0
    gpupci2 pci_0000_03_00_0
    gpupci3 pci_0000_83_00_0
    gpupci4 pci_0000_84_00_0

    [root@vm-container-0-15 ~]# gpupci -s all
    GPU card 'gpupci1' video device 0000:02:00.0 is linked to bus/pci/drivers/nvidia driver
    GPU card 'gpupci1' audio device 0000:02:00.1 is linked to bus/pci/drivers/snd_hda_intel driver
    GPU card 'gpupci2' video device 0000:03:00.0 is linked to bus/pci/drivers/nvidia driver
    GPU card 'gpupci2' audio device 0000:03:00.1 is linked to bus/pci/drivers/snd_hda_intel driver
    GPU card 'gpupci3' video device 0000:83:00.0 is linked to bus/pci/drivers/nvidia driver
    GPU card 'gpupci3' audio device 0000:83:00.1 is linked to bus/pci/drivers/snd_hda_intel driver
    GPU card 'gpupci4' video device 0000:84:00.0 is linked to bus/pci/drivers/nvidia driver
    GPU card 'gpupci4' audio device 0000:84:00.1 is linked to bus/pci/drivers/snd_hda_intel driver

    [root@vm-container-0-15 ~]# gpupci -d all
    Detached GPU card 'gpupci1' video device 0000:02:00.0
    Detached GPU card 'gpupci1' audio device 0000:02:00.1
    GPU card 'gpupci2' video device 0000:03:00.0 is already detached
    Detached GPU card 'gpupci2' audio device 0000:03:00.1
    GPU card 'gpupci3' video device 0000:83:00.0 is already detached
    Detached GPU card 'gpupci3' audio device 0000:83:00.1
    GPU card 'gpupci4' video device 0000:84:00.0 is already detached
    Detached GPU card 'gpupci4' audio device 0000:84:00.1


    [root@vm-container-0-15 ~]# gpupci -s all
    GPU card 'gpupci1' video device 0000:02:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci1' audio device 0000:02:00.1 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci2' video device 0000:03:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci2' audio device 0000:03:00.1 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci3' video device 0000:83:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci3' audio device 0000:83:00.1 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci4' video device 0000:84:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci4' audio device 0000:84:00.1 is linked to bus/pci/drivers/pci-stub driver

    [root@vm-container-0-15 log]# gpupci -a gpupci1
    Attached video card 0000:02:00.0 of gpupci1
    Attached audio card 0000:02:00.1 of gpupci1

    [root@vm-container-0-15 log]# gpupci -l
    gpupci1 pci_0000_02_00_0
    gpupci2 pci_0000_03_00_0
    gpupci3 pci_0000_83_00_0
    gpupci4 pci_0000_84_00_0

    [root@vm-container-0-15 log]# gpupci -s all
    GPU card 'gpupci1' video device 0000:02:00.0 is linked to bus/pci/drivers/nvidia driver
    GPU card 'gpupci1' audio device 0000:02:00.1 is linked to bus/pci/drivers/snd_hda_intel driver
    GPU card 'gpupci2' video device 0000:03:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci2' audio device 0000:03:00.1 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci3' video device 0000:83:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci3' audio device 0000:83:00.1 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci4' video device 0000:84:00.0 is linked to bus/pci/drivers/pci-stub driver
    GPU card 'gpupci4' audio device 0000:84:00.1 is linked to bus/pci/drivers/pci-stub driver


.. _PCI passthrough with KVM: https://docs-old.fedoraproject.org/en-US/Fedora/13/html/Virtualization_Guide/chap-Virtualization-PCI_passthrough.html
.. _Intel Virtualization Technology: http://www.intel.com/content/www/us/en/support/processors/000005486.html
.. _Guest VM device configuration: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Virtualization_Deployment_and_Administration_Guide/chap-Guest_virtual_machine_device_configuration.html#sect-device-GPU
.. _Cuda roll: https://github.com/nbcrrolls/cuda
