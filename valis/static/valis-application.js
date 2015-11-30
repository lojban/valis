(function(root) {

  var $ = root.jQuery,
    BB  = root.Backbone,
    Mn  = root.Mn;

 var ValisApplication = Mn.Application.extend({
    Collections: {},
    Models:      {},
    Views:       {},
    Utilities:   {}
  });

  var app = root.Valis = new ValisApplication();

  app.on("start", function() {
    app.Layout.render();
    BB.history.start({ root: "/ui/", pushState: true });
  });

  $(function() { app.start(); });

})(window);
