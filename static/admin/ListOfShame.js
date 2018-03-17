import React, {Component} from 'react';

export default class ListOfShame extends Component {
  constructor(props, context){
    super(props, context);
    this.state = {
      list: [],
      order: 'balance',
    }
    this.url = window.location.origin + window.location.pathname;
    this.listOrder = {
      balance: (user1, user2) => (user1.balance - user2.balance),
      score: (user1, user2) => (user1.score - user2.score),
      last_service: (user1, user2) => (user1.last_service - user2.last_service),
    }
  }

  parseListOfShame(data){
    var list = data.list.map(item => {
      item.last_service = new Date(item.last_service);
      return item;
    });
    return list.sort(this.listOrder[this.state.order]);
  }

  componentDidMount(){
    $.getJSON(this.url + 'api/listofshame/', (data) => {
      // First convert all dates to js date objects
      this.setState({
        list: this.parseListOfShame(data),
        nextServicePeriods: data.nextServicePeriods,
      });
    });
  }

  changeOrder(order){
    let newState = this.state;
    if(newState.order === order){
      newState.list = newState.list.reverse();
    } else {
      newState.order = order;
      newState.list = newState.list.sort(this.listOrder[order])
    }
    this.setState(newState);
  }

  addService(uid, interval){
    const data = {
      uid: uid,
      interval: interval,
    }
    console.log(uid, interval);
    $.post({
      url: this.url + 'api/add_service/',
      data: JSON.stringify(data),
      success: data => {
        this.setState({list: this.parseListOfShame(data),
                       nextServicePeriods: data.nextServicePeriods});
      },
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
    }).fail(error => {
      console.log('Error while sending service.', error);
    });
  }

  render(){
    const serviceButtons = (uid) => (this.state.nextServicePeriods.map(item => (
      <a key={item}
        className="dropdown-item"
        href="#"
        onClick={e => {e.preventDefault(); this.addService(uid, item);}}>
          {item}
      </a>
    )))
    const serviceToolbar = (uid) => (<div className="btn-group" role="group">
        <button id="btnGroupDrop1" type="button"
          className="btn btn-sm btn-secondary dropdown-toggle"
          data-toggle="dropdown" aria-haspopup="true"
          aria-expanded="false">
            Service
        </button>
        <div className="dropdown-menu" aria-labelledby="btnGroupDrop1">
          {serviceButtons(uid)}
        </div>
      </div>);
    const body = this.state.list.map(user => (
      <tr key={user.id}>
        <td>€ {(user.balance/100).toFixed(2)}</td>
        <td><a href={user.switch_url}>{user.name}</a></td>
        <td>{user.vip ? '' : user.score.toFixed(4)}</td>
        <td>{user.vip ? '' : serviceToolbar(user.id)}</td>
        <td>{user.last_service.toLocaleDateString()}</td>
      </tr>
    ));
    return <table className="table table-striped table-hover">
      <thead>
        <tr>
          <th><a href="#" onClick={e => {e.preventDefault(); this.changeOrder("balance");}}>Balance</a></th>
          <th>User</th>
          <th colSpan="2"><a href="#" onClick={e => {e.preventDefault(); this.changeOrder("score");}}>Score</a></th>
          <th><a href="#" onClick={e => {e.preventDefault(); this.changeOrder("last_service");}}>Last Service</a></th>
        </tr>
      </thead>
      <tbody>
        {body}
      </tbody>
    </table>
  }
}
