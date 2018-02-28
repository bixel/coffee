import React, {Component} from 'react';
import AddButton from './AddButton.js';
import ServiceButton from './ServiceButton.js';
import { Icon } from './Icon.js';
import Achievement from './Achievement.js';

export default class Row extends Component {
  constructor(props, context){
    super(props, context);
  }

  modifyDatabase(db_entry){
    db_entry.id = this.props.userId;
    this.props.modifyDatabase(db_entry);
  }

  render(){
    const buttons = Object.keys(this.props.products).map((name, i) => {
      const product = this.props.products[name];
      const addButton = (<AddButton
        product={product}
        key={product.name}
        name={this.props.name}
        userId={this.props.userId}
        updateAppState={this.props.updateAppState}
        />);
      return addButton;
      });
    const mugs = this.props.consume ?
      this.props.consume.map((product, i) => (
        <Icon key={i} product={this.props.products[product]} size={24} />)
      ) :
      '';
    const service = this.props.service ? <ServiceButton service={this.props.service} sendService={s => this.props.sendService(s)} /> : '';
    const achievements = this.props.achievements.map((a, i) => <Achievement type={a.key} key={i} />);
    return <div className="row" style={this.props.style}>
      <div className="col" style={{marginTop: '6px', fontSize: '24px'}}>
        {this.props.name} {achievements}<br />
        {mugs}
      </div>
      <div className={this.props.service ? "col-7" : "col"}>
        <div className="btn-toolbar" role="toolbar" style={{float: "right"}}>
          {service}{buttons}
        </div>
      </div>
    </div>
  }
}
