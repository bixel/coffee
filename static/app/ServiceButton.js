import React, {Component} from 'react';

const styles = {
  button: {
    fontSize: "16px",
    height: "80px",
    borderRadius: ".25rem",
  },
  dropdown: {
    fontSize: "24px",
    padding: "20px 10px",
  }
}

export default class ServiceButton extends Component {
  constructor(props, context){
    super(props, context);
    this.url = window.location.origin + window.location.pathname;
  }

  render(){
    return <div className="btn-group" role="group">
      <button id="btnGroupDrop1" type="button"
        className="btn btn-secondary" style={styles.button}
        data-toggle="dropdown">
          Service<br />
          +
      </button>
      <div className="dropdown-menu" aria-labelledby="btnGroupDrop1">
        <a className="dropdown-item" style={styles.dropdown} href="#"
          onClick={e => {e.preventDefault(); this.props.sendService("cleaned");}}>
          Gereinigt
          {this.props.service.cleaned ? " ✅" : ""}
        </a>
        <a className="dropdown-item" style={styles.dropdown} href="#"
          onClick={e => {e.preventDefault(); this.props.sendService("cleaning_program");}}>
          Reinigungsprogramm
          {this.props.service.cleaningProgram ? " ✅" : ""}
        </a>
        <a className="dropdown-item" style={styles.dropdown} href="#"
          onClick={e => {e.preventDefault(); this.props.sendService("decalcify_program");}}>
          Entkalkungsprogramm
          {this.props.service.decalcifyProgram ? " ✅" : ""}
        </a>
      </div>
    </div>
  }
}
