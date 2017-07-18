$(function() {
	$.fn.editable.defaults.mode = 'inline';

	$('.edit-btn').click(function(event){
	    var primaryKey = $(this).attr('data-pk');
	    var callUrl = $(this).attr('data-url');
	    
		event.stopPropagation();
		$('.' + primaryKey+'.editable').editable({
			type : 'text',
			pk : primaryKey,
			url : callUrl,
			success : function(response) {
				document.location.reload(true);
			}
		}).click();
	});
});
