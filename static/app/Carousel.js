import React from 'react';

let carouselDivStyle = {
  marginLeft: "50px",
  marginBottom: "30px",
  height: "440px",
  width: "500px"
};

export default function Carousel(props) {
  var serviceUserName = props.service.name;
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
                10.01.18 <i className="fas fa-check-circle"></i>
              </div>
            </div>
            <div className="row">
              <div className="col">
                Reinigung eintragen
              </div>
              <div className="col">
                <button role="button" className="btn btn-primary">Jetzt gereinigt</button>
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
                <tr>
                  <td></td>
                  <td></td>
                </tr>
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
