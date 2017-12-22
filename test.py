import os, sys, hashlib

str = 'http://image.bitautoimg.com/bt/car/default/images/logo/masterbrand/png/100/m_9_100.png'
print hashlib.sha1(str).hexdigest()
print hashlib.sha1(str).digest()
print hashlib.sha1(str)
