import React, {Component} from 'react';
import Row from './Row.js';

export default class List extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      products: [
        "Kaffee",
        "Milchkaffee",
      ],
    };
  }

  render(){
    return <div className="container">
      <div className="row"><div className="col-xs-12">
        <h1>Kaffeeliste</h1>
      </div></div>
      <div className="row">
      <div className="col-xs-3"><h4>Name</h4></div>
      <div className="col-xs-3"><h4>Verbrauch Heute</h4></div>
      <div className="col-xs-6"></div>
      </div>
      <Row products={this.state.products} name="Kevin Heinicke" consume="5" style={{background: "#E1EBCE", padding: "4px",}} />
    </div>
  }
}
