(function(root) {

  var BB = root.Backbone,
    BW   = BB.Wreqr,
    app  = root.Valis;

  var Dispatch = BW.Commands.extend({

    initialize: function() {
      var dispatch = this;
      this.setHandler("search:show", function() {
        dispatch.showSearch();
      });
      this.setHandler("search:configure", function(params) {
        dispatch.configureSearch(params);
      });
      this.setHandler("search:push", function() {
        dispatch.pushSearch();
      });
      this.setHandler("valsi:load", function(valsi) {
        dispatch.loadValsi(valsi);
      });
      this.setHandler("definitions:show", function(valsi, language) {
        dispatch.showDefinitions(valsi, language);
      });
    },

    showSearch: function(query) {
      var queryParams = this.parseSearchParameters(),
        view = new app.Views.Search({
          query:    query || queryParams.query,
          mode:     queryParams.mode,
          type:     queryParams.type,
          language: queryParams.language
        });
      app.Layout.showChildView("input", view);
    },

    parseSearchParameters: function() {
      return _.pick(this.parseQueryParameters(),
                    "query", "mode", "type", "language");
    },

    parseQueryParameters: function() {
      var uri = new URI(window.location.href);
      return URI.parseQuery(uri.query());
    },

    configureSearch: function(params) {
      var outputView = this.currentOutputView();
      if (outputView instanceof app.Views.SearchResults) {
        outputView.trigger("search:configure", params);
      }
      else {
        this.showSearchResults(params);
      }
    },

    currentOutputView: function() {
      return app.Layout.getRegion("output").currentView;
    },

    showSearchResults: function(params) {
      var view = new app.Views.SearchResults(params);
      app.Layout.showChildView("output", view);
    },

    pushSearch: function() {
      var inputView = this.currentInputView();
      if (inputView instanceof app.Views.Search) {
        var href = this.makeParameterizedUrl("/", inputView.readState());
        app.Router.navigate(href, { trigger: false });
      }
    },

    currentInputView: function() {
      return app.Layout.getRegion("input").currentView;
    },

    makeParameterizedUrl: function(root, params) {
      var url;
      _.each(params, function(value, param) {
        if (url) {
          url += ( "&" + encodeURIComponent(param) + "=" + encodeURIComponent(value) );
        }
        else {
          url = ( root + "?" + encodeURIComponent(param) + "=" + encodeURIComponent(value) );
        }
      });
      return url || root;
    },

    loadValsi: function(valsi) {
      var dispatch = this,
        model = new app.Models.Valsi({ word: valsi });
      model.fetch().then(function() {
        dispatch.showValsi(model);
      });
    },

    showValsi: function(model) {
      var collection = new app.Collections.Valsi([ model ]);
      this.ensureSearchView();
      this.showValsiDetails(collection);
    },

    ensureSearchView: function() {
      var inputView = this.currentInputView();
      if (!(inputView instanceof app.Views.Search)) {
        this.showSearch();
      }
    },

    showValsiDetails: function(collection) {
      var view = new app.Views.ValsiDetails({ collection: collection });
      app.Layout.showChildView("output", view);
    },

    showDefinitions: function(valsi, language) {
      var dispatch = this,
        model = new app.Models.Valsi({ word: valsi });
      model.fetch().then(function() {
        dispatch.showDefinitionsForValsiModel(model, language);
      });
      this.ensureSearchView();
    },

    showDefinitionsForValsiModel: function(model, language) {
      var collection = new app.Collections.Valsi([ model ]),
        view = new app.Views.ValsiDetails({ collection: collection });
      app.Layout.showChildView("output", view);
      view.trigger("language:select", language);
    }

  });

  app.Dispatch = new Dispatch();

})(window);
