import React from 'react';
import classnames from 'classnames';

const styles = {
  outer: {
    position: "fixed",
    width: "100%",
    top: 0,
    left: 0,
  },
  inner: {
    padding: "5px",
    width: "100%",
    backgroud: "#C0C7BF",
  },
  text: {
    fontSize: "240%",
  },
}

export default function Alert(props) {
  const classes = classnames('alert show', 'alert-' + props.type || 'info')
  return <div style={styles.outer}><div style={styles.inner}>
    <div className={classes} role="alert" style={styles.text}>
      <h4>Lieber Kaffeenutzer</h4>
      {props.children}
    </div>
  </div></div>
}
