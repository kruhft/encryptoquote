#!/usr/bin/env python
import encryptoquote
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import os, pwd, grp

def update_quote():
    global quote_tuple, quote_str, enc_quote
    quote_tuple = encryptoquote.get_random_quote()
    quote_str = quote_tuple[0] + " -- " + quote_tuple[1]
    quote_str = quote_str.upper()
    enc_quote = encryptoquote.substitution_cipher(quote_str)
update_quote()

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Remove group privileges
    #os.setgroups([])

    # Ensure a very conservative umask
    old_umask = os.umask(077)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/quote.html"):
            global quote_tuple, quote_str, enc_quote
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write("<div style='width:640; margin: 15px; margin-left:auto; margin-right: auto'><h2><center>Encryptoquote - Decode the following encrypted quote.  All letters are substituted for one other.</center></h2></div>")
            self.wfile.write("<div style='border:2px solid black;margin: 15px; padding: 15px; width:640;margin-left:auto; margin-right:auto'>")
            self.wfile.write("<div style='font-family: monospace; font-size: 18px'>")
            for c in enc_quote:
                self.wfile.write("""<span onclick="alert('%s');">""" % c + c + "</span>")
            #self.wfile.write(enc_quote)
            self.wfile.write("<p>")
            dashes = []
            for c in enc_quote:
                if c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    dashes.append(c)
                else:
                    dashes.append('_')
            self.wfile.write(''.join(dashes))
            self.wfile.write('<p></div>')
            self.wfile.write("""<span id='soution_link_span'><a href="#solution" id='solution_link' onclick="solution_div = document.getElementById('solution'); solution_div.style.visibility = 'visible'; solution_link_span = document.getElementById('solution_link_span'); solution_link_span.innerHTML = 'Click to hide this solution.'"><u>Click here to see solution.</u></a>""");
            self.wfile.write("<div id='solution' style='visibility: hidden; font-family: monospace; font-size: 18px'><p>")
            self.wfile.write(quote_tuple[0])
            self.wfile.write("<br>")
            self.wfile.write("-- " + quote_tuple[1])
            self.wfile.write("</div></div></div>")
            self.wfile.write("<center><a href='/quote.html'>Get another quote.</a></center>")
            self.wfile.flush()
            self.wfile.close()
            update_quote()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("404 - Page Not Found.")

def main():
    try:
        server = HTTPServer(('', 8080), MyHandler)
        drop_privileges()
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()
