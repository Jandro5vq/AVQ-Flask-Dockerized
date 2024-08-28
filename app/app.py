from flask import Flask
import pymysql

app = Flask(__name__)

@app.route('/')
def hello():
    return "==="

if __name__ == '__main__':
    app.run(host='0.0.0.0')