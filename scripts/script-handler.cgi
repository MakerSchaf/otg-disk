#!/usr/bin/gawk -f
#


BEGIN {
	# All requests must start with base_address.  Assign a
	# value to limit the script's area of access.
	base_address = "/script-handler/";

	# Set to `1` if the server understand the non-standard
	# `Filename:` response header.
	have_sendfile = 0;
	}

function usage() {
	print "\n" \
		"  Input controls and script attributes are read from the first two\n" \
		"  `#`-comment blocks in the script file to create an HTML input\n" \
		"  form.\n" \
		"\n" \
		"  Script Attributes\n" \
		"\n" \
		"      :name <text>		display <text> in HTML listing.\n" \
		"      :title <title>		set title for HTML form and output.\n" \
		"      :content-type <type>	set content-type other then text/plain\n" \
		"    				(default); use `.` if the script provides\n" \
		"				the content-type.\n" \
		"      :is-script		mark script as executable in case it does\n" \
		"    				not contain any input elements.\n" \
		"      :( <script> )		read input controls definitions from\n" \
		"      				<script>'s output; use `$0` to run the\n" \
		"				script itself.\n" \
		"\n" \
		"    Lines without a leading `:` are inserted as HTML.\n" \
		"\n" \
		"  Input Controls\n" \
		"\n" \
		"    Input controls require type, name and optional default value.\n" \
		"\n" \
		"      :auth <name> <value>	create a password field and verify the\n" \
		"    				submitted data against the contents of\n" \
		"				.script.auth in the script's directory.\n" \
		"      :check <name> <value>	create checkbox <name> with value <text>.\n" \
		"      :checkbox <name> <value>	same as :check.\n" \
		"      :hidden <name> <value>	hidden input field.\n" \
		"      :label <name> <text>	display <text> as label for control\n" \
		"    				<name>.\n" \
		"      :number <name> <text>	number input control.\n" \
		"      :password <name> <value>	password input control.\n" \
		"      :radio <name>  <value>	radio control.\n" \
		"      :range <name> <value>	range input control.\n" \
		"      :select <name> <value>	create selection <name> and fill it\n" \
		"				with <value> which is a comma/blank\n" \
		"				separated list of <key>:<value> pairs.\n" \
		"      :text <name> <text>	text input control.\n" \
		"\n" \
		"  Control Options\n" \
		"\n" \
		"    Control options can be inserted after the control's name\n" \
		"    and parameter.\n" \
		"\n" \
		"      Boolean options:		--autofocus, --checked, --disabled,\n" \
		"    				--multiple, --readonly, --required\n" \
		"\n" \
		"      Options with parameter:	--autocomplete=, --min=, --max=,\n" \
		"    				--maxlength=, --pattern=, --placeholder=,\n" \
		"				--size=, --step=\n" \
		"\n" \
		"    Options are not checked for their compatibility with the input\n" \
		"    control.\n" \
		"\n";

	exit (0);
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
		"Content-Type: %s; charset= utf-8\n" \
		"\n" \
		"%s", type, text);
	return (0);
	}



#
# Function to read the script's header and to convert
# it into an HTML form.
#

