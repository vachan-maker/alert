async function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) {
        console.error("Service workers are not supported.");
        return;
    }

    try {
        const registration = await navigator.serviceWorker.register("/service-worker.js");
        console.log("Service Worker registered:", registration);
    } catch (error) {
        console.error("Service Worker registration failed:", error);
    }
}

async function subscribeUser() {
    const registration = await navigator.serviceWorker.ready;
    const response = await fetch("/vapidPublicKey");
    const { publicKey } = await response.json();

    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey),
    });

    await fetch("/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(subscription),
    });

    console.log("User subscribed!");
}

// Helper function to convert VAPID public key
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map((char) => char.charCodeAt(0)));
}

// Register the service worker & subscribe the user
registerServiceWorker().then(subscribeUser);