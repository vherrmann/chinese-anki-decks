var dconfigPlt = {
  common: {
    leniency: 1,
    averageDistanceThreshold: 250,
    quizSize: 200,
    pinyin: {
      tone1: "#e30000",
      tone2: "#02b31c",
      tone3: "#1510f0",
      tone4: "#8900bf",
      tone5: "#777777",
    },
  },
  mobile: {},
  desktop: {},
};

// See https://docs.ankiweb.net/templates/styling.html#platform-specific-css
var mobilep = document.querySelectorAll(".mobile").length === 1;
if (mobilep) {
  var dconfig = { ...dconfigPlt.common, ...dconfigPlt.mobile };
} else {
  var dconfig = { ...dconfigPlt.common, ...dconfigPlt.desktop };
}
