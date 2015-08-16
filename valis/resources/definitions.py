
from flask import abort
from marshmallow import Schema

from ..utils import uri_unmunge_lojban
from ..web.endpoints import Endpoint
from ..schema.definitions import ItemSchema, CollectionSchema
from ..models import Definition
from abstract import AbstractCollectionResource, AbstractItemResource

class CollectionOptionsSchema(Schema):
    pass

collection_endpoint = \
        Endpoint("DefinitionsCollection",
                "/valsi/<string:word>/<string:language_code>",
                options_schema=CollectionOptionsSchema())

collection_schema = CollectionSchema()

class Collection(AbstractCollectionResource):

    def get(self, word, language_code):
        word = uri_unmunge_lojban(word)
        models, def_scores, kw_scores = \
                self._fetch_definitions_with_scores(language_code, word)
        models = self._sort_with_scores(models, def_scores, kw_scores)
        collection = self._build_collection(models)
        return self._serialize_collection(collection)

    def _endpoint(self):
        return collection_endpoint

    def _fetch_definitions_with_scores(self, language_code, word):
        definitions, def_scores, kw_scores = \
            Definition.fetch_by_language_and_word_with_scores(language_code, word)
        if not definitions:
            abort(404)
        return definitions, def_scores, kw_scores

    def _sort_with_scores(self, definitions, def_scores, kw_scores):
        unscored_defs = set(definitions)
        defs_by_id = self._build_definition_dictionary(definitions, kw_scores)
        positive_scores, zero_scores, negative_scores = self._partition_definition_scores(def_scores)
        positive_defs = self._apply_definition_scores(positive_scores, defs_by_id, unscored_defs)
        negative_defs = self._apply_definition_scores(negative_scores, defs_by_id, unscored_defs)
        for d in unscored_defs:
            zero_scores.append((d.definitionid, 0))
        zero_defs = self._apply_definition_scores(zero_scores, defs_by_id, unscored_defs)
        return positive_defs + zero_defs + negative_defs

    def _build_definition_dictionary(self, definitions, kw_scores):
        definitions_by_id = {}
        for d in definitions:
            def_kw_scores = kw_scores.get(d.definitionid, None)
            if def_kw_scores:
                d.annotate(keyword_scores=def_kw_scores)
            definitions_by_id[d.definitionid] = d
        return definitions_by_id

    @staticmethod
    def _partition_definition_scores(scores):
        positive_scores, zero_scores, negative_scores = [], [], []
        for score in scores: # ASSUME: sorted
            if score > 0:
                positive_scores.append(score)
            elif score == 0:
                zero_scores.append(score)
            else:
                negative_scores.append(score)
        return positive_scores, zero_scores, negative_scores

    def _apply_definition_scores(self, scored_tuples, identity_map, unprocessed_set):
        sorted_definitions = []
        for definition_id, score in scored_tuples:
            definition = identity_map[definition_id]
            definition.annotate(score=score)
            unprocessed_set.remove(definition)
            sorted_definitions.append(definition)
        return sorted_definitions

    def _schema(self):
        return collection_schema

item_endpoint = \
        Endpoint("DefinitionsItem",
                "/valsi/<string:word>/<string:language_code>/<int:definition_id>")

item_schema = ItemSchema()

class Item(AbstractItemResource):

    def get(self, word, language_code, definition_id):
        word = uri_unmunge_lojban(word)
        definition, def_score, kw_scores = \
                self._fetch_definition_with_score(definition_id, language_code, word)
        definition.annotate(score=def_score, keyword_scores=kw_scores)
        return self._serialize_model(definition)

    def _fetch_definition_with_score(self, definition_id, language_code, word):
        definition, def_score, kw_scores = \
                Definition.fetch_for_id_with_scores(definition_id, language_code=language_code, word=word)
        if not definition:
            abort(404)
        return definition, def_score, kw_scores

    def _schema(self):
        return item_schema

