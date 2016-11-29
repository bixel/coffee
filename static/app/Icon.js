import React from 'react';

export function Icon(props) {
    return(
        <img src={props.product.icon} alt={props.product.name} height="24" width="24" />
    )
}
