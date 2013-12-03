import string
import random
import tornado.ioloop
import tornado.web
import tornado.gen
import tornadoredis
import msgpack
from redis import StrictRedis

c = tornadoredis.Client()
c.connect()
r = StrictRedis()

class StormyRedirectHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@tornado.gen.engine
	def get(self, id):
		key = '%s%s' % (self.request.host, self.request.uri)
		self.redirect(r.get(key))
		yield tornado.gen.Task(c.lpush, 'list_%s' % key, msgpack.packb(self.request.headers))

class StormyGeneratorHandler(tornado.web.RequestHandler):
	@tornado.gen.engine
	def post(self):
		digestive = self._randomString()
		key = '%s/%s' % (self.request.host, digestive)
		r.set(key, self.get_argument('target'))

	def _randomString(self, size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for x in xrange(size))

application = tornado.web.Application([
	(r"/generate", StormyGeneratorHandler),
	(r"/(.*)", StormyRedirectHandler)
])

if __name__ == "__main__":
	import sys
	application.listen(sys.argv[1])
	tornado.ioloop.IOLoop.instance().start()
