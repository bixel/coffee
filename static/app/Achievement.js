import React from 'react';

let achievementTypes = {
  first_coffee_of_the_day: {
    className: "fab fa-earlybirds",
    style: {color: "Tomato"}
  },
};

export default function Achievement(props) {
  let faProps = achievementTypes[props.type];
  return (
    <i className={faProps.className} style={faProps.style} />
  );
}
