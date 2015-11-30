(function(root) {

  var $       = root.jQuery,
    Mn        = root.Mn,
    app       = root.Valis,
    Utilities = app.Utilities;

  var ViewMixin = {

    debounceMethod: function(name, wait, immediate, after) {
      wait = wait || 300;
      var view = this,
        liveName = "_" + name;
      this[liveName] = this[name];
      this[name] = Utilities.debounce(function() {
        return view[liveName].apply(view, arguments);
      }, wait, immediate, after);
    },

  };

  var ItemView = Mn.ItemView.extend(_.extend({}, ViewMixin)),
    LayoutView = Mn.LayoutView.extend(_.extend({}, ViewMixin));

  var CollectionViewMixin = {

    replaceChild: function(oldView, NewViewConstructor) {
      var collectionView = this,
        model = oldView.model,
        index = oldView._index;
      this.withoutIndexUpdates(function() {
        collectionView.removeChildView(oldView);
        var newView = collectionView.addChild(model, NewViewConstructor, index);
        newView._index = index; // NOTE: (before:)?add:child events w/o index
      });
    },

    withoutIndexUpdates: function(fn) {
      try {
        this._updateIndices = function() {};
        fn.call(this);
      }
      finally {
        delete this._updateIndices;
      }
    }

  };

  var CollectionView =
    Mn.CollectionView.extend(_.extend({}, ViewMixin, CollectionViewMixin));
  var CompositeView =
    Mn.CompositeView.extend(_.extend({}, ViewMixin, CollectionViewMixin));

  app.Views.RootLayout = LayoutView.extend({

    template: "#valis-layout-template",

    regions: {
      "input"  : "#valis-input",
      "output" : "#valis-right"
    },

    events: {
      "click a" : "onAnchorClick"
    },

    initialize: function() {
      this.debounceMethods();
      this.bindWindowEvents();
    },

    debounceMethods: function() {
      this.debounceMethod("onWindowResize", 300, false);
    },

    bindWindowEvents: function() {
      var layout = this;
      $(window).on("resize", function() {
        layout.onWindowResize();
      });
    },

    onWindowResize: function() {
      this.resizeToWindow();
    },

    onAnchorClick: function(e) {
      var href = $(e.target).attr("href");
      app.Router.navigate(href, { trigger: true });
      e.preventDefault();
    },

    onShow: function() {
      this.resizeToWindow();
    },

    resizeToWindow: function() {
      var height = $(window).height();
      this.$el.css({ height: height + "px" });
      this.trigger("layout:resize");
    }

  });
  app.Layout = new app.Views.RootLayout({ el: "#valis-root" });

  app.Views.Search = ItemView.extend({

    tagName: "form",
    id: "valis-search",
    attributes: { action: "#" },

    template: "#valis-search-form-template",

    ui: {
      queryInput        : "#valis-query-input",
      modeSelector      : "#valis-query-mode",
      valsiTypeSelector : "#valis-query-valsi-type",
      languageSelector  : "#valis-query-language"
    },

    events: {
      "keyup @ui.queryInput"         : "onQueryChange",
      "change @ui.modeSelector"      : "onModeChange",
      "change @ui.valsiTypeSelector" : "onTypeChange",
      "change @ui.languageSelector"  : "onLanguageChange"
    },

    defaults: {
      query    : "",
      mode     : "valsi",
      type     : "",
      language : "en"
    },

    onRender: function() {
      this.initializeControls();
      this.emitState();
    },

    initializeControls: function() {
      var mode = this.options.mode || this.defaults.mode;
      this.ui.queryInput.val(this.options.query ||
                             this.defaults.query);
      this.ui.modeSelector.val(mode);
      this.ui.valsiTypeSelector.val(this.options.type ||
                                    this.defaults.type);
      this.ui.languageSelector.val(this.options.language ||
                                   this.defaults.language);

      this.reconfigureModalControls(mode);
    },

    emitState: function() {
      app.Dispatch.execute("search:configure", this.readState());
    },

    readState: function() {
      return {
        mode:     this.ui.modeSelector.val(),
        type:     this.ui.valsiTypeSelector.val(),
        language: this.ui.languageSelector.val(),
        query:    this.ui.queryInput.val()
      };
    },

    onQueryChange: function(e) {
      this.emitState();
    },

    onModeChange: function(e) {
      var mode = $(e.target).val();
      this.reconfigureModalControls(mode);
      this.emitState();
    },

    reconfigureModalControls: function(mode) {
      if (mode == "valsi") {
        this.ui.languageSelector.hide();
        this.ui.valsiTypeSelector.show();
      }
      else { // words
        this.ui.valsiTypeSelector.hide();
        this.ui.languageSelector.show();
      }
    },

    onTypeChange: function() {
      this.emitState();
    },

    onLanguageChange: function() {
      this.emitState();
    }

  });

  app.Views.SearchResults = LayoutView.extend({

    id: "valis-search-results",
    template: "#valis-search-results-template",

    regions: {
      "items" : "#valis-search-results-items"
    },

    initialize: function(options) {
      this.bindViewEvents();
      this.resetResultsView(options);
    },

    bindViewEvents: function() {
      this.on("search:configure", this.onSearchConfigure);
    },

    onSearchConfigure: function(options) {
      if (this.resultsViewIsReusable(options)) {
        this.fetchResultsCollection(options);
      }
      else {
        this.resetResultsView(options);
      }
    },

    resultsViewIsReusable: function(options) {
      var resultsMode = this.resultsMode();
      if (options.mode !== resultsMode) {
        return false;
      }
      else if (resultsMode == "words") {
        if (this.resultsCollection().langauge !== options.language) {
          return false;
        }
      }
      return true;
    },

    resultsMode: function() {
      if (this.resultsView instanceof app.Views.ValsiCollection) {
        return "valsi";
      }
      else if (this.resultsView instanceof app.Views.WordCollection) {
        return "words";
      }
    },

    fetchResultsCollection: function(options) {
      if (this.resultsView) {
        if (options.query) {
          var collection = this.resultsCollection(),
            fetchOptions = this.buildFetchOptions(options);
          collection.fetch(fetchOptions).
            fail(function() {
              collection.reset();
            });
        }
        else {
          this.resetResultsCollection();
        }
      }
    },

    resultsCollection: function() {
      return this.resultsView && this.resultsView.collection;
    },

    buildFetchOptions: function(options) {
      return {
        data: {
          word_prefix: options.query,
          type:        options.type,
          limit:       15
        }
      };
    },

    resetResultsCollection: function() {
      if (this.resultsView) {
        this.resultsCollection().reset();
      }
    },

    resetResultsView: function(options) {
      this.resultsView = this.buildResultsView(options);
      if (this.isRendered) {
        this.showResultsView();
      }
      this.fetchResultsCollection(options);
    },

    buildResultsView: function(options) {
      if (options.mode === "valsi") {
        return this.buildValsiResultsView(options);
      }
      else if (options.mode === "words") {
        return this.buildWordsResultsView(options);
      }
    },

    buildValsiResultsView: function(options) {
      return new app.Views.ValsiCollection();
    },

    buildWordsResultsView: function(options) {
      return new app.Views.WordCollection({
        collection: this.buildWordsCollection(options)
      });
    },

    buildWordsCollection: function(options) {
      return new app.Collections.Words([], {
        language: options.language
      });
    },

    showResultsView: function() {
      if (this.resultsView) {
        this.showChildView("items", this.resultsView);
      }
      else {
        this.getRegion("items").reset();
      }
    },

    onRender: function() {
      this.showResultsView();
    }

  });

  app.Views.DefinitionLinksItem = ItemView.extend({

    tagName: "li",
    template: "#valis-definition-link-template",

    serializeModel: function(model) {
      var language = model.get("language_code");
      return {
        language_code: language,
        uri: Utilities.valsiUrl(model.get("word"), { language: language })
      };
    },

    ui: {
      "anchor" : "a"
    },

    events: {
      "click @ui.anchor" : "onAnchorClick"
    },

    onAnchorClick: function(e) {
      var href = $(e.target).attr("href");
      app.Router.navigate(href, { trigger: false });
      this.trigger("definition:select");
      e.preventDefault();
      e.stopPropagation();
    },

    modelEvents: {
      "select"   : "onSelect",
      "deselect" : "onDeselect"
    },

    onSelect: function() {
      this.setSelected();
      this.trigger("definition:select");
    },

    onDeselect: function() {
      this.setUnselected();
    },

    setSelected: function() {
      this.ui.anchor.addClass("selected");
    },

    setUnselected: function() {
      this.ui.anchor.removeClass("selected");
    }

  });

  app.Views.DefinitionLinksCollection = CollectionView.extend({
    tagName: "ol",
    childView: app.Views.DefinitionLinksItem,
    childViewEventPrefix: "definitionLink",
    clearSelection: function() {
      this.collection.each(function(model) {
        model.trigger("deselect");
      });
    },
    selectLanguage: function(language) {
      var linkModel = this.collection.findWhere({ language_code: language });
      if (linkModel) {
        linkModel.trigger("select");
      }
    }
  });

  app.Views.ValsiDetail = LayoutView.extend({

    tagName: "li",
    className: "valsi-detail",
    template: "#valis-valsi-detail-template",

    regions: {
      "definitionLinks"  : ".definition-links",
      "definitionDetail" : ".definition-detail"
    },

    ui: {
      "title" : "h3 a"
    },

    childViewEventPrefix: "valsiDefinition",

    initialize: function() {
      this.bindViewEvents();
    },

    bindViewEvents: function() {
      this.on("valsiDefinition:definitionLink:definition:select",
              this.onDefinitionSelect);
      this.on("language:select", this.onLanguageSelect);
    },

    onDefinitionSelect: function(__, linkView) {
      this.clearSelectedLanguageLink();
      linkView.setSelected();
      this.showDefinitionsForLanguageLink(linkView.model);
    },

    clearSelectedLanguageLink: function() {
      var linksView = this.getChildView("definitionLinks");
      if (linksView) {
        linksView.clearSelection();
      }
    },

    showDefinitionsForLanguageLink: function(link) {
      var valsiView = this,
        url = link.get("backend_uri"),
        collection = new app.Collections.Definitions();
      collection.fetch({ url: url }).then(function() {
        var view = new app.Views.DefinitionCollection({
          collection: collection
        });
        valsiView.showChildView("definitionDetail", view);
      });
    },

    onLanguageSelect: function(language) {
      var linksView = this.getChildView("definitionLinks");
      if (linksView) {
        linksView.selectLanguage(language);
      }
    },

    onRender: function() {
      this.showDefinitionLinks();
    },

    showDefinitionLinks: function() {
      var view = new app.Views.DefinitionLinksCollection({
        collection: this.model.definitions()
      });
      this.showChildView("definitionLinks", view);
    }

  });

  app.Views.ValsiDetails = CollectionView.extend({

    tagName: "ol",
    className: "valsi-collection",
    childView: app.Views.ValsiDetail,

    initialize: function() {
      this.bindViewEvents();
    },

    bindViewEvents: function() {
      this.on("language:select", this.onLanguageSelect);
    },

    onLanguageSelect: function(language) {
      this.children.each(function(detailView) {
        detailView.trigger("language:select", language);
      });
    }

  });

  var ScrollingCollectionView = CollectionView.extend({

    initialize: function() {
      this.debounceMethods();
      this.bindViewEvents();
    },

    debounceMethods: function() {
      var view = this;
      this.debounceMethod("onScrollMax", 300, true, function() {
        view.afterScrollMax(); // scroll may have been re-maxed during debounce
      });
    },

    bindViewEvents: function() {
      this.on("valis:scroll:max", this.onScrollMax);
    },

    onScrollMax: function() {
      if (this.collection && this.collection.hasNext()) {
        var view = this;
        this.showBusy();
        this.collection.fetchNext().always(function() {
          view.hideBusy();
          view.ensureScrollableContent();
        });
      }
    },

    showBusy: function() {
      this.$el.addClass("loading");
    },

    hideBusy: function() {
      this.$el.removeClass("loading");
    },

    afterScrollMax: function() {
      this.ensureScrollableContent();
    },

    events: {
      "scroll" : "onScroll"
    },

    scrollMax: 0.7,

    onScroll: function(e) {
      this.ensureScrollableContent();
    },

    ensureScrollableContent: function() {
      var scrollRatio = this.calculateScrollRatio();
      if (scrollRatio >= this.scrollMax) {
        this.trigger("valis:scroll:max");
      }
    },

    calculateScrollRatio: function() {
      var height = this.$el.height(),
        scrollTop = this.$el.scrollTop(),
        scrollHeight = this.el.scrollHeight;
      return (height + scrollTop) / scrollHeight;
    },

    onShow: function() {
      this.resetHeight();
      this.listenTo(app.Layout, "layout:resize", this.onLayoutResize);
    },

    onLayoutResize: function() {
      this.resetHeight();
    },

    resetHeight: function() {
      var height = $(window).height();
      this.$el.css({ height: ( height - 40 ) + "px" });
    }

  });

  app.Views.ValsiCollection = ScrollingCollectionView.extend({

    tagName: "ol",
    className: "valsi-collection",

    childView: app.Views.ValsiDetail,
    childViewEventPrefix: "valsiItem",

    initialize: function() {
      ScrollingCollectionView.prototype.initialize.apply(this, arguments);
      if (!this.collection) {
        this.collection = new app.Collections.Valsi();
      }
    }

  });

  app.Views.DefinitionItem = LayoutView.extend({

    tagName: "li",
    className: "valsi-definition",
    template: "#valis-definition-item-template",

    regions: {
      "glosswords" : ".definition-gloss-words",
      "places"     : ".definition-places"
    },

    onRender: function() {
      this.showGlossWords();
      this.showPlaces();
    },

    showGlossWords: function() {
      var view = new app.Views.DefinitionGlosswordsView({
        collection: this.model.glossWords()
      });
      this.showChildView("glosswords", view);
    },

    showPlaces: function() {
      var places = this.model.places();
      if (places.length > 0) {
        var view = new app.Views.DefinitionPlacesView({ collection: places });
        this.showChildView("places", view);
      }
    }

  });

  app.Views.DefinitionCollection = CollectionView.extend({
    tagName: "ol",
    className: "valsi-definitions",
    childView: app.Views.DefinitionItem
  });

  app.Views.DefinitionGlosswordItem = ItemView.extend({
    tagName: "li",
    className: "definition-gloss-word",
    template: "#valis-keyword-item-template"
  });

  app.Views.DefinitionGlosswordsView = CollectionView.extend({
    tagName: "ol",
    className: "valsi-definition-keywords",
    childView: app.Views.DefinitionGlosswordItem
  });

  app.Views.DefinitionPlacewordItem = ItemView.extend({
    tagName: "li",
    className: "definition-place-word",
    attributes: function() {
      return { value: this.model.get("place") };
    },
    template: "#valis-placeword-item-template",
    serializeModel: function() {
      return _.extend({
        valsi: this.model.get("valsi"),
        place: this.model.get("place")
      }, this.model.get("keyword"));
    }
  });

  app.Views.DefinitionPlacesView = CompositeView.extend({
    template: "#valis-definition-places-template",
    childViewContainer: "ol",
    childView: app.Views.DefinitionPlacewordItem
  });

  app.Views.WordDetail = LayoutView.extend({

    tagName: "li",
    className: "word-detail",
    template: "#valis-word-detail-template",

    regions: {
      "keywordDefinitions" : ".keyword-definitions-region"
    },

    events: {
      "click a" : "onAnchorClick"
    },

    onRender: function() {
      this.showKeywordDefinitions();
    },

    showKeywordDefinitions: function() {
      var view = new app.Views.KeywordDefinitionsView({
        collection: this.model.keywordDefinitions()
      });
      this.showChildView("keywordDefinitions", view);
    },

    onAnchorClick: function(e) {
      this.saveWordSearch();
    },

    saveWordSearch: function() {
      app.Dispatch.execute("search:push");
    }

  });

  app.Views.WordCollection = ScrollingCollectionView.extend({

    tagName: "ol",
    className: "word-collection",

    childView: app.Views.WordDetail,
    childViewEventPrefix: "wordItem",

    initialize: function() {
      ScrollingCollectionView.prototype.initialize.apply(this, arguments);
      if (!this.collection) {
        this.collection = new app.Collections.Words();
      }
    }

  });

  app.Views.KeywordDefinitionView = ItemView.extend({
    tagName: "li",
    className: "keyword-definition",
    template: "#valis-keyword-definition-template"
  });

  app.Views.KeywordDefinitionsView = CollectionView.extend({
    tagName: "ol",
    className: "keyword-definitions",
    childView: app.Views.KeywordDefinitionView
  });

})(window);
