from flask import Flask, render_template, request, jsonify
import marshal

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/api/suggest', methods=['POST', 'GET'])
def get_suggest():
    query = request.args.get('query', None)
    print query
    data = ['PHP', 'MySQL', 'SQL', 'PostgreSQL', 'HTML', 'CSS', 'HTML5', 'CSS3', 'JSON']
    result = {"status" : "Ok", 'result': data}
    return jsonify(**result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
