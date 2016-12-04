import React, {Component} from 'react';
import Row from './Row.js';
import AddButton from './AddButton.js';

export default class List extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      products: [
        {name: "Kaffee", icon: "http://image.flaticon.com/icons/svg/190/190883.svg"},
        {name: "Milchkaffee", icon: "http://image.flaticon.com/icons/svg/190/190880.svg"},
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
    $.getJSON('/app/api/user_list/', (data) => {
      const users = data.users.map(u => (u.name));
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
        name={user}
        key={user}
        consume="5"
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
