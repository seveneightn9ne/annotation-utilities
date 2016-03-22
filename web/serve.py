import SimpleHTTPServer
import SocketServer

import urlparse
#url = 'http://example.com/?q=abc&p=123'
#par = urlparse.parse_qs(urlparse.urlparse(url).query)

import training_data_searcher as tds

PORT = 8000

results_header = '''
<!DOCTYPE html>
<html>

<head>
	<meta charset="utf-8">
	<title>conllu.js</title>
	<meta name="viewport" content="width=device-width">
	<meta name="description" content="CoNLL-U format library for JavaScript">

	<link rel="stylesheet" href="http://spyysalo.github.io/conllu.js/css/jquery-ui-redmond.css">
	<link rel="stylesheet" href="http://spyysalo.github.io/conllu.js/css/main.css">
	<link rel="stylesheet" href="http://spyysalo.github.io/conllu.js/css/style-vis.css">

	<style>
		body {
			margin: 20px;
		}
		pre.embedding {
			margin-bottom: 20px;
		}
		#search-results-header {
			background-color: lightblue;
			padding: 10px;
		}
		.result {
			padding: 10px;
			background-color: #e9e9e9;
		}
		.matched-word {
			background-color: lightgreen;
		}
	</style>

	<script type="text/javascript" src="http://spyysalo.github.io/conllu.js/lib/ext/head.load.min.js"></script>
</head>

<body>
  
<article class="entry-content">
'''

results_footer = '''
<!-- XXX -->

</article>

</body>

<script type="text/javascript">
	var root = 'http://spyysalo.github.io/conllu.js/'; // filled in by jekyll
	head.js(
		// External libraries
		root + 'lib/ext/jquery.min.js',
		root + 'lib/ext/jquery.svg.min.js',
		root + 'lib/ext/jquery.svgdom.min.js',
		root + 'lib/ext/jquery-ui.min.js',
		root + 'lib/ext/waypoints.min.js',

		// brat helper modules
		root + 'lib/brat/configuration.js',
		/* root + 'lib/brat/util.js', */
		'util.js',
		root + 'lib/brat/annotation_log.js',
		root + 'lib/ext/webfont.js',
		// brat modules
		root + 'lib/brat/dispatcher.js',
		root + 'lib/brat/url_monitor.js',
		root + 'lib/brat/visualizer.js',

		// annotation documentation support
		'http://spyysalo.github.io/annodoc/lib/local/annodoc.js',
		root + 'lib/local/config.js',

		// the conllu.js library itself
		root + 'conllu.js'
	);

	var webFontURLs = [
		root + 'static/fonts/PT_Sans-Caption-Web-Regular.ttf',
		root + 'static/fonts/Liberation_Sans-Regular.ttf'
	];

	/* not used here */
	var documentCollections = {};

	head.ready(function() {
	// performes all embedding and support functions
	Annodoc.activate(Config.bratCollData, documentCollections);
	});
</script>

</html>
'''

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		#self.wfile.write(self.path)
		print "hi, I'm handling a get"
		print self.path
		if 'search=' in self.path:
			parsed_args = urlparse.parse_qs(urlparse.urlparse(self.path).query)
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			search_phrase = " ".join(parsed_args['search'])
			self.wfile.write(results_header)
			self.wfile.write(tds.search_corpus(search_phrase))
			self.wfile.write(results_footer)

			return
		else:
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


httpd = SocketServer.ThreadingTCPServer(("", PORT), MyRequestHandler)
print "serving at port", PORT

httpd.serve_forever()