(function(root) {

  var HB      = root.Handlebars,
    katex     = root.katex,
    app       = root.Valis,
    Utilities = app.Utilities;

  function renderTex(tex, options){
    var chunks = analyzeStringWithTex(tex);
    return renderAnalyzedStringWithTex(chunks, options);
  }

  function analyzeStringWithTex(tex) {
    var chars = tex.split(""),
      len = chars.length,
      escaping = false,
      math = false,
      start = 0,
      chunks = [];
    for (var i=0; i<len; i++) {
      var c = chars[i];
      if (c === "\\" && !escaping) {
        escaping = true;
      }
      else if ((c === "$") && !escaping) {
        if (math) {
          if ((start + 1) < i) {
            var chunk = chars.slice(start+1, i).join("");
            chunks.push([ true, chunk ]);
          }
          math = false;
          start = i+1;
        }
        else {
          if (start < i) {
            var chunk = chars.slice(start, i).join("");
            chunks.push([ false, chunk ]);
          }
          math = true;
          start = i;
        }
      }
    }
    if (start < len) {
      var chunk = chars.slice(start, len).join("");
      chunks.push([ math, chunk ]);
    }
    return chunks;
  }

  function renderAnalyzedStringWithTex(chunks, options) {
    var out = [],
      len = chunks.length;
    for(var i=0; i < len; i++) {
      var c = chunks[i];
      out.push(c[0] ? renderMathChunk(c[1]) : renderTextChunk(c[1], options));
    }
    return out.join("");
  }

  function renderMathChunk(content) {
    var out, content = normalizeTex(content);
    try {
      out = katex.renderToString(content, { throwOnError: false });
    }
    catch(err) {
      out = "<span class=\"valis-tex-error\">" + content + "</span>";
    }
    return out;
  }

  function normalizeTex(content) {
    content = content.replace(/\{−/g, "{-"); // e.g. avgadro
    return content;
  }

  function renderTextChunk(content, options) {
    content = HB.Utils.escapeExpression(content);
    var matcher = /\{([^\}]+)\}/g;
    return content.replace(matcher, function(__, valsi) {
      return "<a href=\"" + Utilities.valsiUrl(valsi, options) + "\">" + valsi + "</a>";
    });
  }

  Utilities.renderTex = renderTex;

})(window);
