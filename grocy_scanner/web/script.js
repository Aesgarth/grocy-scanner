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
        // Handle the barcode
        handleScannedBarcode(barcode);
    });
}

async function handleScannedBarcode(barcode) {
    message.textContent = "Checking barcode in Grocy...";
    try {
        console.log("Sending barcode to backend:", barcode);

        const response = await fetch("/api/check-barcode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ barcode })
        });

        console.log("Response received:", response);

        if (!response.ok) {
            // Log response details for debugging
            console.error("Response error:", response.status, response.statusText);
            message.textContent = `Error: ${response.statusText}. Please try again.`;
            return;
        }

        const result = await response.json();
        console.log("Parsed response JSON:", result);

        if (result.status === "success") {
            const product = result.product;
            message.textContent = `Product found: ${product.name}. What would you like to do?`;
            // TODO: Show UI options to add or remove quantity
        } else if (result.status === "not_found") {
            message.textContent = "Product not found in Grocy. Would you like to add it?";
            // TODO: Provide options to add barcode to an existing product or create a new one
        } else {
            message.textContent = `Error: ${result.message}`;
        }
    } catch (error) {
        console.error("Error checking barcode in Grocy:", error);
        message.textContent = "Error checking barcode. Please try again.";
    }
}


// Attach event listeners
startScanButton.addEventListener('click', startScanning);

// Start the camera on page load
startCamera();
