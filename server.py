from flask import Flask, Response
from gensim.models.word2vec import Word2Vec
import json
import getopt
import sys
import numpy as np

app = Flask('word2vec')

@app.route("/")
def hello():
    return "ok"
    
@app.route("/hc")
def health_check():
    return "ok"

@app.route('/v/<word>')
def get_vectors_for_word(word):
    vec = []

    print word
    try:
        word = word.lower()
        vec = model[word].tolist()
    except Exception, e:
        print "Error {}".format(e)
        pass

    return Response(json.dumps(list(vec)), mimetype='application/json')

def get_word_vectors(words):
    words = [word.strip().lower() for word in words]
    res = dict()

    for w in words:
        try:
            res[w] = model[w].tolist()
        except Exception, e:
            res[w] = []
            print "Error {}".format(e)
            pass

    return res

@app.route('/vs/<words_str>')
def get_vectors_for_words(words_str):
    words = words_str.split(",")
    res = get_word_vectors(words)
    return Response(json.dumps(res), mimetype='application/json')

@app.route('/mean/<words_str>')
def mean_vector_for_words(words_str):
    words = words_str.split(",")
    d = get_word_vectors(words)
    vecs = [v for v in d.values() if v]
    if vecs:
        mean = np.array(vecs).mean(axis=0)
    else:
        mean = []
    return Response(json.dumps(list(mean)), mimetype='application/json')

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "p:v", ['port='])
    port = None
    for opt, arg in opts:
        if opt in ('-p', '--port'):
            port = arg
    print port

    global model
    print "loading model..."
    #model = Word2Vec.load_word2vec_format('./GoogleNews-vectors-negative300.bin.gz', binary=True, unicode_errors='ignore')
    model = Word2Vec.load_word2vec_format('./glove.6B.50d.txt', binary=False, unicode_errors='ignore')
    print "done loading model."

    print "starting server..."

    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()

    ##app.debug = True
    #app.run(host='0.0.0.0', port=port)
