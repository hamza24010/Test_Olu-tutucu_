// connector.js
// This script initializes the QWebChannel connection
// Ensure qwebchannel.js is loaded BEFORE this script

document.addEventListener("DOMContentLoaded", function () {
    if (typeof qt !== "undefined" && typeof qt.webChannelTransport !== "undefined") {
        console.log("Qt WebChannel Transport found.");
        new QWebChannel(qt.webChannelTransport, function (channel) {
            // Make bridge object accessible globally
            window.bridge = channel.objects.bridge;
            console.log("Connected to Python Bridge.");

            // Optional: Notify Python we are ready
            if (window.bridge && window.bridge.log) {
                window.bridge.log("Page loaded: " + document.title);
            }
        });
    } else {
        console.warn("Qt WebChannel Transport NOT found. Are you running inside the Desktop App?");
    }
});
