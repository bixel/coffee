import React, {Component} from 'react';
import Row from './Row.js';
import AddButton from './AddButton.js';
import Alert from './Alert.js';
import {plotCoffeeCurve, plotPopularTimes} from '../plots.js';
import Carousel from './Carousel.js';
import config from './config.js';

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
    // get the initial app state immediately
    $.get(this.url + 'api/user_list/', data => this.updateAppState(data));

    // ...and check for an update every 600s
    this.updateInterval = window.setInterval(() => {
      $.get(this.url + 'api/user_list/', data => this.updateAppState(data));
    }, 600 * 1000);
  }

  /* @TODO this should be moved into the service button */
  sendService(service){
    let _this = this;
    $.post({
      url: config.BASEURL + 'api/finish_service/',
      data: JSON.stringify({service: service}),
      success: data => {
        _this.updateAppState(data);
      },
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
    Plotly.d3.json(config.BASEURL.replace('app/', '') + 'global_api/consumption_times/', function(err, response){
      var {
        traces,
        layout
      } = plotPopularTimes(response);
      Plotly.newPlot("coffee-hours", traces, layout, {displayModeBar: false});
    });

    // WARNING: This code is duplicated from the "global.html" template
    Plotly.d3.json(config.BASEURL.replace('app/', '') + 'global_api/global_data/', function(err, response){
      var {
        traces,
        layout,
      } = plotCoffeeCurve(response);
      Plotly.newPlot('global-graph', traces, layout, {displayModeBar: false});
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
        achievements={user.achievements}
        style={{background: background, padding: "4px"}}
        updateAppState={data => this.updateAppState(data)}
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
        updateAppState={data => this.updateAppState(data)}
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
      <Carousel
        service={this.state.service}
        users={this.state.users}
        updateAppState={data => this.updateAppState(data)}
        sendService={this.sendService}
        />
    </div>
  }
}
