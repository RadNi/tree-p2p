import threading
import time


class UserInterface(threading.Thread):
    buffer = []

    def run(self):
        while True:
            message = input("Write your command:\n")
            # if message is not "":
            self.buffer.append(message)
            # print(self.buffer)
            # print("i gave message: _", message, "_")
    # Which the user or client sees and works with. run() #This method runs every time to
    #  see whether there is new messages or not.
    #   TODO

#
#
# class A:
#     buffers = []
#
#     def run(self):
#         """
#         Main loop of the program.
#
#         :return:
#         """
#         try:
#             self.ui = UserInterface()
#             self.ui.start()
#             self.buffers.extend(self.ui.buffer)
#         except:
#             raise Exception('UI thread failed to start')

#
# a = A()
# a.run()
# while True:
#     print(a.ui.buffer)
#     time.sleep(3)