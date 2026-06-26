import socks
import socket
import smtplib

sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
sock.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
sock.settimeout(10)
sock.connect(("smtp.gmail.com", 587))

server = smtplib.SMTP()
server.sock = sock
server.file = sock.makefile("rwb")

banner = server.getreply()
print(f"Banner: {banner}")

(code, msg) = server.ehlo()
print(f"EHLO code: {code}")
print(f"STARTTLS in features: {'starttls' in server.esmtp_features}")

server.quit()
