# coding: utf-8
#

import tornado
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.log import enable_pretty_logging
import hashlib


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

    def post(self):
        pass


class ImageHandler(tornado.web.RequestHandler):
    def get(self, name):
        pass

    def post(self):
        files = self.request.files.get("file")
        assert len(files) == 1
        f = files[0]
        print(f.keys())
        print(f['filename'], f['content_type'], 'size:', len(f['body']))

        with open("name.png", 'wb') as dst:
            dst.write(f['body'])
        m = hashlib.md5()
        m.update(f['body'])

        self.write({
            "success": True,
            "md5": m.hexdigest()
        })


def make_app(**settings):
    settings['template_path'] = 'templates'
    settings['static_path'] = 'static'
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/files/?", ImageHandler),
    ], **settings)


def main():
    enable_pretty_logging()

    app = make_app()
    print("Listen on port 7000")
    app.listen(7000)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
