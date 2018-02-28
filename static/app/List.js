import React, {Component} from 'react';
import Row from './Row.js';
import AddButton from './AddButton.js';
import Alert from './Alert.js';

export default class List extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      products: {
        Kaffee: {
          name: "Kaffee",
          icon: "https://image.flaticon.com/icons/svg/190/190883.svg"
        },
        Milchkaffee: {
          name: "Milchkaffee",
          icon: "https://image.flaticon.com/icons/svg/190/190880.svg"
        },
      },
      users: [],
      service: {},
    };
    this.url = window.location.origin + window.location.pathname;
  }

  componentDidMount(){
    $.get(this.url + 'api/user_list/', data => this.updateAppState(data));
  }

  /* @TODO this should be moved into the service button */
  sendService(service){
    $.post({
      url: this.url + 'api/finish_service/',
      data: JSON.stringify({service: service}),
      success: data => this.setState(data),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
    }).fail(error => {
      console.log('Error while finishing service.', error);
    });
  }

  /* pass this function down to all elements who want to update the app state
   */
  updateAppState(data){
    this.setState(data);

    // WARNING: This code is duplicated from the "global.html" template
    Plotly.d3.json(window.location.origin + '/global_api/consumption_times/', function(err, response){
      var trace_last_four_weeks = {
        type: "histogram",
        x: response.last_four_weeks,
        histnorm: 'probability',
        name: 'Letzte vier Wochen',
        opacity: 0.8,
        xbins: {
          start: 6 * 3600,
          end: 20 * 3600,
          size: 1800,
        },
      };
      var trace_last_week = {
        type: "histogram",
        histnorm: 'probability',
        x: response.last_week,
        name: 'Letzte Woche',
        opacity: 0.4,
        xbins: {
          start: 6 * 3600,
          end: 20 * 3600,
          size: 1800,
        },
      };
      var ticktext = [6, 8, 10, 12, 14, 16, 18, 20]
      var tickvals = ticktext.map(x => x * 3600);
      var layout = {
        title: 'Beliebte Zeiten',
        xaxis: {
          autorange: false,
          range: [6 * 3600, 20 * 3600],
          tickvals: tickvals,
          ticktext: ticktext,
          title: 'Tageszeit / Stunden',
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
      Plotly.newPlot("coffee-hours", [trace_last_four_weeks, trace_last_week], layout, {displayModeBar: false});
    });

    // WARNING: This code is duplicated from the "global.html" template
    Plotly.d3.json(window.location.origin + '/global_api/global_data/', function(err, response){
      console.log(response);
      var data = response.data;
      var trace = {
        y: data.map((a, i) => (a.amount + data.slice(0, i).map(a => a.amount).reduce((a, b) => a + b, 0)) / 100),
        x: data.map(x => x.date),
        type: 'date',
      };
      var layout = {
        title: 'Kaffeekasse',
        xaxis: {
          title: 'Datum',
        },
        yaxis: {
          title: 'Kassenstand / €',
        },
      };
      Plotly.newPlot('global-graph', [trace], layout, {displayModeBar: false});
    });
  }

  render(){
    // store the guest user for later modifications
    let guestUser = undefined;
    let backgroundIt = 0;
    let background = "#F8F8F8";
    let rows = this.state.users.map((user, i) => {
      background = backgroundIt++ % 2 ? "#F8F8F8" : "";

      // dont show the guest user for now
      if(user.username === 'guest'){
        backgroundIt++;
        guestUser = user;
        return undefined;
      }

      return <Row
        products={this.state.products}
        name={user.name}
        key={i}
        userId={user.id}
        consume={user.consume}
        service={user.id === this.state.service.uid ? this.state.service : undefined}
        achievements={user.achievements}
        style={{background: background, padding: "4px"}}
        updateAppState={data => this.updateAppState(data)}
        sendService={service => this.sendService(service)}
      />
    })
    if(guestUser){
      rows.push(<Row
        products={this.state.products}
        name={guestUser.name}
        key={rows.length}
        userId={guestUser.id}
        consume={guestUser.consume}
        achievements={[]}
        style={{background: background, padding: "4px"}}
        updateAppState={this.updateAppState}
        />)
    }
    let alert = '';
    if(this.state.alert){
      alert = <Alert type={this.state.alert.type}>{this.state.alert.text}</Alert>;
      setTimeout(() => this.setState({ alert: undefined, }), 5000);
    };
    return <div className="container" style={{margin: 0, maxWidth: "100%"}}>
      <div className="row"><div className="col-xs-12">
        <h1>Kaffeeliste</h1>
      </div></div>
      {rows}
      {alert}
    </div>
  }
}
