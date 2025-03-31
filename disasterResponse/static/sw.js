self.addEventListener('push', event => {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: '/static/icon.png' // Optional: add an icon in your static folder
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});