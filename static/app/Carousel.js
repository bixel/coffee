import React from 'react';

let carouselDivStyle = {
  marginLeft: "50px",
  marginBottom: "30px",
  height: "440px",
  width: "500px"
};

export default function Carousel(props) {
  var serviceUser = props.service.name;
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
            <h3>Service: {serviceUser}</h3>
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
