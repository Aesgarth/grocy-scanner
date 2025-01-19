const video = document.getElementById("camera");
const startScanButton = document.getElementById("start-scan");
const message = document.getElementById("message");
const beepSound = document.getElementById("beep");

let scanning = false;

// Initialize the camera
async function startCamera() {
    const video = document.getElementById('camera');
    console.log("Initializing camera...");
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        console.log("Camera initialized successfully:", stream);
        video.srcObject = stream;

        // Ensure the video starts playing
        video.onloadedmetadata = () => {
            console.log("Metadata loaded, playing video.");
            video.play().then(() => {
                console.log("Video playing.");
            }).catch((error) => {
                console.error("Error playing video:", error);
            });
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

    message.textContent = "Initializing scanner...";
    console.log("Scanner initialized.");

    Quagga.init(
        {
            inputStream: {
                type: "LiveStream",
                target: video, // Attach to video element
                constraints: {
                    facingMode: "environment" // Use rear-facing camera
                }
            },
            decoder: {
                readers: ["code_128_reader", "ean_reader", "ean_8_reader"] // Add other barcode formats as needed
            }
        },
        (err) => {
            if (err) {
                console.error("Error initializing Quagga:", err);
                message.textContent = "Failed to initialize scanner.";
                scanning = false;
                return;
            }

            message.textContent = "Scanning for barcodes...";
            Quagga.start();
            console.log("Quagga started.");
        }
    );

    Quagga.onDetected((data) => {
        const barcode = data.codeResult.code;
        console.log("Barcode detected:", barcode);
        beepSound.play();
        message.textContent = `Barcode detected: ${barcode}`;

        // Stop scanning automatically after detection
        Quagga.stop();
        scanning = false;
    });
}

// Attach event listeners
startScanButton.addEventListener('click', startScanning);

// Start the camera on page load
startCamera();
