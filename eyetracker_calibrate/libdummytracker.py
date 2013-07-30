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

from openexp.keyboard import keyboard
from openexp.mouse import mouse
from openexp.canvas import canvas
from openexp.synth import synth


class libdummytracker:

	"""A dummy class to keep things running if there is no tracker attached."""

	def __init__(self, experiment, resolution, data_file="default.edf", fg_color=(255, 255, 255), bg_color=(0, 0, 0), saccade_velocity_threshold=35, saccade_acceleration_threshold=9500, force_drift_correct=u'yes'):

		"""Initializes the eyelink dummy object"""

		self.experiment = experiment
		self.data_file = data_file
		self.resolution = resolution
		self.recording = False

		self.simulator = mouse(self.experiment)
		self.simulator.set_timeout(timeout=2)

		self.blinking = False # current 'blinking' condition (MOUSEBUTTONDOWN = eyes closed; MOUSEBUTTONUP = eyes open)
		self.bbpos = (resolution[0]/2,resolution[1]/2) # before 'blink' position

		# check if blinking functionality is possible
		if not hasattr(self.simulator, 'get_pressed') or not hasattr(self.simulator, 'set_poesje'):
			print("libeyelink_dummy: blink functionality not available due to missing openexp.mouse.get_pressed and/or openexp.mouse.set_pos methods")
			self.blinkfun = False
		else:
			self.blinkfun = True

	def send_command(self, cmd):

		"""Dummy command"""

		print 'libeyelink.send_command(): %s' % cmd

	def log(self, msg):

		"""Dummy log message"""

		print 'libeyelink.log(): %s' % msg

	def log_var(self, var, val):

		"""Dummy variable logging"""

		print 'libeyelink.log_var(): %s %d' % var, val

	def status_msg(self, msg):

		"""Dummy status message"""

		print 'libeyelink.status_msg(): %s' % msg

	def connected(self):

		"""Dummy connection status"""

		return True

	def calibrate(self, beep=True, target_size=16):

		"""Dummy calibration"""

		print 'libeyelink.calibrate(): calibration would now take place'

	def get_eyelink_clock_async(self):

		"""Asynchronity between libeyelink_dummy object and OpenSesame"""

		return 0

	def drift_correction(self, pos = None, fix_triggered = False):

		"""Dummy drift correction"""

		if fix_triggered:
			return self.fix_triggered_drift_correction(pos)

		self.simulator.set_visible(visible=True)

		my_keyboard = keyboard(self.experiment, keylist=["space"], timeout=0)
		errorbeep = synth(self.experiment, freq=220, length=200)

		if pos == None:
			pos = self.resolution[0] / 2, self.resolution[1] / 2

		errdist = 60 # pixels (on a 1024x768px and 39.9x29.9cm monitor at 67 cm, this is about 2 degrees of visual angle)

		pressed = None
		while not pressed:
			pressed, presstime = my_keyboard.get_key()
			if pressed:
				gazepos = self.sample()
				if ((gazepos[0]-pos[0])**2  + (gazepos[1]-pos[1])**2)**0.5 < errdist:
					self.simulator.set_visible(visible=False)
					return True
		errorbeep.play()
		self.simulator.set_visible(visible=False)
		return False

	def prepare_drift_correction(self, pos):

		"""Dummy drift correction preparation"""

		pass

	def fix_triggered_drift_correction(self, pos = None, min_samples = 30, max_dev = 60, reset_threshold = 10):

		"""Dummy drift correction (fixation triggered)"""

		self.simulator.set_visible(visible=True)

		if pos == None:
			pos = self.resolution[0] / 2, self.resolution[1] / 2

		self.prepare_drift_correction(pos)
		my_keyboard = keyboard(self.experiment, keylist=["escape", "q"], timeout=0)

		# loop until we have sufficient samples
		lx = []
		ly = []
		while len(lx) < min_samples:

			# pressing escape enters the calibration screen
			if my_keyboard.get_key()[0] != None:
				self.simulator.set_visible(visible=False)
				self.recording = False
				print("libeyelink.fix_triggered_drift_correction(): 'q' pressed")
				return False

			# collect a sample
			x, y = self.sample()

			if len(lx) == 0 or x != lx[-1] or y != ly[-1]:

				# if present sample deviates too much from previous sample, reset counting
				if len(lx) > 0 and (abs(x - lx[-1]) > reset_threshold or abs(y - ly[-1]) > reset_threshold):
					lx = []
					ly = []

				# collect samples
				else:
					lx.append(x)
					ly.append(y)

			if len(lx) == min_samples:

				avg_x = sum(lx) / len(lx)
				avg_y = sum(ly) / len(ly)
				d = ((avg_x - pos[0]) ** 2 + (avg_y - pos[1]) ** 2)**0.5

				if d < max_dev:
					self.simulator.set_visible(visible=False)
					return True
				else:
					lx = []
					ly = []

	def start_recording(self):

		"""Start dummy recording"""

		self.simulator.set_visible(visible=True)
		self.recording = True
		print 'libeyelink.start_recording(): recording started'

	def stop_recording(self):

		"""Stop dummy recording"""

		self.simulator.set_visible(visible=False)
		self.recording = False
		print 'libeyelink.stop_recording(): recording stopped'

	def close(self):

		"""Start dummy recording"""

		if self.recording:
			self.stop_recording()

		print 'libeyelink.close(): connection closed'

	def set_eye_used(self):
		pass

	def sample(self):

		"""Returns simulated gaze position (=mouse position)"""

		if self.blinkfun:
			if self.blinking:
				if self.simulator.get_pressed()[2]: # buttondown
					self.simulator.set_pos(pos=(self.bbpos[0],self.resolution[1])) # set position to blinking position
				elif not self.simulator.get_pressed()[2]: # buttonup
					self.simulator.set_pos(pos=self.bbpos) # set position to position before blinking
					self.blinking = False # 'blink' stopped

			elif not self.blinking:
				if self.simulator.get_pressed()[2]: # buttondown
					self.blinking = True # 'blink' started
					self.bbpos =  self.simulator.get_pos()[0] # position before blinking
					self.simulator.set_pos(pos=(self.bbpos[0],self.resolution[1])) # set position to blinking position

		return self.simulator.get_pos()[0]

	def pupil_size(self):

		"""Dummy pupil size"""

		return 0

	def wait_for_event(self, event):

		"""Waits for simulated event (3=STARTBLINK, 4=ENDBLINK, 5=STARTSACC, 6=ENDSACC, 7=STARTFIX, 8=ENDFIX)"""

		if event == 5:
			self.wait_for_saccade_start()
		elif event == 6:
			self.wait_for_saccade_end()
		elif event == 7:
			self.wait_for_fixation_start()
		elif event == 8:
			self.wait_for_fixation_end()
		elif event == 3:
			self.wait_for_blink_start()
		elif event == 4:
			self.wait_for_blink_end()

		return (self.experiment.time(), ())

	def wait_for_saccade_start(self):

		"""Returns starting time and starting position when a simulated saccade is started"""

		# function assumes that a 'saccade' has been started when a deviation of more than
		# maxerr from the initial 'gaze' position has been detected (using Pythagoras, ofcourse)

		spos = self.sample() # starting position
		maxerr = 3 # pixels
		while True:
			npos = self.sample() # get newest sample
			if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > maxerr: # Pythagoras
				break

		return self.experiment.time(), spos

	def __wait_for_saccade_start_pre_10028(self):

		"""
		Returns starting time and starting position when a simulated saccade is started.
		(dummy for a libeyelink implementation that catches a pylink bug that existed before pylink 1.0.0.28)
		"""

		return self.wait_for_saccade_start()


	def wait_for_saccade_end(self):

		"""Returns ending time, starting and end position when a simulated saccade is ended"""

		# function assumes that a 'saccade' has ended when 'gaze' position remains reasonably
		# (i.e.: within maxerr) stable for five samples
		# for saccade start algorithm, see wait_for_fixation_start

		stime, spos = self.wait_for_saccade_start()
		maxerr = 3 # pixels
		
		# wait for reasonably stable position
		xl = [] # list for last five samples (x coordinate)
		yl = [] # list for last five samples (y coordinate)
		moving = True
		while moving:
			# check positions
			npos = self.sample()
			xl.append(npos[0]) # add newest sample
			yl.append(npos[1]) # add newest sample
			if len(xl) == 5:
				# check if deviation is small enough
				if max(xl)-min(xl) < maxerr and max(yl)-min(yl) < maxerr:
                                        print xl
                                        print yl
					moving = False
				# remove oldest sample
				xl.pop(0); yl.pop(0)
			# wait for a bit, to avoid immediately returning (runs go faster than mouse moves)
			self.experiment.sleep(10)

		return self.experiment.time(), spos, (xl[len(xl)-1],yl[len(yl)-1])

	def wait_for_fixation_start(self):

		"""Returns starting time and position when a simulated fixation is started"""

		# function assumes a 'fixation' has started when 'gaze' position remains reasonably
		# stable for five samples in a row (same as saccade end)

		maxerr = 3 # pixels
		
		# wait for reasonably stable position
		xl = [] # list for last five samples (x coordinate)
		yl = [] # list for last five samples (y coordinate)
		moving = True
		while moving:
			npos = self.sample()
			xl.append(npos[0]) # add newest sample
			yl.append(npos[1]) # add newest sample
			if len(xl) == 5:
				# check if deviation is small enough
				if max(xl)-min(xl) < maxerr and max(yl)-min(yl) < maxerr:
					moving = False
				# remove oldest sample
				xl.pop(0); yl.pop(0)
			# wait for a bit, to avoid immediately returning (runs go faster than mouse moves)
			self.experiment.sleep(10)

		return self.experiment.time(), (xl[len(xl)-1],yl[len(yl)-1])

	def wait_for_fixation_end(self):

		"""Returns starting time and position when a simulated fixation is started"""

		# function assumes that a 'fixation' has ended when a deviation of more than maxerr
		# from the initial 'fixation' position has been detected (using Pythagoras, ofcourse)

		stime, spos = self.wait_for_fixation_start()
		maxerr = 3 # pixels
		
		while True:
			npos = self.sample() # get newest sample
			if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > maxerr: # Pythagoras
				break

		return self.experiment.time(), spos

	def wait_for_blink_start(self):

		"""Returns starting time and position of a simulated blink (mousebuttondown)"""

		# blinks are simulated with mouseclicks: a right mouseclick simulates the closing
		# of the eyes, a mousebuttonup the opening.

		if self.blinkfun:
			while not self.blinking:
				pos = self.sample()

			return self.experiment.time(), pos

		else:
			print("libeyelink_dummy: blink functionality not available")
			return self.experiment.time(), (0,0)

	def wait_for_blink_end(self):

		"""Returns ending time and position of a simulated blink (mousebuttonup)"""
		
		# blinks are simulated with mouseclicks: a right mouseclick simulates the closing
		# of the eyes, a mousebuttonup the opening.

		if self.blinkfun:
			# wait for blink start
			while not self.blinking:
				spos = self.sample()
			# wait for blink end
			while self.blinking:
				epos = self.sample()

			return self.experiment.time(), epos

		else:
			print("libeyelink_dummy: blink functionality not available")
			return self.experiment.time(), (0,0)

	def prepare_backdrop(self, canvas):
		pass

	def set_backdrop(self, backdrop):
		pass
