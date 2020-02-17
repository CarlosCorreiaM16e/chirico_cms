function slugify (str) {
    /* adpeted from Marcelo Ribeiro:
    https://gist.github.com/marcelo-ribeiro/abd651b889e4a20e0bab558a05d38d77 */
    var map = {
        '-' : ' ',
        'a' : 'á|à|ã|â|À|Á|Ã|Â',
        'e' : 'é|è|ê|É|È|Ê',
        'i' : 'í|ì|î|Í|Ì|Î',
        'o' : 'ó|ò|ô|õ|Ó|Ò|Ô|Õ',
        'u' : 'ú|ù|û|ü|Ú|Ù|Û|Ü',
        'c' : 'ç|Ç',
        'n' : 'ñ|Ñ'
    };
    for (var pattern in map) {
        str = str.replace(new RegExp(map[pattern], 'g'), pattern);
    };
}

function sanitize_filename( filename ) {
    var parts = filename.split( '.' );
    var fname = slugify( parts.slice( 0, -1 ).join( '.' ) );
    var ext = parts.slice( -1 )[0];
    var filename = fname.replace( /\W/g, '-' );
    return filename + '.' + ext.toLowerCase();
}

