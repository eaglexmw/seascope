#!/usr/bin/python

import os, string
from PyQt4.QtCore import *

from ..PluginBase import ProjectBase, ConfigBase, QueryBase
import GtagsProjectUi
from GtagsProjectUi import QueryUiGtags

from .. import PluginHelper

class ConfigGtags(ConfigBase):
	def __init__(self):
		ConfigBase.__init__(self)

		self.gt_dir = ''
		self.gt_opt = ''
		self.gt_list = []

	def get_proj_name(self):
		return os.path.split(self.gt_dir)[1]
	def get_proj_src_files(self):
		fl = self.gt_list
		return fl

	def proj_start(self):
		gt_args = string.join(self.gt_opt)

	def proj_open(self, proj_path):
		self.gt_dir = proj_path
		self.proj_start()

	def proj_update(self, proj_args):
		self.proj_new(proj_args)
		
	def proj_new(self, proj_args):
		self.proj_args = proj_args
		(self.gt_dir, self.gt_opt, self.gt_list) = proj_args
		self.proj_start()

	def proj_close(self):
		pass

	def get_proj_conf(self):
		return (self.gt_dir, self.gt_opt, self.gt_list)

	def is_ready(self):
		return True

class ProjectGtags(ProjectBase):
	def __init__(self):
		ProjectBase.__init__(self)

	@staticmethod
	def _prj_new_or_open(conf):
		prj = ProjectGtags()
		prj.conf = conf
		prj.qry = QueryGtags(prj.conf)
		prj.qryui = QueryUiGtags(prj.qry)

		return (prj)

	@staticmethod
	def prj_new():
		proj_args = QueryUiGtags.prj_show_settings_ui(None)
		if (proj_args == None):
			return None

		conf = ConfigGtags()
		conf.proj_new(proj_args)
		prj = ProjectGtags._prj_new_or_open(conf)
		return (prj)

	@staticmethod
	def prj_open(proj_path):
		conf = ConfigGtags()
		conf.proj_open(proj_path)
		prj = ProjectGtags._prj_new_or_open(conf)
		return (prj)

	def prj_close(self):
		if (self.conf != None):
			self.conf.proj_close()
		self.conf = None

	def prj_dir(self):
		return self.conf.gt_dir
	def prj_name(self):
		return self.conf.get_proj_name()
	def prj_src_files(self):
		return self.conf.get_proj_src_files()

	def prj_is_open(self):
		return self.conf != None
	def prj_is_ready(self):
		return self.conf.is_ready()
		
	def prj_conf(self):
		return self.conf.get_proj_conf()
		
	def prj_update_conf(self, proj_args):
		self.conf.proj_update(proj_args)
	def prj_settings_trigger(self):
		proj_args = self.prj_conf()
		proj_args = QueryUiGtags.prj_show_settings_ui(proj_args)
		#if (proj_args == None):
			#return False
		#self.prj_update_conf(proj_args)
		#return True
		return False

from ..PluginBase import PluginProcess

class GtProcess(PluginProcess):
	def __init__(self, wdir, rq):
		PluginProcess.__init__(self, wdir)
		self.name = 'gtags process'
		if rq == None:
			rq = ['', '']
		self.cmd_str = rq[0]
		self.req = rq[1]

	def parse_result(self, text, sig):
		text = text.strip().splitlines()
		res = []
		for line in text:
			if line == '':
				continue
			line = line.split(' ', 3)
			line = [line[1], line[0], line[2], line[3]]
			res.append(line)
		return res

class QueryGtags(QueryBase):
	def __init__(self, conf):
		QueryBase.__init__(self)
		self.conf = conf

		self.gt_file_list_update()

	def query(self, cmd_str, req, opt):
		print cmd_str, req, opt
		if (not self.conf):
		#or not self.conf.is_ready()):
			print "pm_query not is_ready"
			return None
		if opt == None or opt == '':
			opt = []
		else:
			opt = opt.split()
		cmd_opt = GtagsProjectUi.cmd_str2id[cmd_str]
		pargs = [ 'global', '-a', '--result=cscope', '-x' ] + opt
		if cmd_opt != '':
			pargs += [ cmd_opt ]
		pargs += [ req ]
		
		qsig = GtProcess(self.conf.gt_dir, None).run_query_process(pargs, req)
		return qsig

	def rebuild(self):
		if (not self.conf.is_ready()):
			print "pm_query not is_ready"
			return None
		if (os.path.exists(os.path.join(self.conf.gt_dir, 'GTAGS'))):
			pargs = [ 'global', '-u' ]
		else:
			pargs = [ 'gtags', '-i' ]
		qsig = GtProcess(self.conf.gt_dir, None).run_rebuild_process(pargs)
		qsig.connect(self.gt_file_list_update)
		return qsig

	def gt_file_list_update(self):
		gt_file = os.path.join(self.conf.gt_dir, 'GTAGS')
		if not os.path.exists(gt_file):
			return
		fl = []
		try:
			import subprocess
			pargs = [ 'global', '-P', '-a' ]
			proc = subprocess.Popen(pargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=self.conf.gt_dir)
			(out_data, err_data) = proc.communicate()
			fl = out_data.strip().splitlines()
			print '1.flist', len(fl)
			PluginHelper.file_view_update(fl)
		except:
			import sys
			e = sys.exc_info()[1]
			print ' '.join(pargs)
			print e

	def gt_is_open(self):
		return self.conf != None
	def gt_is_ready(self):
		return self.conf.is_ready()
