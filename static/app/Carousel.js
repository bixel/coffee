import React, {Component} from 'react';
import moment from 'moment';

let carouselDivStyle = {
  marginLeft: "50px",
  marginBottom: "30px",
  height: "440px",
  width: "500px"
};

export default class Carousel extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    var userDict = {};
    this.props.users.map(u => { userDict[u.id] = u });

    try {
      var serviceUserName = userDict[this.props.service.uid].name;
      var nextServiceUsers = this.props.service.upcoming.map((s, i) => {
        var startDate = moment(s.week + "1", "ggggwwe");
        var endDate = moment(s.week + "1", "ggggwwe").add(5, 'days');
        return (
          <tr key={i}>
            <td>{ userDict[s.user].name }</td>
            <td>{ startDate.format('DD.MM') } bis { endDate.format('DD.MM.YYYY') }</td>
          </tr>
        );
      });
      var lastCleanedDate = moment(this.props.service.last_cleaned);
      var cleanedToday = moment().isSame(lastCleanedDate, 'day') ?
        <i className="fas fa-check-circle"></i> :
        <i className="fas fa-times-circle"></i>;
    } catch(e) {
      var serviceUserName = '...';
      var nextServiceUsers = [];
      var lastCleanedDate = moment();
      var cleanedToday = "";
    }

    // build user-id -> user dict for quick access via uids.
    // This could be lifted to the server... design decisions blah
    return (
      <div id="carouselExampleIndicators" className="carousel slide" data-ride="false" data-pause="true">
        <ol className="carousel-indicators">
          <li data-target="#carouselExampleIndicators" data-slide-to="0"
            className="active"></li>
          <li data-target="#carouselExampleIndicators"
            data-slide-to="1"></li>
        </ol>
        <div className="carousel-inner">
          <div className="carousel-item active">
            <div id="coffee-hours" style={carouselDivStyle} className="plotly-graph-div col-xs-8">
            </div>
          </div>
          <div className="carousel-item">
            <div id="global-graph" style={carouselDivStyle} className="plotly-graph-div col-xs-8">
            </div>
          </div>
          <div className="carousel-item">
            <div id="service-box" style={{ ...carouselDivStyle, paddingTop: "30px" }}>
              <h3>Service Aktuell: {serviceUserName}</h3>
              <div className="row">
                <div className="col">
                  Letzte Reinigung
                </div>
                <div className="col">
                  {lastCleanedDate.format('DD.MM.YYYY')} {cleanedToday}
                </div>
              </div>
              <div className="row">
                <div className="col">
                  Reinigung eintragen
                </div>
                <div className="col">
                  <button
                    role="button"
                    className="btn btn-primary"
                    onClick={e => {
                      e.preventDefault();
                      this.props.sendService("cleaned")
                    }}>
                    Jetzt gereinigt
                  </button>
                </div>
              </div>
              <h3>Nächste Dienste</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Datum</th>
                  </tr>
                </thead>
                <tbody>
                  {nextServiceUsers}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <a className="carousel-control-prev" href="#carouselExampleIndicators" role="button" data-slide="prev" style={{color: "#bbb"}}>
          <i className="fas fa-angle-left fa-4x"></i>
          <span className="sr-only">Previous</span>
        </a>
        <a className="carousel-control-next" href="#carouselExampleIndicators" role="button" data-slide="next" style={{color: "#bbb"}}>
          <i className="fas fa-angle-right fa-4x"></i>
          <span className="sr-only">Next</span>
        </a>
      </div>
    );
  }
}
