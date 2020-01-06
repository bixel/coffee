function plotCoffeeCurve(response){
    function getTrace(data){
      return {
        y: data.map((a, i) => (a.amount + data.slice(0, i).map(a => a.amount).reduce((a, b) => a + b, 0)) / 100),
        x: data.map(x => x.date),
        type: 'date',
      }
    };

    var actualTrace = getTrace(response.actual_curve);
    actualTrace.name = 'Ist';
    var targetTrace = getTrace(response.target_curve);
    targetTrace.name = 'Soll';
    var layout = {
      title: 'Kaffeekasse',
      xaxis: {
        title: 'Datum',
      },
      yaxis: {
        title: 'Kassenstand / €',
      },
      legend: {
        x: 0,
        y: 1.1,
      },
    };
  return {
    traces: [actualTrace, targetTrace],
    layout,
  }
}

function plotPopularTimes(response){
  var trace_last_four_weeks = {
    type: "histogram",
    // transform to correct timezone
    x: response.last_four_weeks.map(t => t * 1000 - 3600 * 1000),
    name: 'Letzte vier Wochen',
    opacity: 0.8,
    xbins: {
      start: 6 * 3600 * 1000,
      end: 20 * 3600 * 1000,
      size: 1800 * 1000,
    },
  };
  var trace_last_week = {
    type: "histogram",
    // transform to correct timezone
    x: response.last_week.map(t => t * 1000 - 3600 * 1000),
    name: 'Letzte Woche',
    opacity: 0.4,
    xbins: {
      start: 6 * 3600 * 1000,
      end: 20 * 3600 * 1000,
      size: 1800 * 1000,
    },
  };
  var layout = {
    title: 'Beliebte Zeiten',
    xaxis: {
      // autorange: false,
      // range: [6 * 3600, 20 * 3600],
      title: 'Tageszeit / Stunden',
      type: 'date',
      tickformat: '%H:%M',
    },
    yaxis: {
      title: 'Kaffee-Dichte / 30 Minuten',
    },
    barmode: 'overlay',
    showlegend: true,
    legend: {
      x: 0,
      y: 1.1
    },
  };
  return {
    traces: [trace_last_four_weeks, trace_last_week],
    layout,
  };
}

// check if this is build with webpack...
try {
  module.exports.plotCoffeeCurve = plotCoffeeCurve;
  module.exports.plotPopularTimes = plotPopularTimes;
} catch (exeption) {
  // I'll just ignore this... This file is also used in non-webpack manner
}
