const URL = "/ajax_messages";

function sendRequest(method, url, body = null){
  return new Promise((resolve) => {
    const xhr = new XMLHttpRequest();

    xhr.open(method, url);

    xhr.responseType = 'json';
    xhr.setRequestHeader("Content-type", "application/json");

    xhr.onload = () => {
      resolve(xhr.response);
    }

    xhr.onerror = () => {
      resolve(xhr.response);
    };

    xhr.send(JSON.stringify(body));
  })
}


sendRequest('POST', URL, data)
  .then(data => console.log(data))
  .catch(err => console.error(err))
