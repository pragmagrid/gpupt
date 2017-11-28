# $Id: __init__.py,v 1.10 2013/01/30 19:27:35 clem Exp $
#
# @Copyright@
# 
# 				Rocks(r)
# 		         www.rocksclusters.org
# 		         version 6.2 (SideWinder)
# 
# Copyright (c) 2000 - 2014 The Regents of the University of California.
# All rights reserved.	
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
# 
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# @Copyright@
#

import os
import rocks.commands
QEMUDOMAIN ="<domain type='qemu' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>" 

class Plugin(rocks.commands.Plugin):

 def provides(self):
  return 'global'

 def newqemu(self,xml):
	rxml = []
	for line in xml:
		if "<domain" in line:
			rxml.append(QEMUDOMAIN)
		elif "</features>" in line:
			rxml.append("      <kvm>")
			rxml.append("          <hidden state='on'/>")
			rxml.append("      </kvm>")
			rxml.append(line)
		elif "<emulator>" in line:
			rxml.append("    <emulator>/opt/gpupt-qemu/bin/qemu-system-x86_64</emulator>")
		else:
			rxml.append(line)
	return rxml

 def enablekvmflag(self):
  xmltext = []
  xmltext.append(" <qemu:commandline>")
  xmltext.append("   <qemu:arg value='-enable-kvm'/>")
  xmltext.append(" </qemu:commandline>")

  return xmltext

 def run(self, node, xml):
  """ If a VM has a 'gpupci' attribute set, the value is 
      a pci addresss of the host's GPU card.  Create a configuration 
      to assign the GPU device to the VM.
  """
  db = self.db
  attrs = self.db.getHostAttrs(node.name,0)
  rtxml = xml[:-1]
  if ("gpupci" in attrs.keys()):
      rtxml = self.newqemu(xml[:-1])
      rtxml += self.enablekvmflag()
  rtxml.append(xml[-1])
  return rtxml

