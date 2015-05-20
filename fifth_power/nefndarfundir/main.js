$(function(){
	jQuery.each(Object.keys(data), function(i, d){
		content = data[d]['fundargerd_texti'];
		console.log(content);
		$('#data').append(content);	
	});
});