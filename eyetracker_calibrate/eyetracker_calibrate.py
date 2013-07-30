"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4 import QtGui

from libopensesame import item, debug
from libqtopensesame import qtplugin
import imp
import os.path

class eyetracker_calibrate(item.item):

	"""
	The calibration plug-in also handles the connection to the eye tracker, and
	therefore should always be the first eyetracker plug-in of the experiment.
	"""

	def __init__(self, name, experiment, string=None):

		"""
		Constructor.

		Arguments:
		name		--	The item name.
		experiment	--	The experiment object.

		Keyword arguments:
		string		--	The definition string. (default=None)
		"""

		self.version = 0.01
		self.item_type = u'eyetracker_calibrate'
		self.description = \
			u'Calibration/ initialization plugin for an eye tracker'
		# default values
		self._text_eyelink = u'EyeLink'
		self._text_smi = u'SMI'
		self._text_sdummy = u'simple dummy mode (does nothing)'
		self._text_edummy = u'extended dummy mode (use mouse to simulate eye movement)'
		self.tracker_type = self._text_sdummy
		self.sacc_vel_thresh = 35
		self.sacc_acc_thresh = 9500
		self.cal_target_size = 16
		self.cal_beep = u'yes'
		self.force_drift_correct = u'no'
		self.ip = u'127.0.0.1'
		self.sendport = 4444
		self.receiveport = 5555
		self.screen_w = 399
		self.screen_h = 299

		# the parent handles the rest of the construction
		item.item.__init__(self, name, experiment, string)

	def prepare(self):

		"""Prepares the item and connects to the eye tracker."""

		item.item.prepare(self)
		
		# the logfile has the same name as the opensesame log, but with a
		# different extension; we also filter out characters that are not
		# supported
		data_file = u''
		for c in os.path.splitext(os.path.basename(self.get( \
			u'logfile')))[0]:
			if c.isalnum():
				data_file += c
		print u'eyetracker_calibrate(): logging tracker data as %s' % data_file

		# EYELINK
		if self.get(u'tracker_type') == self._text_eyelink:
			libname = u'libeyelink'

			# data file extension
			data_file = data_file + u'.edf'
			# automatically rename common filenames that are too long.
			if data_file[:8] == u'subject-':
				data_file = u'S' + data_file[8:]
			if data_file == u'defaultlog.edf':
				data_file = u'default.edf'

		# SMI
		elif self.get(u'tracker_type') == self._text_smi:
			libname = u'libsmi'

		# EXTENDED DUMMY
		elif self.get(u'tracker_type') == self._text_edummy:
			libname = u'libdummytracker'

		# SIMPLE DUMMY
		else:
			libname = u'libdummy'

		# dynamically load eyetracker library
		exec(u'path = os.path.join(os.path.dirname(__file__), u"%s.py")' % libname)
		exec(u'%s = imp.load_source(u"%s", path)' % (libname, libname))
		exec(u'eyetracker = %s.%s' % (libname,libname))

		# initialize eyetracker
		debug.msg(u'loading %s' % libname)
		self.experiment.eyetracker = eyetracker(
			self.experiment, \
			(self.get(u'width'), self.get(u'height')), \
			data_file=data_file, \
			saccade_velocity_threshold=self.get(u'sacc_vel_thresh'), \
			saccade_acceleration_threshold=self.get(u'sacc_acc_thresh'), \
			force_drift_correct=self.get(u'force_drift_correct')== u'yes'
			)

		# update cleanup functions
		self.experiment.cleanup_functions.append(self.close)
		
		# Report success DEPRECATED IN 0.27.2+
		return True

	def close(self):

		"""
		Performs some cleanup functions to make sure that we don't leave
		OpenSesame and the eye tracker in a mess.
		"""

		debug.msg(u'starting eyetracker deinitialisation')
		self.sleep(100)
		self.experiment.eyetracker.close()
		self.experiment.eyetracker = None
		debug.msg(u'finished eyetracker deinitialisation')
		self.sleep(100)

	def run(self):

		"""
		Runs the item.
		"""

		self.set_item_onset()
		self.experiment.eyetracker.calibrate(beep=self.get(u'cal_beep')== \
			u'yes', target_size=self.get(u'cal_target_size'))

		# report success DEPRECATED IN 0.27.2+
		return True

