

function get_mps(session)
{
	console.log("test");
	$.get( "get_mps?session=144", function( data ) {
		console.log( data );
		alert( "Load was performed." );
	});
}