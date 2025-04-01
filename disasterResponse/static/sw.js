self.addEventListener('push', event => {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: '/static/icon.png', // Optional: add an icon in your static folder
        data: { url: notificationData.url }, // URL to open when the notification is clicked
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});
