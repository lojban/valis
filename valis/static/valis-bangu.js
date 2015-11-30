(function(root) {

  var app = root.Valis;

  var CONVERSIONS = [ "", "", "se ", "te ", "ve ", "xe " ];

  var DIGITS = [ "no", "pa", "re", "ci", "vo", "mu", "xa", "ze", "bi", "so" ];

  function expandInteger(num) { // assume positive
    num = Math.floor(num);
    if ( num === 0 ) { return DIGITS[0]; }
    var digits = [];
    while (num > 0) {
      digits.unshift(DIGITS[ num % 10 ]);
      num = Math.floor(num / 10);
    }
    return digits.join("");
  }

  function conversionForPlace(place) {
    return ( place < 6 ) ?
          ( CONVERSIONS[place] || "" ) :
          ( "sexi" + expandInteger(place) + " " );
  }

  app.Utilities.expandInteger = expandInteger;
  app.Utilities.conversionForPlace = conversionForPlace;

})(window);
