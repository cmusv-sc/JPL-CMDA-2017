$(function() {
	var visualSearch = VS.init({
		container : $('.visual_search'),
		query : '',
		callbacks : {
			search : function(query, searchCollection) {
			},
			facetMatches : function(callback) {
				callback([ 'deviceUri', 'deviceType', 'sensorTypeNames',
						'sensorNames', 'longitude', 'latitude', 'altitude',
						'representation', 'deviceUserDefinedFields' ]);
			},
			valueMatches : function(facet, searchTerm, callback) {
			}
		}
	});

	$('.visual_search').click(function() {
		// first show all the rows
		$('.devices').show();
		
		var facets = visualSearch.searchQuery.facets();
		$.each(facets, function(index, val) {
			for ( var prop in val) {
				var search = val[prop];
				if (prop === 'text') {
					prop = 'devices';
				}
				var notFound = $("." + prop).filter(function() {
					var str = $(this).text();
					return str.toLowerCase().indexOf(search) == -1;
				});
				if (prop !== 'devices') {
					notFound = notFound.parent();
				}
				notFound.hide();
			}

		});
		// var notFound = $(element).filter(function() {
		// var str = $(this).text();
		// return str.indexOf(str) == -1;
		// });
	});
});

var searchHide = function(element, str) {
	var notFound = $(element).filter(function() {
		var str = $(this).text();
		return str.indexOf(str) == -1;
	});
	if (element !== '.devices') {
		notFound = notFound.parent();
	}
	notFound.hide();
}