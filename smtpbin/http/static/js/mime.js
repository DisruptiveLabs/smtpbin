function parseMIME(doc) {

  var lines = Array.isArray(doc) ? doc : doc.split('\n'),
      header_lines = [],
      body_lines = [],
      inHeader = true,
      headers, body;

  for (var i = 0, line = lines[0]; i < lines.length; line = lines[++i]) {
    console.log(inHeader ? 'header ' : '  body ', line);
    if (inHeader && line === '') {
      inHeader = false;
    } else if (inHeader) {
      if (line.startsWith(" ")) {
        header_lines[header_lines.length - 1] += line;
      }
      header_lines.push(line);
    } else {
      body_lines.push(line);
    }
  }

  // Convert headers to object
  headers = header_lines.reduce((a, e) => {
    var parts = e.split(":"), key = parts.shift().toLowerCase(), value = parts.join(":").trim();
    a[key] = value;
    return a
  }, {});

  var content_type = headers['content-type'];

  switch (content_type.split(";")[0]) {
    case 'multipart/alternative':
    case 'multipart/mixed':
      var boundary = content_type.match(/boundary="(.+)"/)[1],
          boundary_begin = "--" + boundary,
          boundary_end = "--" + boundary + "--",
          mime_messages = [],
          mime_message = null,
          inBody = false;

      for (var i = 1, line = body_lines[0]; i < body_lines.length; line = body_lines[i++]) {
        if (line === boundary_end) {
          break;
        } else if (line === boundary_begin) {
          inBody = true;
          mime_message = [];
          mime_messages.push(mime_message);
        } else if (inBody) {
          mime_message.push(line);
        }
      }

      body = mime_messages.map(parseMIME);
      break;

    case 'multipart/related':
    default:
      console.log("Unhandled content-type: " + content_type);
    case 'text/plain':
    case 'text/html':
      body = body_lines.join("\n");
      break;
  }

  return {headers, body}
}

console.log(JSON.stringify(parseMIME("" +
    "Content-Type: multipart/mixed; boundary=\"===============7133210628759955100==\"\n" +
    "MIME-Version: 1.0\n" +
    "Subject: Franklyn Tackitt (3-D Brokerage) commented on Invoice #4351 for\n" +
    " $74.95 at 3848 E. 32nd St, 2B, Tucson, AZ 85713\n" +
    "From: reply+bf4d8b2164b945e999377ef546b65321.a165885.66d11593af135d68318666590e6584cd91dfbf0a@reply.frankcmng.ngrok.io\n" +
    "To: donald.dempsey@3dbkg.com\nDate: Thu, 12 May 2016 11:10:14 -0700\n" +
    "Message-ID: <146307661352.15898.11449013716423752701@frank-lap>\n" +
    "Reply-To: reply+bf4d8b2164b945e999377ef546b65321.a165885.66d11593af135d68318666590e6584cd91dfbf0a@reply.frankcmng.ngrok.io\n" +
    "\n" +
    "--===============7133210628759955100==\n" +
    "Content-Type: multipart/alternative;\n" +
    " boundary=\"===============0107181265882323068==\"\n" +
    "MIME-Version: 1.0\n" +
    "\n" +
    "--===============0107181265882323068==\n" +
    "Content-Type: text/plain; charset=\"utf-8\"\n" +
    "MIME-Version: 1.0\n" +
    "Content-Transfer-Encoding: 7bit\n" +
    "\n" +
    "\n" +
    "--===============0107181265882323068==\n" +
    "Content-Type: text/html; charset=\"utf-8\"\n" +
    "MIME-Version: 1.0\n" +
    "Content-Transfer-Encoding: 7bit\n" +
    "\n" +
    "    <a href=\"http://frankcmng.ngrok.io/go/bf4d8b21-64b9-45e9-9937-7ef546b65321\">http://frankcmng.ngrok.io/go/bf4d8b21-64b9-45e9-9937-7ef546b65321</a>\n" +
    "\n" +
    "  <h3>\n" +
    "    <b>Franklyn Tackitt</b> <small>(3-D Brokerage)</small> has commented on\n" +
    "    <a href=\"http://frankcmng.ngrok.io/go/bf4d8b21-64b9-45e9-9937-7ef546b65321\">Invoice #4351 for $74.95 at 3848 E. 32nd St, 2B <small>Tucson, AZ 85713</small></a>\n" +
    "  </h3>\n" +
    "\n" +
    "  <blockquote>\n" +
    "    <p>test is a test</p>\n" +
    "  </blockquote>\n" +
    "\n" +
    "  <p style=\"font-size:.7em; color: #888888;\">\n" +
    "    <a href=\"http://frankcmng.ngrok.io/notifications/unsub/bf4d8b21-64b9-45e9-9937-7ef546b65321\">Click here to unsubscribe</a> from future emails\n" +
    "  </p>\n" +
    "\n" +
    "--===============0107181265882323068==--\n" +
    "\n" +
    "--===============7133210628759955100==--"), null, 2));

if (module) {
  module.exports = parseMIME;
}