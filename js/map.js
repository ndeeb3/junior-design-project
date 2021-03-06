

var width = 600,
    height = 500,
    barHeight = height / 2 - 40;

var formatNumber = d3.format("s");
// var datamap = new Map();
// datamap.set("2015", "data/data2015.csv");
// datamap.set("2016", "data/data2016.csv");
// var selYear = "2016";
// function selectYear() {
//     selYear = document.getElementById("mySelect").value;
//     d3.select("svg").remove();
//     loadGraph();
// }

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.split(search).join(replacement);
};

function loadGraph(fb_data) {
    console.log(fb_data);
    var color = d3.scale.ordinal()
        .range(["#8dd3c7","#ffffb3","#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5","#d9d9d9","#bc80bd","#ccebc5","#ffed6f"]);

    var svg = d3.select('#chartbody').append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width/2 + "," + height/2 + ")");

    // d3.json("data/data.json", function(error, data) {
        var keys = [];
        data = JSON.parse(fb_data, function(key, value) {
            if (key) {
                keys.push(key);
            }
            return value;
        });
        console.log(data);
        console.log(keys);

        var extent = d3.extent(data, function(d) { return d.value; });
        extent[0] = extent[0] * 0.5;
        extent[1] = extent[1] * 1.25;
        var barScale = d3.scale.linear()
            .domain(extent)
            .range([0, barHeight]);



        var numBars = keys.length;

        var x = d3.scale.linear()
            .domain(extent)
            .range([0, -barHeight]);

        var xAxis = d3.svg.axis()
            .scale(x).orient("left")
            .ticks(3)
            .tickFormat(formatNumber);

        var circles = svg.selectAll("circle")
            .data(x.ticks(3))
            .enter().append("circle")
            .attr("r", function(d) {return barScale(d);})
            .style("fill", "none")
            .style("stroke", "black")
            .style("stroke-dasharray", "2,2")
            .style("stroke-width",".5px");

        var arc = d3.svg.arc()
            .startAngle(function(d,i) { return (i * 2 * Math.PI) / numBars; })
            .endAngle(function(d,i) { return ((i + 1) * 2 * Math.PI) / numBars; })
            .innerRadius(0);

        var segments = svg.selectAll("path")
            .data(data)
            .enter().append("path")
            .each(function(d) { d.outerRadius = 0; })
            .style("fill", function (d) { return color(d.name); })
            .attr("d", arc);

        segments.transition().ease("elastic").duration(750).delay(function(d,i) {return (25-i)*100;})
            .attrTween("d", function(d,index) {
                var i = d3.interpolate(d.outerRadius, barScale(+d.value));
                return function(t) { d.outerRadius = i(t); return arc(d,index); };
            });

        svg.append("circle")
            .attr("r", barHeight)
            .classed("outer", true)
            .style("fill", "none")
            .style("stroke", "black")
            .style("stroke-width","1.5px");

        var lines = svg.selectAll("line")
            .data(keys)
            .enter().append("line")
            .attr("y2", -barHeight - 20)
            .style("stroke", "black")
            .style("stroke-width",".5px")
            .attr("transform", function(d, i) { return "rotate(" + (i * 360 / numBars) + ")"; });

        svg.append("g")
            .attr("class", "x axis")
            .call(xAxis);

        // Labels
        var labelRadius = barHeight * 1.025;

        var labels = svg.append("g")
            .classed("labels", true);

        labels.append("def")
            .append("path")
            .attr("id", "label-path")
            .attr("d", "m0 " + -labelRadius + " a" + labelRadius + " " + labelRadius + " 0 1,1 -0.01 0");

        labels.selectAll("text")
            .data(keys)
            .enter().append("text")
            .style("text-anchor", "middle")
            .style("font-weight","bold")
            .style("fill", function(d, i) {return "#3e3e3e";})
            .append("textPath")
            .attr("xlink:href", "#label-path")
            .attr("startOffset", function(d, i) {return i * 100 / numBars + 50 / numBars + '%';});
            // .text(function(d) {return d.toUpperCase(); });

    // });
}

window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const search_term = urlParams.get('search');
    var title = document.getElementById("title");
    title.textContent += search_term;
    var config = {
        apiKey: "AIzaSyBXViFaFbggSb0QqB1QwmAtuE3XO545NF0",
        authDomain: "junior-design-project.firebaseapp.com",
        databaseURL: "https://junior-design-project.firebaseio.com",
        projectId: "junior-design-project",
        storageBucket: "junior-design-project.appspot.com",
        messagingSenderId: "986723685667"
    };
    firebase.initializeApp(config);
    var database = firebase.database();
    database.ref('/').orderByChild('name').equalTo(search_term).on("value", function(snapshot) {
        snapshot.forEach(function(child) {
            loadGraph(child.val()['fields'].replaceAll("'", '"'));
        });
    });
};