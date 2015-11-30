(function(root) {

  var _       = root._,
    $         = root.$,
    BB        = root.Backbone,
    app       = root.Valis,
    Utilities = app.Utilities;

  app.Models.AbstractModel = BB.Model.extend({
    url: function() {
      var links = this.get("_links");
      return (links && links.self) ?
        links.self : BB.Model.prototype.url.apply(this, arguments);
    }
  });

  app.Collections.AbstractCollection = BB.Collection.extend({

    parse: function(resp) {
      if (resp) {
        this._meta = _.pick(resp, "count", "_links", "updated_at");
        return resp.items;
      }
    },

    remoteLength: function() {
      return this._meta ? this._meta.count : false;
    },

    fetchNext: function() {
      var nextUrl = this._meta && this._meta._links && this._meta._links.next;
      return nextUrl ?
        this.fetch({ url: nextUrl, remove: false }) :
        $.Deferred().resolve().promise();
    },

    hasNext: function() {
      return !! (this._meta && this._meta._links && this._meta._links.next);
    }

  });

  app.Models.Valsi = app.Models.AbstractModel.extend({

    urlRoot: "/api/valsi",

    idAttribute: "word",

    definitions: function() {
      var models = this.buildDefinitionModels();
      return new BB.Collection(models);
    },

    buildDefinitionModels: function() {
      var word = this.get("word"),
        definitions = this.get("definitions"),
        sortedLangs = _.keys(definitions).sort();
      return _.map(sortedLangs, function(lang) {
        return {
          word:          word,
          language_code: lang,
          backend_uri:   definitions[lang]
        };
      });
    }

  });

  app.Collections.Valsi = app.Collections.AbstractCollection.extend({
    url: "/api/valsi",
    model: app.Models.Valsi
  });

  app.Models.Definition = app.Models.AbstractModel.extend({

    glossWords: function() {
      return this.buildGlossWordCollection();
    },

    buildGlossWordCollection: function() {
      var words = this.get("gloss_words") || [];
      return new app.Collections.Words(words, {
        language: this.get("language")
      });
    },

    places: function() {
      return this.buildPlacesCollection();
    },

    buildPlacesCollection: function() {
      var definition = this,
        placeKeywords = _.map(this.get("place_keywords"), function(kw, place) {
          return definition.buildPlaceKeyword(place, kw);
        });
      return new app.Collections.PlaceKeywords(placeKeywords);
    },

    buildPlaceKeyword: function(place, keyword) {
      return {
        valsi:   this.get("valsi"),
        place:   place,
        keyword: keyword
      };
    }

  });

  app.Collections.Definitions = app.Collections.AbstractCollection.extend({
    model: app.Models.Definition
  });

  app.Models.Word = app.Models.AbstractModel.extend({

    idAttribute: "word_id",

    urlRoot: function() {
      return Utilities.backendUri("languages",
                                  this.get("language"),
                                  "words",
                                  this.get("word"));
    },

    keywordDefinitions: function() {
      return this.buildKeywordDefinitionsCollection();
    },

    buildKeywordDefinitionsCollection: function() {
      var keywordDefinitions = ( this.get("definition_references") || {} ),
        glossDefinitions = ( keywordDefinitions["as_gloss_word"] || [] ),
        placeDefinitions = this.buildSortedPlaceWordDefinitions(),
        definitions = this.uniqueKeywordDefinitions(glossDefinitions, placeDefinitions);
      return new app.Collections.KeywordDefinitions(definitions);
    },

    buildSortedPlaceWordDefinitions: function() {
      var keywordDefinitions = ( this.get("definition_references") || {} ),
        definitionsByPlace = ( keywordDefinitions["as_place_keyword"] || {} );
      return this.transformPlaceWordDefinitions(definitionsByPlace);
    },

    transformPlaceWordDefinitions: function(definitionsByPlace) {
      var sortedDefinitions = [];
      _.each(Utilities.sortNumeric(_.keys(definitionsByPlace)), function(place) {
        var placeDefinitions = definitionsByPlace[place];
        _.each(placeDefinitions, function(definition) {
          sortedDefinitions.push(_.extend({ place: place }, definition));
        });
      });
      return sortedDefinitions;
    },

    uniqueKeywordDefinitions: function(glossDefinitions, placeDefinitions) {
      var seenWords = {};
      glossDefinitions = _.filter(glossDefinitions, function(definition) {
        var word = definition.word;
        return seenWords[word] ? false : ( seenWords[word] = true );
      });
      placeDefinitions = _.filter(placeDefinitions, function(definition) {
        var word = definition.word, place = definition.place;
        if (place && (parseInt(place) < 2)) { place = ""; }
        word = word + place;
        return seenWords[word] ? false : ( seenWords[word] = true );
      });
      return glossDefinitions.concat(placeDefinitions);
    }

  });

  app.Collections.Words = app.Collections.AbstractCollection.extend({
    initialize: function(models, options) {
      if (options.language) { this.language = options.language; }
      else { throw new Error("No language specified!"); }
    },
    model: app.Models.Word,
    url: function() {
      return Utilities.backendUri("languages",
                                  this.language,
                                  "words");
    }
  });

  app.Models.PlaceKeyword = app.Models.AbstractModel.extend({
  });

  app.Collections.PlaceKeywords = app.Collections.AbstractCollection.extend({
    model: app.Models.PlaceKeyword
  });

  app.Models.KeywordDefinition = app.Models.AbstractModel.extend({
    // word, language, definition_id, _links
  });

  app.Collections.KeywordDefinitions = app.Collections.AbstractCollection.extend({
    model: app.Models.KeywordDefinition
  });

})(window);
