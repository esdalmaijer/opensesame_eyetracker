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

class libdummy:

	"""
	A dummy class to keep things running if there is
	no tracker attached.
	"""

	def __init__(self, experiment, resolution, data_file=u'default.edf', fg_color=(255, 255, 255), bg_color=(0, 0, 0), saccade_velocity_threshold=35, saccade_acceleration_threshold=9500, force_drift_correct=False):
		self.experiment = experiment
	
	def send_command(self, cmd):
		pass
	
	def log(self, msg):
		pass	

	def log_var(self, var, val):
		pass	
		
	def status_msg(self, msg):
		pass
	
	def connected(self):
		pass
		
	def calibrate(self, beep=True, target_size=16):
		pass
	
	def drift_correction(self, pos = None, fix_triggered = False):
		self.experiment.sleep(200)
		return True

	def get_eyelink_clock_async(self):
		return 0

	def prepare_drift_correction(self, pos):
		pass
					
	def fix_triggered_drift_correction(self, pos = None, min_samples = 30, max_dev = 60, reset_threshold = 10):
		self.experiment.sleep(200)
		return True
	
	def start_recording(self):
		pass
		
	def stop_recording(self):
		pass

	def close(self):
		pass

	def set_eye_used(self):
		pass

	def sample(self):
		pass
	
	def pupil_size(self):
		pass

	def wait_for_event(self, event):
		pass
		
	def wait_for_saccade_start(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0)

	def __wait_for_saccade_start_pre_10028(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0)

	def wait_for_saccade_end(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0), (0, 0)

	def wait_for_fixation_start(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0)	
		
	def wait_for_fixation_end(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0)	
	
	def wait_for_blink_start(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0)	
	
	def wait_for_blink_end(self):
		self.experiment.sleep(100)
		return self.experiment.time(), (0, 0)

	def prepare_backdrop(self, canvas):
		pass

	def set_backdrop(self, backdrop):
		pass
