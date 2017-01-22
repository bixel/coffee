import React from 'react';
import classnames from 'classnames';

const styles = {
  outer: {
    position: "fixed",
    width: "100%",
    height: "100%",
    top: 0,
    left: 0,
  },
  inner: {
    padding: "5px",
    width: "100%",
    backgroud: "#C0C7BF",
  },
}

export default function Alert(props) {
  const classes = classnames('alert show', 'alert-' + props.type || 'info')
  console.log(classes);
  return <div style={styles.outer}><div style={styles.inner}>
    <div className={classes} role="alert">
      {props.children}
    </div>
  </div></div>
}
