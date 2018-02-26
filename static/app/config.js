let BASEURL = window.location.origin + window.location.pathname;

let URLs = {
  addConsumption: BASEURL + 'api/add_consumption/',
}

module.exports = {
  BASEURL, URLs
};
