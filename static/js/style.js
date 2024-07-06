// Add this to your existing JavaScript file (style.js)

document.getElementById('toggle-login').addEventListener('click', function() {
    document.getElementById('signup-box').style.transform = 'translateX(-100%)';
    document.getElementById('login-box').style.transform = 'translateX(0)';
    document.getElementById('signup-box').style.opacity = '0';
    document.getElementById('login-box').style.opacity = '1';
});

document.getElementById('toggle-signup').addEventListener('click', function() {
    document.getElementById('signup-box').style.transform = 'translateX(0)';
    document.getElementById('login-box').style.transform = 'translateX(100%)';
    document.getElementById('signup-box').style.opacity = '1';
    document.getElementById('login-box').style.opacity = '0';
});

function showThankYouMessage(formType) {
    document.getElementById('signup-box').style.display = 'none';
    document.getElementById('login-box').style.display = 'none';
    document.getElementById('thank-you-message').style.display = 'block';

    if (formType === 'signup') {
        document.getElementById('thank-you-message').innerHTML = `
            <h2>Thank You for Joining!</h2>
            <p>Your account has been created successfully. Please check your email to verify your account.</p>
            <button onclick="location.href='{{ url_for('home') }}'" class="btn">Go to Home</button>
        `;
    } else {
        document.getElementById('thank-you-message').innerHTML = `
            <h2>Welcome Back!</h2>
            <p>You have successfully logged in.</p>
            <button onclick="location.href='{{ url_for('home') }}'" class="btn">Go to Home</button>
        `;
    }
    return false;
}



