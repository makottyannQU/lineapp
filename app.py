# -*- coding: utf-8 -*-
from apis import blueprint as api
from views import app

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
