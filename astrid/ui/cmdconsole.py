import cmd
from astrid.server import AstridServer
from astrid.client import AstridClient

class AstridConsole(cmd.Cmd):
    """ Astrid Console 
    """

    prompt = '^_- '
    intro = 'Astrid Console'

    def __init__(self, client=None):
        cmd.Cmd.__init__(self)

        if client is None:
            self.client = AstridClient()
        else:
            self.client = client

    def do_p(self, cmd):
        self.client.send_cmd(['play'] + cmd.split(' '))

    def do_v(self, cmd):
        self.client.send_cmd(['set_value'] + cmd.split(' '))

    def do_track(self, cmd):
        self.client.send_cmd(['analysis'] + cmd.split(' '))

    def do_a(self, cmd):
        self.client.send_cmd(['add'] + cmd.split(' '))

    def do_r(self, cmd):
        self.client.send_cmd(['reload'] + cmd.split(' '))

    def do_i(self, cmd):
        try:
            for instrument in self.client.list_instruments():
                if isinstance(instrument, bytes):
                    instrument = instrument.decode('ascii')
                print(instrument)
        except TypeError:
            pass

    def do_s(self, instrument):
        if instrument == '':
            self.client.send_cmd(['stop_all'])
        else:
            self.client.send_cmd(['stop_instrument', instrument])

    def do_b(self, cmd):
        action, *values = cmd.split(' ')
        if action == 'c' or action == 'clear':
            self.client.send_cmd(['clear_bank'] + values)
        if action == 'r' or action == 'rec':
            self.client.send_cmd(['rec_bank'] + values)
        if action == 'd' or action == 'dub':
            self.client.send_cmd(['dub_bank'] + values)

    def do_quit(self, cmd):
        self.quit()

    def do_EOF(self, line):
        return True

    def postloop(self):
        pass

    def start(self):
        self.cmdloop()

    def quit(self):
        print('Quitting')
