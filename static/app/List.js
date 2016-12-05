import React, {Component} from 'react';
import Row from './Row.js';
import AddButton from './AddButton.js';

export default class List extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      products: [
        {name: "Kaffee", icon: "https://image.flaticon.com/icons/svg/190/190883.svg"},
        {name: "Milchkaffee", icon: "https://image.flaticon.com/icons/svg/190/190880.svg"},
      ],
      users: ["Timon",
              "Kevin",
              "Moritz"],
    };
  }

  handleModifyDatabase(db_entry){
    console.log("Modifying the DB. Object:");
    console.log(db_entry);
  }

  componentDidMount(){
    console.log('mount');
    const url = window.location.href;
    $.getJSON(url + 'api/user_list/', (data) => {
      const users = data.users.map(u => ({
        name: u.name,
        consume: u.consume,
        id: u.id,
      }));
      console.log(users);
      this.setState({
        users: users,
      });
    });
  }

  render(){
    const rows = this.state.users.map((user, i) => {
      const background = (i + 1) % 2 ? "#E3EBDE" : "";
      return <Row
        products={this.state.products}
        name={user.name}
        key={user.id}
        consume={user.consume}
        style={{background: background, padding: "4px"}}
        modifyDatabase={(db_entry) => this.handleModifyDatabase(db_entry)}
      />
    })
    return <div className="container">
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
