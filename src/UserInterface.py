import threading
import time


class UserInterface(threading.Thread):
    buffer = []

    def run(self):
        while True:
            message = input("give me some message to broadcast:\n")
            self.buffer.append(message)

    # Which the user or client sees and works with. run() #This method runs every time to
    #  see whether there is new messages or not.
    #   TODO


class A:
    buffers = []

    def run(self):
        """
        Main loop of the program.

        :return:
        """
        try:
            self.ui = UserInterface()
            self.ui.start()
            self.buffers.extend(self.ui.buffer)
        except:
            raise Exception('UI thread failed to start')


a = A()
a.run()
while True:
    print(a.ui.buffer)
    time.sleep(3)