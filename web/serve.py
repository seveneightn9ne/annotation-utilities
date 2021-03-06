import SimpleHTTPServer
import SocketServer
import traceback
import datetime

import urlparse
#url = 'http://example.com/?q=abc&p=123'
#par = urlparse.parse_qs(urlparse.urlparse(url).query)

import training_data_searcher as tds

PORT = 8080

results_header = '''
<!DOCTYPE html>
<html>

<head>	
    <title>TLE</title>	
    <link rel="stylesheet" href="http://spyysalo.github.io/conllu.js/css/jquery-ui-redmond.css">
    <link rel="stylesheet" href="http://spyysalo.github.io/conllu.js/css/main.css">
    <link rel="stylesheet" href="http://spyysalo.github.io/conllu.js/css/style-vis.css">
    <link rel="stylesheet" type="text/css" href="searchstyle.css">
    <script type="text/javascript" src="http://spyysalo.github.io/conllu.js/lib/ext/head.load.min.js"></script>
    <script src="jsfunctions.js"></script>
'''

insert_javascript_esl = '''
	<script type="text/javascript"> window.onload = function() {
  		document.getElementById('corpus_list').getElementsByTagName('option')[0].selected = 'selected'; 
	};</script>'''

insert_javascript_eng = '''
	<script type="text/javascript"> window.onload = function() {
  		document.getElementById('corpus_list').getElementsByTagName('option')[1].selected = 'selected'; 
	};</script>'''

results_header_end = '''
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
		print self.path
		if 'search=' in self.path:
			try:
				parsed_args = urlparse.parse_qs(urlparse.urlparse(self.path).query)
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				try:
					search_phrase = " ".join(parsed_args['search'])
				except KeyError as e:
					search_phrase = ""
				corpus = parsed_args['corpus'][0]
				error = parsed_args['error'][0]
				if 'corr' in parsed_args:
					show_corr = True
				else:
					show_corr = False
                                if 'triplet' in parsed_args:
					triplet_match = True
				else:
					triplet_match = False

				with open('index.html', 'r') as searchPageFile:
					searchPageText = searchPageFile.read().strip()

				searchPageBody = searchPageText[searchPageText.find("<body>")+6:searchPageText.find("</body>")]

				self.wfile.write(results_header)
				if corpus == 'esl':
					self.wfile.write(insert_javascript_esl)
				else:
					self.wfile.write(insert_javascript_eng)
				self.wfile.write(results_header_end)
				self.wfile.write(searchPageBody)
				self.wfile.write(tds.search_corpus(search_phrase, triplet_match, error, corpus, show_corr))
				self.wfile.write(results_footer)
			except Exception as e:
				errorFile = open("error.log","a")
				errorFile.write("================\n")
				errorFile.write(str(datetime.datetime.now())+"\n")
				errorFile.write("================\n")

				traceback.print_exc(file=errorFile)

				errorFile.write("\n\n\n")

			return
		else:
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


httpd = SocketServer.ThreadingTCPServer(("", PORT), MyRequestHandler)
print "serving at port", PORT

httpd.serve_forever()
