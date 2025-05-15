document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const messageDiv = document.getElementById('message');
    
    async function sendRequest(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    }

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;
        
        const result = await sendRequest('/register', {username, password});
        if (result.success) {
            messageDiv.textContent = 'Registration successful! Please login.';
            messageDiv.style.color = 'green';
        } else {
            messageDiv.textContent = result.message;
            messageDiv.style.color = 'red';
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        const result = await sendRequest('/login', {username, password});
        if (result.success) {
            window.location.href = '/game?username=' + encodeURIComponent(username);
        } else {
            messageDiv.textContent = result.message;
            messageDiv.style.color = 'red';
        }
    });
});

