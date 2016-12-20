import React, {Component} from 'react';
import { Icon } from './Icon.js'

const successIconLink = {icon: "https://image.flaticon.com/icons/svg/148/148767.svg",
                         name: "Success"};
const errorIconLink = {icon: "https://image.flaticon.com/icons/svg/148/148766.svg",
                       name: "Error"};
const styles = {
  addButtonNormal: {
    width: '100px',
    height: '80px',
  },
  addButtonCanUndo: {
    width: '60px',
    height: '80px',
  },
  undoButton: {
    width: '40px',
    height: '80px',
    padding: '8px 4px',
  },
  cancelBadgeStyle: {
    position: 'absolute',
    right: '-10px',
    top: '-10px',
    color: 'white',
    width: '20px',
    height: '20px',
    background: '#D75A4A',
    borderRadius: '10px',
  },
  addBadgeStyle: {
    position: 'absolute',
    right: '-10px',
    top: '-10px',
    color: 'white',
    width: '20px',
    height: '20px',
    background: '#53D838',
    borderRadius: '10px',
  },
}

const Badge = ({children, style}) => (
  <div style={style}>
    {children}
  </div>
);

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
    const undoButtonText = this.state.cur_undo_time > 0 ?
      <Icon product={errorIconLink} size={26} /> :
      <Icon product={successIconLink} size={26} />;
    const undoButton = (this.state.cur_consumption === 0 || this.state.cur_undo_time < 0) ?
      null :
      <button
        type="button"
        className="btn btn-secondary"
        style={styles.undoButton}
        onClick={() => this.modifyConsumption(-1)}>
          {undoButtonText}<Badge style={styles.cancelBadgeStyle}>{this.state.cur_undo_time}</Badge>
      </button>;

    const addButtonBadge = (this.state.cur_consumption === 0 || this.state.cur_undo_time < 0) ?
      null :
      <Badge style={styles.addBadgeStyle}>{this.state.cur_consumption}</Badge>;
    const addButtonText = <Icon product={this.props.product} size={32} />;
    const addButton =
        <button
          type="button"
          className="btn btn-primary"
          style={undoButton ? styles.addButtonCanUndo : styles.addButtonNormal}
          onClick={() => this.modifyConsumption(+1)}>
            {addButtonText}{addButtonBadge}
        </button>;

    return (
        <div className="btn-group">
            {addButton}{undoButton}
        </div>
    )
  }
}
