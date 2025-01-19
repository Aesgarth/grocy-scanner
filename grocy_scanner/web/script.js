const video = document.getElementById('camera');
const startScanButton = document.getElementById('start-scan');
const beepSound = document.getElementById('beep');

let scanning = false;

// Initialize the camera
async function startCamera() {
    const video = document.getElementById('camera');
    console.log("Initializing camera...");
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        console.log("Camera initialized successfully:", stream);
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            console.log("Metadata loaded, playing video.");
            video.play();
        };
    } catch (error) {
        console.error("Error initializing camera:", error);
        const message = document.getElementById('message');
        message.textContent = "Failed to access the camera. Please check permissions.";
    }
}

// Function to start scanning
function startScanning() {
    if (scanning) return;

    scanning = true;
    console.log("Scanning started...");

    // Simulate barcode scanning using a timer (replace this with QuaggaJS or ZXing integration)
    setTimeout(() => {
        scanning = false;
        beepSound.play();
        console.log("Barcode detected: 123456789");
        alert("Barcode detected: 123456789");
    }, 3000); // Simulates a barcode scan after 3 seconds
}

// Attach event listeners
startScanButton.addEventListener('click', startScanning);

// Start the camera on page load
startCamera();
