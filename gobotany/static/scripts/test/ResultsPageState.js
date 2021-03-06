/* Tests for simplekey/ResultsPageState.js */

var requirejs = require('requirejs');
var ResultsPageState = requirejs('simplekey/ResultsPageState');
var _ = requirejs('bridge/underscore');

var sample_hash = '#_filters=family,genus,habitat_general,' +
    'state_distribution,trophophyll_form_ly,sporophyll_position_ly,' +
    'upright_shoot_form_ly,horizontal_shoot_position_ly,' +
    'trophophyll_morphology_ly,trophophyll_margins_ly' +
    '&family=Lycopodiaceae&trophophyll_form_ly=short%20and%20scale-like' +
    '&horizontal_shoot_position_ly=on%20the%20surface%20of%20the%20ground' +
    '&_view=photos&_show=branches';

var results_page_state = ResultsPageState.create({hash: sample_hash});

module.exports = {
    'ResultsPageState': {
        'can detect the filters parameter in the hash': function () {
            var has_filters = results_page_state.hash_has_filters();
            has_filters.should.equal(true);
        },

        'can parse a list of filters from the hash': function () {
            var filter_names = results_page_state.filter_names();
            filter_names.length.should.be.above(0);
            filter_names.should.eql([
                'family', 'genus', 'habitat_general', 'state_distribution',
                'trophophyll_form_ly', 'sporophyll_position_ly',
                'upright_shoot_form_ly', 'horizontal_shoot_position_ly',
                'trophophyll_morphology_ly', 'trophophyll_margins_ly']);
        },

        'can parse filter values from the hash': function () {
            var filter_values = results_page_state.filter_values();
            _.size(filter_values).should.be.above(0);
            filter_values.should.eql({
                'family': 'Lycopodiaceae',
                'trophophyll_form_ly': 'short and scale-like',
                'horizontal_shoot_position_ly':
                    'on the surface of the ground'});
        },

        'can parse the tab view from the hash': function () {
            var tab_view = results_page_state.tab_view();
            tab_view.should.equal('photos');
        },

        'can parse the image type from the hash': function () {
            var image_type = results_page_state.image_type();
            image_type.should.equal('branches');
        },

        'can create a hash from the page state': function () {
            var filter_names = results_page_state.filter_names(),
                filter_values = results_page_state.filter_values(),
                hash,
                page_state = ResultsPageState.create({
                    'filter_names': filter_names,
                    'filter_values': filter_values,
                    'image_type': 'branches',
                    'tab_view': 'photos'
                });
            hash = page_state.hash();
            hash.should.equal(sample_hash);
        }
    }
};
