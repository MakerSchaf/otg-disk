#!/usr/bin/gawk -f
#


BEGIN {
	# All access must below _base_address.  Set to `/` to allow
	# everywhere.
	_base_address = "/uploads/";

	# If PATH_INFO / PATH_TRANSLATED points to a directory that
	# does not exist, it is created when the parameter is `1`.
	_create_directories = 1;

	# Replace blanks in files with dashes.
	_replace_blanks = 1;

	# Create upload log files.
	_write_logs = 1;
	}


function skipws(s) {
	sub(/^[ \t\r\n]+/, "", s);
	return (s);
	}

function noctrl(s) {
	sub(/[ \t\r\n]+$/, "", s);
	return (s);
	}

function sq(s) {
	gsub(/'/, "'\\''", s);
	s = "'" s "'";
	return (s);
	}

function escape(s) {
	gsub(/&/, "\\&amp;", s);
	gsub(/</, "\\&lt;", s);
	gsub(/>/, "\\&gt;", s);
	gsub(/"/, "\\&quot;", s);
	return (s);
	}

#
# senderror() sends an error response to the client.
#

function senderror(s) {
	printf ("Status: %d\n" \
		"\n", (s == ""? 404: s));
	exit (0);
	}


# sendfile() tells http-server to send the file fn
# to the client and terminates the handler script.

function sendfile(fn) {
	printf ("Status: 200\n" \
		"Filename: %s\n" \
		"\n", fn);
	exit (0);
	}


#
# sendtext() send text to the client.
#

function sendtext(text, type) {
	if (type == "")
		type = "text/html";

	printf ("Status: 200\n" \
		"Content-Type: %s\n" \
		"\n" \
		"%s", type, text);
	return (0);
	}


#
# Construction of HTML pages.
#

function getDirNavigator(   i, n, p, url, x, T) {
	p = "<a href=\"" ENVIRON["SCRIPT_NAME"] "/\">Home</a>";

	n = split(ENVIRON["PATH_INFO"], x, "/");
	url = ENVIRON["SCRIPT_NAME"] "/";
	for (i = 2; i < n; i++) {
		url = url x[i] (i < n? "/": "");
		p = p sprintf (" | <a href=\"%s\">%s</a>",
				url, x[i]);

		}

	p = p " - <a href=\"#upload\">Upload</a>\n";
	return (p);
	}

function getNavigator(   T) {
	T = "<table valign=\"top\" class=\"nav\"" \
		" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\">\n" \
		"<tr>\n" \
		"<td style=\"padding: .1em; padding-left: .3em;\">" getDirNavigator() "</td>" \
		"<td>" "&nbsp;" "</td>" \
		"</tr>\n" \
		"</table>\n";

	return (T);
	}

function getUploadForm(   T) {
	T = "<A ID=\"upload\"></A>\n" \
		"<center>\n" \
		"<form action=\"" ENVIRON["SCRIPT_NAME"] ENVIRON["PATH_INFO"] "\"\n" \
		"    method=\"POST\" enctype=\"multipart/form-data\">\n" \
		"  <input type=\"file\" id=\"files\" name=\"files\" multiple=\"multiple\">\n" \
		"  <input type=\"submit\">\n" \
		"</form>\n" \
		"</center>\n";

	return (T);
	}

function getHtml(body,   T) {
	T = "<HTML>\n" \
		"<HEAD>\n" \
		"  <!-- software: request-handler -->\n" \
		"  <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">\n" \
		"  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" \
		"  <title>" pageTitle "</title>\n" \
		"<STYLE TYPE=\"text/css\">\n" \
		"    A:link, A:visited { text-decoration: none; color: blue; }\n" \
		"    A:hover { color: #00FF00; }\n" \
		"    A:focus { outline: none; border: 1px solid red; background: #E0E0E0; }\n" \
		"\n" \
		"    BODY { color: #000000; background: #FFFFFF; max-width: 400; }\n" \
		"    BODY, P, DIV, TD, TH, SELECT, INPUT { font-family: Verdana, Georgia, Helvetica, Arial, sans-serif; font-size: 11pt; }\n" \
		"    P, FORM { display: block; line-height: 1.5; }\n" \
		"    DIV.label { padding-top: .5em; }\n" \
		"    PRE { font-family: \"courier new\" monospace; margin-left: 1em; margin-right: 3em; }\n" \
		"\n" \
		"    BODY { padding-top: 1.5em; }\n" \
		"    DIV.item { font-size: 100%; padding: .2em; white-space: nowrap; overflow: hidden; }\n" \
		"    TABLE.nav { position: fixed; top: 1px; padding: 2px 10px 2px 0; background: rgb(240, 255, 240); }\n" \
		"</STYLE>\n" \
		"<X-LINK HREF=\"wiki.css\" REL=\"stylesheet\" type=\"text/css\">\n" \
		"</HEAD>\n" \
		"<BODY>\n" \
		getNavigator() \
		"\n" \
		body \
		"\n" \
		"<P><HR SIZE=\"1\">\n" \
		getUploadForm() \
		"\n" \
		"</BODY>\n" \
		"</HTML>\n";

	return (T);
	}



#
# Functions to decode CGI input
#

function cgidecode(str,   k, x, result) {
	hex = "123456789ABCDEF";
	result = "";
	gsub(/+/, " ", str);
	while ((k = index(str, "%")) > 0) {
		result = result substr(str, 1, k-1);
		str = substr(str, k+1);
		x = index(hex, substr(str, 1, 1)) * 16 + index(hex, substr(str, 2, 1));
		result = result sprintf ("%c", x);
		str = substr(str, 3);
		}

	result = result str;
	return (result);
	}

function getcgivars(querystring,   i, k, n, x, name, val) {
	delete CGIVAR;
	n = split(querystring, x, "&");
	for (i=1; i<=n; i++) {
		if ((k = index(x[i], "=")) > 0) {
			name = "CGI_" toupper(substr(x[i], 1, k-1));
			val = cgidecode(substr(x[i], k+1));
			if ((name in CGIVAR)  &&  CGI[name] != "")
				CGI[name] = CGI[name] ", " val;
			else
				CGI[name] = val;

			CGIVAR[name] = 1;
			}
		}

	return (0);
	}


# Check if the path is below _base_address.

function check_path(   path_info) {

	path_info = ENVIRON["PATH_INFO"];

	# No leading dots in filenames.
	if (index(path_info, "/.") > 0)
		senderror(400);

	# Check the path.
	else if (_base_address != ""  &&
	         substr(path_info, 1, length(_base_address)) != _base_address) {
		location = ENVIRON["SCRIPT_NAME"] _base_address;

		printf ("Status: %s\n", 302);
		printf ("Content-Type: %s\n", "text/html");
		printf ("Location: %s\n", location);

		printf ("\n");

		printf ("<A HREF=\"%s\">%s</A>\n", location, location);
		printf ("\n");

		exit (0);
		}

	return (0);
	}

function readCgi(   cmd, POSTDATA) {
	if (ENVIRON["REQUEST_METHOD"] == "GET")
		getcgivars(ENVIRON["QUERY_STRING"]);
	else if (ENVIRON["REQUEST_METHOD"] == "POST") {
		if (ENVIRON["CONTENT_TYPE"] ~ /^multipart\/form-data/)
			;
		else {
			cmd = sprintf ("dd bs=1 count='%d' 2>/dev/null", ENVIRON["CONTENT_LENGTH"]);
			if (debug)
				printf ("cmd= %s\n", cmd) >>STDERR;

			cmd | getline POSTDATA;
			close(cmd);
			getcgivars(POSTDATA);
			ENVIRON["REQUEST_METHOD"] = "GET";
			}
		}

	# Make sure we have a request path.
	if (ENVIRON["PATH_INFO"] == "")
		ENVIRON["PATH_INFO"] = "/";

	# busybox does not set PATH_TRANSLATED.
	if (ENVIRON["PATH_TRANSLATED"] == ""  &&
	    ENVIRON["SERVER_SOFTWARE"] ~ /busybox/) {
	    	val = ENVIRON["SCRIPT_FILENAME"];
		if ((k = index(val, "/cgi-bin/")) > 0) {
			val = substr(val, 1, k - 1) ENVIRON["PATH_INFO"];
			ENVIRON["PATH_TRANSLATED"] = val;
			# printf ("path_translated= %s\n", ENVIRON["PATH_TRANSLATED"]) >>STDERR;
			}
		}

	return (0);
	}


#
# Functions to create a directory listing.
#

function getDirectory(path,   line, cmd, fn, type, perm, p, x,
		i, n, nd, dir, nf, file,
		bn, urlPath, is_script, readmeFile, T) {

	urlPath = ENVIRON["SCRIPT_NAME"] ENVIRON["PATH_INFO"];

	# Create the find command ...
	cmd = sprintf ("find %s -maxdepth 1 -printf %s | sort ",
			path,
			sq("%P\\t%Y\\t%M\\t%p\\n"));

	# ... and read the directory listing.
	while (cmd | getline line > 0) {
		split(line, x, "\t");
		title = fn = x[1];
		type = x[2];
		perm = x[3];

		# Pickup the directory's readme file.
		if (fn == ".readme.html")
			readmeFile = fn;
		else if (readmeFile == ""  &&  fn == ".readme.txt")
			readmeFile = fn;


		# Check if the file should be displayed.
		if (x[1] == "")
			continue;

		# No leading dots, no tilde allowed
		else if (substr(fn, 1, 1) == "."  ||  fn ~ /~/)
			continue;

		if (type == "d") {
			dir[++nd] = title "\t" urlPath fn;
			}
		else if (type == "f") {
			file[++nf] = title "\t" ENVIRON["PATH_INFO"] fn;
			}
		}

	close (cmd);

	# Get the readme file.
	if (readmeFile != "") {
		while (getline line <readmeFile > 0)
			T = T line "\n";

		close (readmeFile);
		if (readmeFile !~ /\.html$/)
			T = "<PRE>" T "</PRE>\n";

		T = T "<P>\n";
		}


	# ... add directories ...
	n = asort(dir);
	for (i = 1; i <= n; i++) {
		split(dir[i], x, "\t");
		T = T sprintf ("<div class=\"item\">" \
				"<a href=\"%s/\">%s /</a></div>\n",
				x[2], x[1]);
		}

	# ... and the files.
	n = asort(file);
	for (i = 1; i <= n; i++) {
		split(file[i], x, "\t");
		T = T sprintf ("<div class=\"item\">" \
				"<a href=\"%s\">%s</a></div>\n",
				x[2], x[1]);
		}


	# Compute the page title for the directory (used by
	# getHtml()).
	p = ENVIRON["PATH_INFO"];
	if (p == "/")
		pageTitle = "Home";
	else {
		n = split(p, x, "/");
		pageTitle = x[n-1];
		}

	return (T);
	}


#
# Receiving files
#

function decodeHeader(line, header,   c, name, attr, val) {
	delete header;

	if (match(line, /^[^ \t:]+:/) == 0)
		return ("");

	name = substr(line, 1, RLENGTH-1);
	line = skipws(substr(line, RLENGTH+1));

	if (match(line, /[^;]*(;|$)*/) == 0)
		return ("");
		
	val = substr(line, 1, RLENGTH);
	sub(/[ \t]*;$/, "", val);
	header[""] = val;
	
	line = skipws(substr(line, RLENGTH+1));
	while (line != "") {
		if (match(line, /^[-A-Za-z0-9]+=/) == 0)
			break;

		attr = substr(line, 1, RLENGTH-1);
		line = skipws(substr(line, RLENGTH+1));
		if ((c = substr(line, 1, 1)) == "\"") {
			if (match(line, /^"[^"]*"([ \t]*;)?/) == 0)
				break;

			val = substr(line, 2);
			sub(/".*$/, "", val);
			line = skipws(substr(line, RLENGTH+1));
			}
		else {
			if (match(line, /^[^;]*(;|$)/) == 0)
				break;

			val = substr(line, 1, RLENGTH);
			sub(/;[ \t]*$/, "", val);
			line = skipws(substr(line, RLENGTH+1));
			}

		header[attr] = val;
		}

	name = tolower(name);
	return (name);
	}

function readPart(b1, b2, path,   i, p, name, header, var, val,
			filename, prevline, line) {
	var = "";
	while (getline line > 0) {
		line = noctrl(line);
		if (line == "")
			break;

		if ((name = decodeHeader(line, header)) != "") {
			if (name == "content-disposition") {
				var = header["name"];
				filename = p = header["filename"];
				if (_replace_blanks) {
					gsub(/[^-+_a-zA-Z0-9.()!]+/, "-", filename);
					gsub(/[-_]+/, "-", filename);
					}
				else if (filename != "") {
					sub(/^.*[\/\\]/, "", filename);
					sub(/^\.+/, "", filename);
					sub(/[^-+_\.A-Za-z0-9()!]/, "", filename);
					if (filename == "") {
						printf ("%s: empty filename: var= %s\n", program, var) >STDERR;
						exit (1);
						}
					}

				if (debug)
					printf ("%s --> %s\n", p, filename) >>STDERR;
				}
			}
		}

	if (line != "") {
		printf ("%s: broken input\n", program) >STDERR;
		exit (1);
		}
	else if (name == "") {
		# Finish if there's no variable name.
		return ("");
		}

	if (filename == "") {
		val = "";
		while (1) {
			if (getline line <= 0) {
				printf ("%s: broken input, var= %s\n", program, var) >STDERR;
				exit (1);
				}

			if (line == b1  ||  line == b2)
				break;

			val = val " " noctrl(line);
			}

		_text = _text sprintf (" - %s: %s\n", var, skipws(val));
		}
	else {
		basename = filename;
		filename = sprintf ("%s/%s", path, filename);
		sub(/\/+/, "/", filename);

		prevline = "\n";
		while (1) {
			if (getline line <= 0) {
				printf ("%s: broken input, var= %s\n", program, var) >STDERR;
				exit (1);
				}

			if (line == b1  ||  line == b2) {
				sub(/\r$/, "", prevline);
				printf ("%s", prevline) >filename;
				break;
				}

			if (prevline != "\n")
				printf ("%s\n", prevline) >filename;

			prevline = line;
			}

		close (filename);
		_text = _text sprintf (" - %s: %s\n", "file", basename);
		}

	return (line);
	}


function receiveFiles(path,   line, name, header, boundary, b2, n,
				cmd, fn, parts, T) {
	if (ENVIRON["CONTENT_TYPE"] == "") {
		printf ("%s: empty or unset content-type\n", program);
		senderror(404);
		}

	line = sprintf("content-type: %s", ENVIRON["CONTENT_TYPE"]);
	name = decodeHeader(line, header);
	if (name == "") {
		printf ("%s: error decoding header: %s\n", program, line);
		senderror(404);
		}
	else if (header["boundary"] == "") {
		printf ("%s: empty or unset boundary: %s\n", program, line);
		senderror(404);
		}

	boundary = "--" header["boundary"] "\r";
	b2 = "--" header["boundary"] "--\r";

	while (getline line > 0) {
		if (line == boundary)
			break;
		}

	if (_create_directories) {
		cmd = sprintf ("test -d %s  ||  mkdir -p %s",
				sq(path), sq(path));
		if (system(cmd) != 0) {
			senderror(500);
			exit (1);
			}
		}

	while (1) {
		line = readPart(boundary, b2, path);
		if (line != boundary)
			break;

		parts++;
		}

	if (_write_logs != 0) {
		if (parts > 1) {
			fn = sprintf ("%s/%s",
				path, strftime("%Y%m%d-%H%M%S.txt", systime()) );
			printf ("%s", _text) >fn;
			close (fn);
			}
		}

	printf ("Status: 302\n" \
		"Location: %s%s\n" \
		"\n",
		ENVIRON["SCRIPT_NAME"], ENVIRON["PATH_INFO"]);

	return (0);
	}



BEGIN {
	program = "file-server.cgi";
	STDERR = "/dev/stderr";
	IGNORECASE = 1;
	debug = 1;

	check_path();
	readCgi();

	METHOD = ENVIRON["REQUEST_METHOD"];
	if (METHOD == "POST") {
		PATH = ENVIRON["PATH_TRANSLATED"];
		# cmd = sprintf ("cat >%s/out.tmp", PATH);
		# print cmd >>STDERR;
		# system(cmd);
		# sendtext("ok.", "text/plain");
		receiveFiles(PATH);
		}
	else if (METHOD == "GET") {
		PATH = ENVIRON["PATH_TRANSLATED"];
		if (PATH ~ /\/$/) {
			T = getDirectory(PATH);
			sendtext( getHtml(T), "text/html");
			}
		else
			senderror(400);
		}
	else
		senderror(404);

	exit (0);
	}

