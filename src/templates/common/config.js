var dconfigPlt = {
  mobile: {
    leniency: 1,
    averageDistanceThreshold: 250,
    quizSize: 200,
  },
  desktop: {
    leniency: 1,
    averageDistanceThreshold: 250,
    quizSize: 200,
  },
};

// See https://docs.ankiweb.net/templates/styling.html#platform-specific-css
var mobilep = document.querySelectorAll(".mobile").length === 1;
if (mobilep) {
  var dconfig = dconfigPlt.mobile;
} else {
  var dconfig = dconfigPlt.desktop;
}
