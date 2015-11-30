(function(root) {

  var Mn      = root.Mn,
    HB        = root.Handlebars,
    app       = root.Valis,
    Utilities = app.Utilities;

  Mn.TemplateCache.prototype.compileTemplate = function(template) {
    return HB.compile(template);
  };

  Handlebars.registerHelper("escapeValsi", function(valsi) {
    return Utilities.escapeValsi(valsi);
  });

  Handlebars.registerHelper("TeX", function(tex, options) {
    return Utilities.renderTex(tex, options.hash);
  });

  Handlebars.registerHelper("convert", function(place) {
    if (!place) { return ""; }
    return Utilities.conversionForPlace(parseInt(place));
  });

 Handlebars.registerHelper("commify", function(array) {
    return array.join(", ");
  });

})(window);
