import base64
import smtpd


def decode_b64(data):
    byte_string = data.encode('utf-8')
    decoded = base64.b64decode(byte_string)
    return decoded.decode('utf-8')


def encode_b64(data):
    byte_string = data.encode('utf-8')
    encoded = base64.b64encode(byte_string)
    return encoded.decode('utf-8')


class SMTPBinChannel(smtpd.SMTPChannel):
    def __init__(self, server, *args, **kwargs):
        super().__init__(server, *args, **kwargs)
        self.database = server.database

        self.username = None
        self.password = None
        self.authenticating = False
        self.authenticated = False
        self.inbox = None

    def smtp_EHLO(self, arg):
        if not arg:
            self.push('501 Syntax: EHLO hostname')
            return
        # See issue #21783 for a discussion of this behavior.
        if self.seen_greeting:
            self.push('503 Duplicate HELO/EHLO')
            return
        self._set_rset_state()
        self.seen_greeting = arg
        self.extended_smtp = True
        self.push('250-%s' % self.fqdn)

        # Send the AUTH header
        self.push('250-AUTH LOGIN PLAIN')
        self.push('250-AUTH=PLAIN LOGIN')

        if self.data_size_limit:
            self.push('250-SIZE %s' % self.data_size_limit)
            self.command_size_limits['MAIL'] += 26
        if not self._decode_data:
            self.push('250-8BITMIME')
        if self.enable_SMTPUTF8:
            self.push('250-SMTPUTF8')
            self.command_size_limits['MAIL'] += 10
        self.push('250 HELP')

    def smtp_AUTH(self, arg):
        if 'PLAIN' in arg:
            split_args = arg.split(' ')
            # second arg is Base64-encoded string of blah\0username\0password
            authbits = decode_b64(split_args[1]).split('\0')
            self.username = authbits[1]
            self.password = authbits[2]
            inbox = self.database.get_inbox(self.username, self.password)
            if not inbox:
                self.push('454 Temporary authentication failure.')
            else:
                self.authenticated = True
                self.inbox = inbox['id']
                self.push('235 Authentication successful.')

        elif 'LOGIN' in arg:
            self.authenticating = True
            split_args = arg.split(' ')
            if len(split_args) == 2:  # LOGIN <Username>
                self.username = decode_b64(arg.split(' ')[1])
                self.push('334 ' + encode_b64('Password'))
            else:  # LOGIN
                self.push('334 ' + encode_b64('Username'))

        elif self.authenticating and not self.username:
            self.username = decode_b64(arg)
            self.push('334 ' + encode_b64('Password'))

        elif self.authenticating:
            self.authenticating = False
            self.password = decode_b64(arg)
            inbox = self.database.get_inbox(self.username, self.password)
            if not inbox:
                self.push('454 Temporary authentication failure.')
            else:
                self.authenticated = True
                self.inbox = inbox['id']
                self.push('235 Authentication successful.')

    def found_terminator(self):
        line = self._emptystring.join(self.received_lines)
        self.received_lines = []
        if self.smtp_state == self.COMMAND:
            sz, self.num_bytes = self.num_bytes, 0
            if not line:
                self.push('500 Error: bad syntax')
                return
            if not self._decode_data:
                line = str(line, 'utf-8')
            i = line.find(' ')
            if self.authenticating:
                arg = line.strip()
                command = 'AUTH'
            elif i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i + 1:].strip()

            max_sz = (self.command_size_limits[command]
                      if self.extended_smtp else self.command_size_limit)
            if sz > max_sz:
                self.push('500 Error: line too long')
                return

            if command not in ['AUTH', 'EHLO', 'HELO', 'NOOP', 'RSET', 'QUIT']:
                if not self.authenticated:
                    self.push('530 Authentication required')
                    return

            method = getattr(self, 'smtp_' + command, None)
            if not method:
                self.push('500 Error: command "%s" not recognized' % command)
                return
            method(arg)
            return
        else:
            if self.smtp_state != self.DATA:
                self.push('451 Internal confusion')
                self.num_bytes = 0
                return
            if self.data_size_limit and self.num_bytes > self.data_size_limit:
                self.push('552 Error: Too much mail data')
                self.num_bytes = 0
                return
            # Remove extraneous carriage returns and de-transparency according
            # to RFC 5321, Section 4.5.2.
            data = []
            for text in line.split(self._linesep):
                if text and text[0] == self._dotsep:
                    data.append(text[1:])
                else:
                    data.append(text)
            self.received_data = self._newline.join(data)
            args = (self.inbox, self.peer, self.mailfrom, self.rcpttos, self.received_data)
            kwargs = {}
            if not self._decode_data:
                kwargs = {
                    'mail_options': self.mail_options,
                    'rcpt_options': self.rcpt_options,
                }
            status = self.smtp_server.process_message(*args, **kwargs)
            self._set_post_data_state()
            if not status:
                self.push('250 OK')
            else:
                self.push(status)
