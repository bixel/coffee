import React, {Component} from 'react';
import Row from './Row.js';
import AddButton from './AddButton.js';

export default class List extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      products: [
        {name: "Kaffee", icon: "☕️"},
        {name: "Milchkaffee", icon: "☕️+🍼"},
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

  render(){
    const rows = this.state.users.map((user, i) => {
      const background = (i + 1) % 2 ? "#E1EBCE" : "";
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
        <div className="col-xs-3"><h4>Kaffee Heute</h4></div>
        <div className="col-xs-6"></div>
      </div>
      {rows}
    </div>
  }
}
