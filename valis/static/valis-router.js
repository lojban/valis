(function(root) {

  var Mn = root.Mn,
    app  = root.Valis;

  var ValisRouter = Mn.AppRouter.extend({

    routes: {
      ""                            : "showSearch",
      "valsi/:valsi"                : "showValsi",
      "valsi/:valsi/:language_code" : "showValsiDefinitions"
    },

    showSearch: function() {
      app.Dispatch.execute("search:show");
    },

    showValsi: function(valsi) {
      app.Dispatch.execute("valsi:load", valsi);
    },

    showValsiDefinitions: function(valsi, language) {
      app.Dispatch.execute("definitions:show", valsi, language);
    }

  });

  app.Router = new ValisRouter();

})(window);
