from flask import Flask, request, jsonify, render_template

app = Flask(_name_)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if _name_ == '_main_':
    app.run(debug=True)