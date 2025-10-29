from flask import Flask  # pyright: ignore[reportMissingImports]
from flask import redirect, request, url_for

app = Flask(__name__)

#route
@app.route('/')
def home():
     return f"Visit the <a href='{url_for('about')}'>About</a> page."
 

@app.route('/about')
def about():
    return "This is the about page."

#dynamic route
@app.route('/user/<name>')
def user(name):
    return f"Hello, {name}!"

#dynamic route
@app.route('/add/<int:a>/<int:b>')
def add(a, b):
    return f"The sum of {a} and {b} is {a + b}."
    
#query string
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"You searched for: {query}"

#redirection
@app.route('/redirect')
def redirect_page():
      return redirect(url_for('about')) 

#http methods
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        return "Form Submitted!"
    return "Submit Form Page"

#Run
if __name__ == '__main__':
    app.run(debug=True)
