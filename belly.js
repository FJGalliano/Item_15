


var pieDiv = document.getElementById("pie-chart");

var traceA = {
 type: "pie",
 values: [8149300, 4916438, 4776980, 3100950, 2083210],
 labels: ['Russia', 'Canada', 'Brazil', 'United States', 'China']
};

var data = [traceA];

var layout = {
 title: "Area Under Forest for Different Countries"
};

Plotly.plot(pieDiv, data, layout);