function readHeader(fn,    n, line, T, p, x, block) {
	delete _have_datalist;
	isScript = 0;
	pageTitle = scriptName = contentType = "";

	block = 1;
	while (getline line <fn > 0) {
		if (line !~ /^#/) {
			if (line != "")
				break;

			block++;
			if (block > 2)
				break;
			}

		line = noctrl(line);
		while (line ~ /\\$/) {
			if (getline p <fn <= 0)
				break;
			else if (p !~ /^#[ \t]+/)
				break;

			line = noctrl(substr(line, 1, length(line) - 1)) \
				" " skipws( substr(p, 2));
			}

		if (line ~ /^#[ \t]+:is-script/)
			isScript = 1;
		else if (match(line, /^#[ \t]+:(title|content-type|name)[ \t]+(.*)$/, x) > 0) {
			p = x[1];
			if (p == "title") {
				pageTitle = x[2];
				continue;
				}
			else if (p == "content-type") {
				contentType = x[2];
				continue;
				}
			else if (p == "name") {
				scriptName = x[2];
				continue;
				}
			}
		else if (match(line, /^#[ \t]+:\((.*)\)$/, x) > 0) {
			# Interpret output from shell command
			T = T "( " skipws(x[1]) "\n";
			}
		else {
			if (match(line, /^#[ \t]+:(.*)$/, x) > 0) {
				T = T x[1] "\n";
				if (match(x[1], /^([^ \t]+)[ \t]+([^ \t]+)/, x) > 0) {
					p = tolower(x[1]);
					if (p == "datalist")
						_have_datalist[x[2]] = 1;
					else if (p == "html")
						;
					else if (p == "auth")
						_auth_variable = x[2];
					else if (x[2] ~ /^[_a-z0-9]+$/)
						_have_input[x[2]] = 1;
					}
				}
			else if (0  &&  match(line, /^#[ \t]+:(.*)$/, x) > 0) {
				T = T x[1] "\n";

				# Preparsing for makeForm()
				p = x[1];
				if (match(p, /datalist[ \t]([-a-z0-9]+)/, x))
					_have_datalist[x[1]] = 1;
				}
			else if (match(line, /^#[ \t]+([^ \t]+.*)$/, x) > 0)
				T = T "html " x[1] "\n";
			}
		}

	close (fn);
	return (T);
	}


#
# Substitute any "( <cmd>" sequences by their command output.
#

function shellSubst(T,   i, n, cmd, line, Q, x) {
	n = split( noctrl(T), x, "\n");
	Q = ""
	for (i = 1; i <= n; i++) {
		if (substr(x[i], 1, 2) == "( ") {

			#
			# Execute the shell command and read the
			# output.
			#

			cmd = skipws( substr(x[i], 2));
			if (substr(cmd, 1, 2) == "$0")
				cmd = FILE substr(cmd, 3);

			while (cmd | getline line > 0) {
				if (line ~ /^:[a-z]/)
					Q = Q substr(line, 2) "\n";
				}

			close (cmd);
			continue;
			}
		else
			Q = Q x[i] "\n";
		}

	return (Q);
	}


function get(pattern, string, arr,  a) {
	pattern = "^[ \t]*(" pattern ")([ \t]+(.*)$)?";
	if (match(string, pattern, a) == 0)
		return ("");

	arr[2] = a[3];
	return (arr[1] = a[1]);
	}

function __default(var, def,   val) {
	var = "CGI_" toupper(var);
	val = (var in CGI)? CGI[var]: def;
	return (val);
	}

function __checked(var, val, opt, keyword,   i, n, x) {
	if (keyword == "")
		keyword = "checked";

	var = "CGI_" toupper(var);
	if (! (var in CGI))
		return (opt == 1? " " keyword: "");
	else if (val == "")
		return ("");

	n = split(tolower(CGI[var]), x, / *, */);
	val = tolower(val);
	for (i = 1; i <= n; i++) {
		if (val == x[i])
			return (" " keyword);
		}

	return ("");
	}

function makeForm(text,   i, j, n, m, p, s, arr, x, y, z,
			type, name, var, value, opt, checked, T) {
	n = split(noctrl(text), x, "\n");
	for (i = 1; i <= n; i++) {
		p = x[i];
		if ((type = get("[-a-zA-Z0-9]+", p, arr)) == "")
			continue;

		if (type == "html") {
			T = T arr[2] "\n";
			continue;
			}
		else if (type == "code"  ||  type == "pre") {
			T = T "<CODE>" arr[2] "</CODE><BR>\n";
			continue;
			}

		if ((name = get("[-a-zA-Z0-9]+", arr[2], arr)) == "")
			continue;

		opt = "";
		checked = 0;
		while ((p = get("--[-a-z]+[^ \t]*", arr[2], arr)) != "") {
			if (match(p, /^--([-a-z]+)(=(.*))?/, y) == 0)
				continue;

			p = tolower(y[1]);
			if (p ~ /^(autocomplete|min|max|maxlength|pattern|placeholder|size|step)$/)
				opt = opt sprintf (" %s=\"%s\"", p, escape(y[3]));
			else if (p ~ /^(autofocus|disabled|multiple|readonly|required)$/)
				opt = opt sprintf (" %s", p);
			else if (p == "checked")
				checked = 1;
			}

		if (name in _have_datalist)
			opt = opt " " sprintf (" list=\"%s-list\"", name);

		if (type == "label") {
			T = T sprintf("  <div class=label><label for=\"%s\">%s</label></div>\n",
					name, arr[2]);
			}
		else if (type ~ /^(text|password|number|range|hidden)$/) {
			T = T sprintf("  <input type=\"%s\" id=\"%s\" name=\"%s\" value=\"%s\"%s><br>\n",
					toupper(type),
					name, name, escape( __default(name, arr[2])), opt);
			}
		else if (type == "auth") {
			T = T sprintf("  <input type=\"password\" id=\"%s\" name=\"%s\" value=\"%s\"%s><br>\n",
					name, name, escape( __default(name, arr[2])), opt);
			}
		else if (type == "check"  ||  type == "checkbox") {
			value = get("[^ ]+", arr[2], arr);
			T = T sprintf("  <input type=\"CHECKBOX\" id=\"%s\" name=\"%s\" value=\"%s\"%s>\n",
					name, name,
					escape(value), __checked(name, value, checked));
			T = T sprintf("  <label for=\"%s\">%s</label><br>\n",
					escape(value), arr[2]);
			}
		else if (type == "radio") {
			value = get("[^ ]+", arr[2], arr);
			T = T sprintf("  <input type=\"RADIO\" id=\"%s\" name=\"%s\" value=\"%s\"%s>\n",
					name, name,
					escape(value), __checked(name, value, checked));
			T = T sprintf("  <label for=\"%s\">%s</label><br>\n",
					escape(value), arr[2]);
			}
		else if (type == "select") {
			s = sprintf ("  <select id=\"%s\" name=\"%s\"%s>\n",
					name, name, opt);

			m = split(arr[2], arr, / *, */);
			for (j = 1; j <= m; j++) {
				split(arr[j], y, ":");
				if (y[2] == "")
					y[2] = y[1];

				s = s sprintf ("    <option value=\"%s\"%s>%s</option>\n",
					y[1], __checked(name, y[1], 0, "selected"), y[2]);
				}

			s = s "  </select><br>\n";
			T = T s;
			}
		else if (type == "datalist") {
			s = sprintf ("  <datalist id=\"%s-list\">\n", name);
			m = split(arr[2], arr, / *, */);
			for (j = 1; j <= m; j++) {
				s = s sprintf ("    <option value=\"%s\">\n",
					escape(arr[j]));
				}

			s = s "  </datalist>\n";
			T = T s;
			}
		else if (type == "list") {
			T = T sprintf("  <input list=\"%s\" name=\"%s\" value=\"%s\"%s><br>\n",
					toupper(type),
					name, escape( __default(name, arr[2])), opt);
			}
		}

	T = T sprintf ("  <p>\n" \
			"  <input type=\"SUBMIT\">\n" \
			"  <input type=\"RESET\"><br>\n");

	T = sprintf ("<form action=\"%s\" method=\"POST\">\n" \
			"  <input type=\"hidden\" name=\"_d\" value=\"1\">\n\n",
				ENVIRON["SCRIPT_NAME"] ENVIRON["PATH_INFO"]) \
		T \
		sprintf ("</form>\n");

	return (T);
	}



#
# Construction of HTML pages.
#

function getDirNavigator(   i, n, p, url, x, T) {
	p = "<a href=\"" ENVIRON["SCRIPT_NAME"] "/\">Home</a>";

	n = split(ENVIRON["PATH_INFO"], x, "/");
	url = ENVIRON["SCRIPT_NAME"] "/";
	for (i = 2; i <= n; i++) {
		if (x[i] == "")
			continue;

		url = url x[i] (i < n? "/": "");
		p = p sprintf (" | <a href=\"%s\">%s</a>",
				url, x[i]);

		}

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
		"    TABLE.nav { position: fixed; top: 1px; padding: 2px 10px 2px 0; background: rgb(255, 240, 240); }\n" \
		"</STYLE>\n" \
		"</HEAD>\n" \
		"<BODY>\n" \
		getNavigator() \
		"\n" \
		body \
		"\n" \
		"</BODY>\n" \
		"</HTML>\n";

	return (T);
	}



#
# Functions to decode CGI input
#

function cgi_decode(str,   k, x, result) {
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

function get_cgivars(querystring,   i, k, n, x, name, val) {
	delete CGIVAR;
	n = split(querystring, x, "&");
	for (i=1; i<=n; i++) {
		if ((k = index(x[i], "=")) > 0) {
			name = "CGI_" toupper(substr(x[i], 1, k-1));
			val = cgi_decode(substr(x[i], k+1));
			if ((name in CGIVAR)  &&  CGI[name] != "")
				CGI[name] = CGI[name] ", " val;
			else
				CGI[name] = val;

			CGIVAR[name] = 1;
			}
		}

	return (0);
	}

function read_cgi(   cmd, POSTDATA) {
	if (ENVIRON["REQUEST_METHOD"] == "GET")
		get_cgivars(ENVIRON["QUERY_STRING"]);
	else if (ENVIRON["REQUEST_METHOD"] == "POST") {
		if (ENVIRON["CONTENT_TYPE"] ~ /^multipart\/form-data/)
			;
		else {
			cmd = sprintf ("dd bs=1 count='%d' 2>/dev/null", ENVIRON["CONTENT_LENGTH"]);
			cmd | getline POSTDATA;
			close(cmd);
			get_cgivars(POSTDATA);
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
			val = substr(val, 1, k) ENVIRON["PATH_INFO"];
			ENVIRON["PATH_TRANSLATED"] = val;
			}
		}

	return (0);
	}


#
# Get and export the CGI environment, then run the
# script.
#

function runScript(path,   i, v, cmd, rc, line, fn, T) {

	if (_auth_variable != "") {
		# Compute the password filename.
		fn = path;  sub(/[^\/]+$/, "", fn);
		fn = fn ".script.auth";

		# Take the supplied password ...
		v = skipws( noctrl( CGI[toupper("CGI_" _auth_variable)] ));

		# ... and compare.
		getline line <fn;  close (fn);
		if (skipws(noctrl(line)) != v) {
			printf ("%s: password mismatch\n", path) >>STDERR;
			sendtext("Bad password.\n");

			exit (0);
			}
		}

	# Get CGI variables as defined in the script ...
	for (i in _have_input) {
		v = toupper("CGI_" i);
		cmd = cmd sprintf(" %s=%s", v, sq(CGI[v]));
		}

	# ... and complete the command line.
	cmd = substr(cmd, 2) " exec " path;

	# Set a default for the content-type.
	if (contentType == "")
		contentType = "text/plain";

	if (contentType == "text/plain") {

		# Output of text/plain scripts in collected and
		# wrapped into HTML.

		while (cmd | getline line > 0)
			T = T escape(line) "\n";

		rc = close(cmd);
		T = "<PRE>" T "</PRE>\n";
		sendtext( getHtml(T), "text/html");
		}
	else {
		if (contentType != ".") {
			printf ("Status: 200\n" \
				"Content-Type: %s\n" \
				"\n", contentType);
			}

		rc = system(cmd);
		}

	return (rc);
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
			# The filename must have a dot or the file is executable
			if (fn !~ /\./  &&  perm !~ /^-rwx/)
				continue;

			bn = fn;
			sub(/\.[^.]*$/, "", bn);

			# x[4] contains the full path to the file.
			p = readHeader(x[4]);
			if (scriptName != "")
				title = scriptName;
			else if (pageTitle != "")
				title = pageTitle;

			if (p != "")
				title = title " ...";

			p = pageTitle != ""? urlPath: ENVIRON["PATH_INFO"];
			file[++nf] = title "\t" p fn;
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


BEGIN {
	IGNORECASE = 1;
	STDERR = "/dev/stderr";

	if (ARGV[1] == "--help"  ||  ARGV[1] == "--usage")
		usage();

	# Check the request.
	path_info = ENVIRON["PATH_INFO"];
	if (index(path_info, "/.") > 0)
		senderror(400);
	else if (base_address != ""  &&
	         substr(path_info, 1, length(base_address)) != base_address) {
		location = ENVIRON["SCRIPT_NAME"] base_address;

		printf ("Status: %s\n", 302);
		printf ("Content-Type: %s\n", "text/html");
		printf ("Location: %s\n", location);

		printf ("\n");

		printf ("<A HREF=\"%s\">%s</A>\n", location, location);
		printf ("\n");

		exit (0);
		}


	read_cgi();
	FILE = ENVIRON["PATH_TRANSLATED"];

	if (FILE ~ /\/$/) {
		T = getDirectory(FILE);
		sendtext( getHtml(T), "text/html");
		}
	else {
		# Check if the file exists ...
		if (getline line <FILE < 0)
			senderror(404);

		close (file);

		# ... and if it is a script.
		if (line !~ /^#!\//)
			sendfile(FILE);

		# Read the FORM definition from the script's
		# first and second comment block.
		T = readHeader(FILE);
		if (T == ""  &&  isScript == 0)
			sendfile(FILE);

		# If data is available, run the script.
		if (isScript == 1  ||
		    ENVIRON["REQUEST_METHOD"] == "POST"  ||
		    ENVIRON["CGI__HD"] == 1) {
			runScript(FILE);
			}

		# ... otherwise create and send the input form.
		else {
			T = shellSubst(T);
			T = getHtml( makeForm(T));
			sendtext(T, "text/html");
			}
		}

	exit (0);
	}

