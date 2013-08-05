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

from libopensesame import item, exceptions
from libqtopensesame import qtplugin
import os.path
import imp
from PyQt4 import QtGui, QtCore

class eyetracker_stop_recording(item.item):

	"""
	This class (the class with the same name as the module)
	handles the basic functionality of the item. It does
	not deal with GUI stuff.
	"""

	def __init__(self, name, experiment, string = None):
	
		"""
		Constructor
		"""
		
		# The item_typeshould match the name of the module
		self.item_type = "eyetracker_stop_recording"		
		
		self.xpos = 0
		self.ypos = 0
		
		# Provide a short accurate description of the items functionality
		self.description = "Stop eye-tracker recording (part of the eyetracker plug-ins)"

		# The parent handles the rest of the contruction
		item.item.__init__(self, name, experiment, string)
		
		if not hasattr(self, "log_msg"):
			self.log_msg = "stop_trial"
						
	def prepare(self):
	
		"""
		Prepare the item. In this case this means drawing a fixation
		dot to an offline canvas.
		"""
		
		# Pass the word on to the parent
		item.item.prepare(self)		
		
		# Create an eyetracker instance if it doesn't exist yet. Libeyetracker is
		# dynamically loaded
		if not hasattr(self.experiment, "eyetracker"):
			raise exceptions.runtime_error("Please connect to the eyetracker using the the eyetracker_calibrate plugin before using any other eyetracker plugins")
				
		# Report success
		return True
				
	def run(self):
	
		"""
		Run the item. In this case this means putting the offline canvas
		to the display and waiting for the specified duration.
		"""
		
		self.set_item_onset()

		self.experiment.eyetracker.status_msg(self.eval_text(self.get("log_msg")))	
		self.experiment.eyetracker.log(self.eval_text(self.get("log_msg")))	
		self.experiment.eyetracker.stop_recording()
				
		# Report success
		return True
					
class qteyetracker_stop_recording(eyetracker_stop_recording, qtplugin.qtplugin):

	"""
	This class (the class named qt[name of module] handles
	the GUI part of the plugin. For more information about
	GUI programming using PyQt4, see:
	<http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>
	"""

	def __init__(self, name, experiment, string = None):
	
		"""
		Constructor
		"""
		
		# Pass the word on to the parents		
		eyetracker_stop_recording.__init__(self, name, experiment, string)		
		qtplugin.qtplugin.__init__(self, __file__)	
		
	def init_edit_widget(self):
	
		"""
		This function creates the controls for the edit
		widget.
		"""
		
		# Lock the widget until we're doing creating it
		self.lock = True
		
		# Pass the word on to the parent		
		qtplugin.qtplugin.init_edit_widget(self, False)			
		self.add_line_edit_control("log_msg", "Log message", default = "stop_trial", tooltip = "A message to write to the eyetracker logfile.", min_width = 400)
		
		# Add a stretch to the edit_vbox, so that the controls do not
		# stretch to the bottom of the window.
		self.edit_vbox.addStretch()		
		
		# Unlock
		self.lock = True		
		
	def apply_edit_changes(self):
	
		"""
		Set the variables based on the controls
		"""
		
		# Abort if the parent reports failure of if the controls are locked
		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return False
				
		# Refresh the main window, so that changes become visible everywhere
		self.experiment.main_window.refresh(self.name)		
		
		# Report success
		return True

	def edit_widget(self):
	
		"""
		Set the controls based on the variables
		"""
		
		# Lock the controls, otherwise a recursive loop might aris
		# in which updating the controls causes the variables to be
		# updated, which causes the controls to be updated, etc...
		self.lock = True
		
		# Let the parent handle everything
		qtplugin.qtplugin.edit_widget(self)				
		
		# Unlock
		self.lock = False
		
		# Return the _edit_widget
		return self._edit_widget
		
		

