const link = document.getElementById("link_for_json");
const URL = link.href;

const time = 1000;

function sendRequest(method, url, body = null) {
    const headers = {
        "Content-Type": "application/json"
    };

    // Проверяем метод запроса и устанавливаем тело, если это не GET
    const requestOptions = {
        method: method,
        headers: headers
    };

    if (method !== 'GET' && body !== null) {
        requestOptions.body = JSON.stringify(body);
    }

    return fetch(url, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            throw error;
        });
}


function updateChat(){
// Пример использования
sendRequest('GET', URL)
    .then(data => {
        const myBlock = document.getElementById('main_for_messages');
        user = data.messages[0];
        textHtml = "";
        for (let i = 1; i < data.messages.length; i++) {
            message = data.messages[i];
            if (message.user_id === user.id_user_real_time){
                textHtml += `
                <div class="msg right-msg">
                    <div class="msg-img"></div>
                    <div class="msg-bubble">
                        <div class="msg-info">
                            <div class="msg-info-name">${message.user_name}</div>
                            <div class="msg-info-time">${message.created_at}</div>
                        </div>
                        <div class="msg-text">${message.message}</div>
                    </div>
                </div>`;
            }
            else{
                textHtml += `
                <div class="msg left-msg">
                    <div class="msg-img"></div>
                        <div class="msg-bubble">
                            <div class="msg-info">
                                <div class="msg-info-name">${message.user_name}</div>
                                <div class="msg-info-time">${message.created_at}</div>
                            </div>
                        <div class="msg-text">${message.message}</div>
                    </div>
                </div>
                `;
            }
        }
        myBlock.innerHTML = textHtml;
        myBlock.scrollTop = myBlock.scrollHeight;
    })
    .catch(error => {
        console.error('Error after fetch:', error);
    });
}

async function addMessage(){
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;

    // Проверяем, чтобы не отправлять пустые сообщения
    if (message.trim() !== ''){
        const data = {message: message}
        try {
            const response = await sendRequest("POST", URL, data);
            console.log(response);
            // После успешной отправки данных очищаем поле ввода
            messageInput.value = "";
        } catch (error) {
            console.error('Error after fetch:', error);
        }
    }
}

// Получаем ссылки на кнопку и поле ввода по их id
const sendButton = document.getElementById('my_button');

// Добавляем обработчик события к кнопке
sendButton.addEventListener('click', addMessage);

// Инициировать первое обновление чата
updateChat();

// Запускать обновление чата каждые 5 секунд
setInterval(updateChat, time);

setInterval(function() {
        fetch('/update_status', {method: 'POST'});
    }, 60000);  // Каждую минуту