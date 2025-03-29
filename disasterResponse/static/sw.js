self.addEventListener("push", function (event) {
    console.log("Push event received:", event);
    console.log("Push data:", event.data ? event.data.text() : "No data");

    let notificationData = {};
    if (event.data) {
        notificationData = event.data.json();
    }

    const options = {
        body: notificationData.body || "New notification",
        icon: "/static/icon.png",
        badge: "/static/badge.png",
        vibrate: [200, 100, 200],
        actions: [
            { action: "open", title: "Open App" },
            { action: "close", title: "Dismiss" }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(notificationData.title || "Notification", options)
    );
});
