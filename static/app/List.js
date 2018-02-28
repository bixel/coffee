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
    $.get(this.url + 'api/user_list/', data => this.setState(data));
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
    return <div className="container">
      <div className="row"><div className="col-xs-12">
        <h1>Kaffeeliste</h1>
      </div></div>
      {rows}
      {alert}
    </div>
  }
}
