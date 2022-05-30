import os
from flask import Flask
import upload

app=Flask(__name__)
app.register_blueprint(upload.bp,url_prefix='/upload')
if __name__=='__main__':
    app.run()

