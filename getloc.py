
import socket

# server used to get lat/long from ip addr
LOC_HOST = {\
   'name':"www.geoplugin.net",\
   'port':80,\
   'page':"/json.gp",\
   'country_field':"geoplugin_countryName",\
   'city_field':"geoplugin_city",\
   'region_field':"geoplugin_regionName",\
   'lat_field':"geoplugin_latitude",\
   'long_field':"geoplugin_longitude"}
#mycontext['loc_port'] = 80
#mycontext['loc_page'] = "/json.gp"

# size of chunk to read from socket
READ_SIZE = 4096


# Continuously try to read from the socket until
#  either no more data is present, or the conn is closed
def recv_data(sock):

   data = ""
   try:	
      chunk = sock.recv(READ_SIZE)
      while (chunk != ""):
         data += chunk
         chunk = sock.recv(READ_SIZE)
			
   except Exception, e:
      if "Socket closed" not in str(e):
         raise
		
   return data


# Gets the lat/long from an ip addr by sending an http request to 
#  a geolocation server, Returns the lat and long 
def get_location(ip=None, server=LOC_HOST):

   if ip is None:
      ip_req = ""
   else:
      ip_req = "?ip=" + ip

   loc = {}
   try:
      sock = socket.create_connection((server['name'], server['port']))
  
      http_req = "GET " + server['page'] + ip_req + " HTTP/1.0\r\n\r\n"
      sock.send(http_req)

      html = recv_data(sock)
      sock.close()

      fields = html.split(',')
      for field in fields:
         if server['city_field'] in field:
            loc['city'] = field.split(':')[1]
         elif server['region_field'] in field:
            loc['region'] = field.split(':')[1]
         elif server['country_field'] in field:
            loc['country'] = field.split(':')[1]
      
   except Exception, e:
      print "error getting location!", type(e), str(e)

   return loc


def stringify_location(loc):
    
    s = ""
    try:
        s += loc['city']
    except KeyError:
        None
    try:
        s += ", "+loc['region']
    except KeyError:
        None
    try:
        s += ", "+loc['country']
    except KeyError:
        None

    return s

