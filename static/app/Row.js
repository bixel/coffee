import React, {Component} from 'react';
import AddButton from './AddButton.js';
import { Icon } from './Icon.js';

export default class Row extends Component {
  constructor(props, context){
    super(props, context);
  }

  modifyDatabase(db_entry){
    this.props.modifyDatabase(db_entry);
  }

  render(){
    const buttons = this.props.products.map((product, i) => {
      const addButton = <AddButton product={product} key={product.name} name={this.props.name}
                         modifyDatabase={(cur_consumption) => this.modifyDatabase(cur_consumption)}/>
      return addButton;
      });
    console.log(this.props.consume);
    const mugs = [...Array(+this.props.consume)].map((_, i) => (<Icon key={i} product={this.props.products[0]}/>)) || '';
    return <div className="row" style={this.props.style}>
      <div className="col-xs-3" style={{marginTop: '6px'}}>{this.props.name}</div>
      <div className="col-xs-3" style={{marginTop: '5px'}}>{mugs}</div>
      <div className="col-xs-6">
        <div className="btn-toolbar">
          {buttons}
        </div>
      </div>
    </div>
  }
}
