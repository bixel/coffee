import React from 'react';

export function Icon(props) {
  return <span><img
    src={props.product.icon}
    alt={props.product.name}
    height={props.size}
    width={props.size}
    />
  </span>
}
