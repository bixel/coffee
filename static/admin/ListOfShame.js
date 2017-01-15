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
    }
  }

  componentDidMount(){
    $.getJSON(this.url + 'api/listofshame/', (data) => {
      this.setState({
        list: data.list.sort(this.listOrder[this.state.order]),
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

  render(){
    const body = this.state.list.map(user => (
      <tr key={user.id}>
        <td>€ {(user.balance/100).toFixed(2)}</td>
        <td><a href={user.switch_url}>{user.name}</a></td>
        <td>{user.score.toFixed(4)}</td>
      </tr>
    ));
    return <table className="table table-striped table-hover">
      <thead>
        <tr>
          <th><a href="#" onClick={() => this.changeOrder("balance")}>Balance</a></th>
          <th>User</th>
          <th><a href="#" onClick={() => this.changeOrder("score")}>Score</a></th>
        </tr>
      </thead>
      <tbody>
        {body}
      </tbody>
    </table>
  }
}
