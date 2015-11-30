(function(root) {

  var app = root.Valis;

  function backendUri() {
    var components = _.toArray(arguments);
    components.unshift("api");
    return buildUri(components);
  }

  function buildUri(components) {
    components = _.map(components, function (arg) {
      return encodeURIComponent(arg);
    });
    return "/" + components.join("/");
  }

  function sortNumeric(numberStrings) {
    return numberStrings.sort(function (a, b) {
      var a1 = parseInt(a), b1 = parseInt(b);
      return ( a1 < b1 ) ? -1 : ( ( a1 > b1 ) ? 1 : 0 );
    });
  }

  function escapeValsi(valsi) {
    return valsi ? valsi.replace(/('|&#x27;)/g, "h") : valsi;
  }

  function valsiUrl(valsi, options) {
    var components = [ "valsi", escapeValsi(valsi) ];
    if ( options && options.language ) {
      components.push(options.language);
    }
    return buildUri(components);
  }

  // underscore debounce + "after" callback
  function debounceWithFollowup (func, wait, immediate, after) {
    var timeout, args, context, timestamp, result;

    var later = function() {
      var last = _.now() - timestamp;

      if (last < wait && last >= 0) {
        timeout = setTimeout(later, wait - last);
      } else {
        timeout = null;
        if (!immediate) {
          result = func.apply(context, args);
          if (!timeout) context = args = null;
        }
        if (after) after.call();
      }
    };

    return function() {
      context = this;
      args = arguments;
      timestamp = _.now();
      var callNow = immediate && !timeout;
      if (!timeout) timeout = setTimeout(later, wait);
      if (callNow) {
        result = func.apply(context, args);
        context = args = null;
      }

      return result;
    };
  }

  app.Utilities.backendUri  = backendUri;
  app.Utilities.sortNumeric = sortNumeric;
  app.Utilities.escapeValsi = escapeValsi;
  app.Utilities.valsiUrl    = valsiUrl;
  app.Utilities.debounce    = debounceWithFollowup;

})(window);
