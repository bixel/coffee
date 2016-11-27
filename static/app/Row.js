import React, {Component} from 'react';

const CoffeeMug = () => (
  <span style={{padding: "4px"}}>
  ☕️
  </span>
)

export default class Row extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      productStack: {},
    }
  }

  addConsumption(product){
    let stack = this.state.productStack;
    if(stack[product]){
      stack[product].push(product);
    } else {
      stack[product] = [product];
    }
    this.setState({
      productStack: stack,
    });
    console.log("add", product);
  }

  undoConsumption(product){
    let stack = this.state.productStack;
    if(stack[product]){
      stack[product].pop();
      this.setState({
        productStack: stack,
      })
      console.log(stack);
    }
    console.log("undo", product);
  }

  render(){
    const stack = this.state.productStack;
    const buttons = this.props.products.map((product, i) => {
      const addButton = (
        <button type="button" className="btn btn-primary"
          onClick={() => this.addConsumption(product)}>
          {product}
        </button>
      );
      const undoButton = stack[product] && stack[product].length ? (
        <button type="button" className="btn btn-secondary"
          onClick={() => this.undoConsumption(product)}>
          undo
        </button>
      ) : '';
      return <div className="btn-group" key={i}>
        {addButton}{undoButton}
      </div>
    })
    const mugs = [...Array(+this.props.consume)].map((_, i) => (<CoffeeMug key={i} />))
    return <div className="row" style={this.props.style}>
      <div className="col-xs-3">{this.props.name}</div>
      <div className="col-xs-3">{mugs}</div>
      <div className="col-xs-6">
        <div className="btn-toolbar">
          {buttons}
        </div>
      </div>
    </div>
  }
}
