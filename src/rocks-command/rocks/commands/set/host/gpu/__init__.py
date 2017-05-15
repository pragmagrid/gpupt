# $Id: __init__.py,v 1.11 2012/11/27 00:48:26 phil Exp $
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
import stat
import time
import sys
import string

import rocks.commands

class Command(rocks.commands.set.host.command):
	"""
	Sets a GPU on a host to the specified value 

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<arg type='string' name='gpu'>
	Name of the gpu. Must have prefix 'gpupci'.
	</arg>

	<arg type='string' name='value'>
	Value of the gpu PCI bus
	</arg>
	
	<param type='string' name='gpu'>
	same as gpu argument
	</param>

	<param type='string' name='value'>
	same as value argument
	</param>

	<example cmd='set host gpu compute-0-0 gpupci1 pci_0000_02_00_0'>
	Sets the value for gpu PCI bus to pci_0000_02_00_0 on host compute-0-0.
	</example>

	<example cmd='set host gpu compute-0-0 gpu=gpupci1 value=pci_0000_02_00_0'>
	same as above
	</example>
	
	<related>dump host gpu</related>
	<related>list host gpu</related>
	<related>remove host gpu</related>
	"""

	def run(self, params, args):

		(args, gpu, value) = self.fillPositionalArgs(('gpu', 'value'))
		hosts = self.getHostnames(args)
		if len(hosts) != 1:
			self.abort('must supply one host')
		host = hosts[0]

		if not gpu:
			self.abort('missing gpu name')
		if gpu.find('gpupci') != 0:
			self.abort('gpu name must start with "gpupci" prefix')

		if not value:
			self.about('missing value of gpu')

		for node in self.newdb.getNodesfromNames(args):
			self.newdb.setCategoryAttr('host', node.name, gpu, value)

RollName = "base"
