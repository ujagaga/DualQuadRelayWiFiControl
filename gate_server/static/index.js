
function addTimestampToLinks() {
  const timestamp = new Date().getTime();

  const links = document.querySelectorAll('a.big_btn');

  links.forEach(function(link) {
    const href = link.getAttribute('href');

    if (href.includes('?')) {
      // If there's a query string, append the timestamp with an '&'
      link.setAttribute('href', href + '&timestamp=' + timestamp);
    } else {
      // If there's no query string, append the timestamp with a '?'
      link.setAttribute('href', href + '?timestamp=' + timestamp);
    }
  });
}

addTimestampToLinks();