class qteyetracker_calibrate(eyetracker_calibrate, qtplugin.qtplugin):

	"""The GUI part of the plug-in."""

	def __init__(self, name, experiment, string=None):

		"""
		Constructor.

		Arguments:
		name		--	The item name.
		experiment	--	The experiment object.

		Keyword arguments:
		string	--	The definition string. (default=None)
		"""
		
		eyetracker_calibrate.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""Initializes the controls."""

		# lock the widget until we're doing creating it
		self.lock = True

		# pass the word on to the parent
		qtplugin.qtplugin.init_edit_widget(self, False)
		
		# general
		self.add_combobox_control("tracker_type", "Tracker type", \
			[self._text_eyelink, self._text_smi, self._text_sdummy, self._text_edummy], \
			tooltip = "Indicates the tracker type")
		self.add_checkbox_control("cal_beep", "Calibration beep", \
			tooltip = "Indicates whether a beep sounds when the calibration target jumps")
		self.add_spinbox_control("cal_target_size", "Calibration target size", 0, 256,
			tooltip = "The size of the calibration target in pixels")
		self.add_line_edit_control("sacc_vel_thresh", "Saccade velocity threshold", \
			tooltip = "Saccade detection parameter")
		self.add_line_edit_control("sacc_acc_thresh", "Saccade acceleration threshold", \
			tooltip = "Saccade detection parameter")
		
		# EyeLink only
#		self.add_text("<br><b>EyeLink only</b>")
#		row = self.edit_grid.rowCount()
#		self.edit_vbox.addWidget(QtGui.QLabel("<br><b>EyeLink only</b>"), row)
		self._driftwidget = self.add_checkbox_control("force_drift_correct", \
			"Enable drift correction if disabled (Eyelink 1000)", \
			tooltip = "Indicates whether drift correction should be enabled, if it is disabled in the Eyelink configuration.")
		# SMI only
#		self.add_text("<br><b>SMI only</b>")
		self._ipwidget = self.add_line_edit_control("ip", "iViewX IP (SMI)", \
			tooltip = "iViewX internal IP address")
		self._sendportwidget = self.add_line_edit_control("sendport", "iViewX send port (SMI)", \
			tooltip = "port number for iViewX sending")
		self._receiveportwidget = self.add_line_edit_control("receiveport", "iViewX receive port (SMI)", \
			tooltip = "port number for iViewX receiving")
		self._wwidget = self.add_spinbox_control("screen_w", "Physical screen width (SMI)", 0, 9999,
			suffix=u'mm', tooltip = "The width of the screen in millimeters; used for event detection")
		self._hwidget = self.add_spinbox_control("screen_h", "Physical screen height (SMI)", 0, 9999,
			suffix=u'mm', tooltip = "The height of the screen in millimeters; used for event detection")
		# version number
		self.add_text("<br><br><small><b>OpenSesame EyeTracker plug-in v%.2f</b></small>" % self.version)

		# pad empty space below controls
		self.add_stretch()

		# unlock
		self.lock = False

	def apply_edit_changes(self):

		"""Applies the controls."""

		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return False
		self.experiment.main_window.refresh(self.name)
		return True

	def edit_widget(self):

		"""Update the controls."""

		# lock
		self.lock = True
		# edit
		qtplugin.qtplugin.edit_widget(self)
		# disable EyeLink and SMI specific widgets
		self._driftwidget.setDisabled(self.get(u'tracker_type') != self._text_eyelink)
		self._ipwidget.setDisabled(self.get(u'tracker_type') != self._text_smi)
		self._sendportwidget.setDisabled(self.get(u'tracker_type') != self._text_smi)
		self._receiveportwidget.setDisabled(self.get(u'tracker_type') != self._text_smi)
		self._wwidget.setDisabled(self.get(u'tracker_type') != self._text_smi)
		self._hwidget.setDisabled(self.get(u'tracker_type') != self._text_smi)
		# unlock
		self.lock = False
		return self._edit_widget

