window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const to_deletes = document.querySelectorAll('to_deletes')
for(let i = 0; i < to_deletes.length; i++) {
  const to_delete = to_deletes[i];
  to_delete.onclick = function (e) {
    console.log('event', e);
    
  }
}

