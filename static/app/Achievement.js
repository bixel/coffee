import React from 'react';

let achievementTypes = {
  first_coffee_of_the_day: {
    className: "fab fa-earlybirds",
    style: {color: "Tomato"}
  },
  symmetric_coffee: {
    className: "fas fa-expand-arrows-alt",
    style: {color: "Green"}
  },
  minimalist: {
    className: "fas fa-money-bill-alt",
    style: {color: "Purple"}
  }
};

export default function Achievement(props) {
  let faProps = achievementTypes[props.type];
  return (
    <i className={faProps.className} style={faProps.style} />
  );
}
