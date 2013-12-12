

draw_table = function(file, columns, id) {
    d3.json(file, function(data) {

        var table = d3.select(id).append("table").attr("class", "table table-striped"),
            thead = table.append("thead"),
            tbody = table.append("tbody");

        // append the header row
        thead.append("tr")
            .selectAll("th")
            .data(columns)
            .enter()
            .append("th")
                .text(function(column) { return column; });

        // create a row for each object in the data
        var rows = tbody.selectAll("tr")
            .data(data)
            .enter()
            .append("tr");

        // create a cell in each row for each column
        var cells = rows.selectAll("td")
            .data(function(row) {
                return columns.map(function(column) {
                    var value = row[column];
                    return {column: column, value: value};
                });
            })
            .enter()
            .append("td")
                .append("div")
                .style("color", function(d) {
                    if (d.column == 'amount') {
                        if (d.value > 0) {
                            return "green";
                        } else if (d.value < 0) {
                            return "red";
                        }
                    }
                })
                .text(function(d) {
                    value = d.value

                    if (d.column === "amount") {
                        value = (0.01 * value).toFixed(2);
                        value = value + ' €';
                    }
                    return value;
                });
    });
}

draw_graph = function(file, id) {
    var margin = {top: 20, right: 20, bottom: 70, left: 50},
        width = 680 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var parseDate = d3.time.format("%Y-%m-%d").parse;

    var x = d3.time.scale()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height-10, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var line = d3.svg.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.amount); })
        .interpolate("step-before");

    var svg = d3.select(id).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.json(file, function(error, data) {
      sum = 0;
      data.forEach(function(d) {
        d.date = parseDate(d.date);
        sum += 0.01 * d.amount;
        d.amount = sum;

      });

      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain(d3.extent(data, function(d) { return d.amount; }));

      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)
          .selectAll("text")
          .style("text-anchor", "end")
          .attr("transform", function(d) {
              return "rotate(-45)";
          })

      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Balance (€)");

      svg.append("path")
          .datum(data)
          .attr("class", "line")
          .attr("d", line);
    });
}
