##############################################################################
#  Script to record data for X seconds of duration at Y second intervals
##############################################################################
import time
import camcmd


class IntervalRecording(object):

    def __init__(self, log_duration=1.0, log_interval=30):
    """
        log_duration    <float>         Number of seconds to record data after enabling recording
        log_interval    <float>         Number of seconds to wait before recording for log_duration again.
    """
        self.cmdobj = camcmd.CamCmd()
        self.log_duration = log_duration
        self.log_interval = log_interval

    def enable_recording(self):
        # Enable recording
        cmd_str='enable_recording'
        self.cmdobj.send(cmd_str)
        print("Sending [%s]..."%(cmd_str))

    def disable_recording(self):
        # Disable recording
        cmd_str='disable_recording'
        self.cmdobj.send(cmd_str)
        print("Sending [%s]..."%(cmd_str))


    def run(self):

        while True:

            self.enable_recording()
            print("Recording for [%.2f] seconds..."%(self.log_duration))
            time.sleep(self.log_duration)
            self.disable_recording()

            print("Wait [%.2f] seconds log interval..."%(self.log_interval))
            time.sleep(self.log_interval)

def main():

    a = IntervalRecording()
    a.run()

    pass


if __name__ == "__main__":

    main()
