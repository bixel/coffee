import React, {Component} from 'react';
import Row from './Row.js';
import AddButton from './AddButton.js';

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
      users: ["Timon",
              "Kevin",
              "Moritz"],
    };
    this.url = window.location.origin + window.location.pathname;
  }

  addConsumption(db_entry){
    console.log(db_entry);
    $.post({
      url: this.url + 'api/add_consumption/',
      data: JSON.stringify(db_entry),
      success: data => {
        if(data.users){
          this.setState({
            users: data.users,
          });
        }
      },
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
    }).fail(error => {
      console.log('error', error);
    });
  }

  componentDidMount(){
    $.getJSON(this.url + 'api/user_list/', (data) => {
      this.setState({
        users: data.users,
      });
    });
  }

  render(){
    const rows = this.state.users.map((user, i) => {
      const background = (i + 1) % 2 ? "#E3EBDE" : "";

      // dont show the guest user for now
      if(user.username === 'guest'){
        return undefined;
      }

      return <Row
        products={this.state.products}
        name={user.name}
        key={i}
        userId={user.id}
        consume={user.consume}
        style={{background: background, padding: "4px"}}
        modifyDatabase={(db_entry) => this.addConsumption(db_entry)}
      />
    })
    return <div className="container" style={{margin: "0px", width: "100%"}}>
      <div className="row"><div className="col-xs-12">
        <h1>Kaffeeliste</h1>
      </div></div>
      <div className="row">
        <div className="col-xs-3"><h4>Name</h4></div>
        <div className="col-xs-9"><h4>Kaffee Heute</h4></div>
      </div>
      {rows}
    </div>
  }
}
