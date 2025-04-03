self.addEventListener('push', event => {
    console.log('Push event received:', event);

    if (event.data) {
        const notificationData = event.data.json();
        console.log('Notification Data:', notificationData);

        self.registration.showNotification(notificationData.title, {
            body: notificationData.body,
            icon: '/static/image/192.png',
            data: { url: notificationData.url },
            actions: [
                { action: 'open_url', title: 'View Alert' }
            ]
        });
    }
});

self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);

    event.notification.close();  // Close the notification

    if (event.action === 'open_url') {  // Button click action
        const url = event.notification.data?.url || '/';
        event.waitUntil(clients.openWindow(url));
    } else {  // Default click (outside button)
        const url = event.notification.data?.url || '/';
        event.waitUntil(
            clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
                for (let client of windowClients) {
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                return clients.openWindow(url);
            })
        );
    }
});
