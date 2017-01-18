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

  sendService(service){
    $.post({
      url: this.url + 'api/finish_service/',
      data: JSON.stringify({service: service}),
      success: data => {
        window.alert('Service eingetragen!');
      },
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
    }).fail(error => {
      console.log('Error while finishing service.', error);
    });
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
          onClick={e => {e.preventDefault(); this.sendService("cleaned");}}>Gereinigt</a>
        <a className="dropdown-item" style={styles.dropdown} href="#"
          onClick={e => {e.preventDefault(); this.sendService("cleaning_program");}}>Reinigungsprogramm</a>
        <a className="dropdown-item" style={styles.dropdown} href="#"
          onClick={e => {e.preventDefault(); this.sendService("decalcify_program");}}>Entkalkungsprogramm</a>
      </div>
    </div>
  }
}
