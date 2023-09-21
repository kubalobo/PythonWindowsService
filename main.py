import win32serviceutil
import win32service
import win32event
import servicemanager
# import socket
from datetime import datetime
import time
import sys

import apteki


class PythonService4(win32serviceutil.ServiceFramework):
    _svc_name_ = 'PythonService4'
    _svc_display_name_ = 'PythonService4'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        # socket.setdefaulttimeout(60)
        self.isAlive = True

    def SvcStop(self):
        self.isAlive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.isAlive = True
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def zapi_do_pliku(self):
        DIR = "D:\\Temp\\xxx\\test.log"

        with open(DIR, 'a') as file:
            file.write(str(f'{datetime.now()} wynik \n'))


    def main(self):
        # i = 0
        while self.isAlive:

            self.zapi_do_pliku()

            katalog1 = apteki.KatalogAptek()
            katalog1.wczytaj_z_pliku('apteki.txt')
            apteki.sprawdzam_niewyslane_recepty(katalog1)

            time.sleep(5)



if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PythonService4)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        sys.frozen = 'windows_exe' # Easier debugging
        win32serviceutil.HandleCommandLine(PythonService4)
