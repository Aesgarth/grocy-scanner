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
    if (scanning) return; // Prevent multiple initializations
    scanning = true;

    message.textContent = "Initializing scanner...";
    console.log("Scanner initialized.");

    Quagga.init(
        {
            inputStream: {
                type: "LiveStream",
                target: video,
                constraints: { facingMode: "environment" },
            },
            decoder: {
                readers: ["code_128_reader", "ean_reader", "ean_8_reader"],
            },
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
        if (handledBarcodes.has(barcode)) {
            console.log(`Barcode ${barcode} already handled.`);
            return;
        }
        handledBarcodes.add(barcode);
        console.log("Barcode detected:", barcode);
        beepSound.play();

        // Stop scanning after detecting a barcode
        Quagga.stop();
        scanning = false;

        // Handle the detected barcode
        handleScannedBarcode(barcode);
    });
}

const BASE_PATH = window.location.pathname.replace(/\/$/, "");


async function handleScannedBarcode(barcode) {
    message.textContent = "Checking barcode in Grocy...";
    try {
        console.log("Sending barcode to backend:", barcode);

        const response = await fetch(`${BASE_PATH}/api/check-barcode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ barcode }),
        });

        if (!response.ok) {
            console.error("Response error:", response.status, response.statusText);
            message.textContent = `Error: ${response.statusText}. Please try again.`;
            handledBarcodes.delete(barcode); // Allow re-scan if it failed
            return;
        }

        const result = await response.json();
        console.log("Response JSON:", result);

        if (result.status === "success") {
            const product = result.product;
            message.textContent = `Product found: ${product.name}. What would you like to do?`;
            // TODO: Add UI options for add/remove quantity
        } else if (result.status === "not_found") {
            message.textContent = "Product not found in Grocy. Would you like to add it?";
            // TODO: Add options for creating or associating the product
        } else {
            message.textContent = `Error: ${result.message}`;
        }
    } catch (error) {
        console.error("Error checking barcode in Grocy:", error);
        message.textContent = "Error checking barcode. Please try again.";
        handledBarcodes.delete(barcode); // Allow re-scan if it failed
    }
}

// Attach event listeners
startScanButton.addEventListener('click', startScanning);

// Start the camera on page load
startCamera();
