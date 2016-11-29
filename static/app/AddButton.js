import React, {Component} from 'react';
import { Icon } from './Icon.js'

const successIconLink = {icon: "http://image.flaticon.com/icons/svg/148/148767.svg",
                         name: "Success"};
const errorIconLink = {icon: "http://image.flaticon.com/icons/svg/148/148766.svg",
                       name: "Error"};

export default class AddButton extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
        cur_consumption: 0,
        cur_undo_time: null,
        start_countdown_at: 3,
    };
  }

  modifyConsumption(val){
    if (this.state.cur_undo_time > 0 || this.state.cur_undo_time == null) {
        const cur_consumption = this.state.cur_consumption + val;
        this.setState({
            cur_consumption: cur_consumption,
            cur_undo_time: this.state.start_countdown_at,
        });
    };
  }

  modifyDatabase(cur_consumption){
    const db_entry = {
        user: this.props.name,
        cur_consumption: this.state.cur_consumption,
        consumption_type: this.props.product.name
    };
    this.props.modifyDatabase(db_entry);
  }

  tick(){
    const cur_undo_time = (this.state.cur_undo_time <= 0) ?
        null : this.state.cur_undo_time - 1;
    if (this.state.cur_undo_time == 0 && this.state.cur_consumption > 0) {
        const cur_consumption = this.state.cur_consumption;
        this.modifyDatabase(cur_consumption);
        this.setState({
            cur_consumption : 0,
        });
   }
    this.setState({
        cur_undo_time: cur_undo_time,
    });
  }

  componentDidMount(){
    this.interval = setInterval(() => this.tick(), 1000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  render() {
    const addButtonText = this.state.cur_consumption === 0 ?
        <Icon product={this.props.product} /> :
        <div>
          <Icon product={this.props.product} />  {" (+" + this.state.cur_consumption + ")"}
        </div>
    const addButton =
        <button type="button" className="btn btn-primary" onClick={() => this.modifyConsumption(+1)}>
            {addButtonText}
        </button>

    const undoButtonText = this.state.cur_undo_time > 0 ?
      <div>
        <Icon product={errorIconLink} /> {" (" + this.state.cur_undo_time.toString() + ")"}
      </div>
        :
        <Icon product={successIconLink} />;
    const undoButton = (this.state.cur_consumption === 0 || this.state.cur_undo_time < 0) ? null :
        <button type="button" className="btn btn-secondary" onClick={() => this.modifyConsumption(-1)}>
            {undoButtonText}
        </button>


    return (
        <div className="btn-group">
            {addButton}{undoButton}
        </div>
    )
  }
}
