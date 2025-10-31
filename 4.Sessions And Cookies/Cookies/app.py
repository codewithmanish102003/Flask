from flask import Flask, make_response, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/setcookie')
def setcookie():
    response = make_response("Cookie is set")
    response.set_cookie('username', 'Manish')
    return response

@app.route('/getcookie')
def getcookie():
    name = request.cookies.get('username')
    return f'Welcome back, {name}!'

@app.route('/deletecookie')
def deletecookie():
    response = make_response("Cookie has been deleted")
    response.set_cookie('username', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(debug=True)
    
