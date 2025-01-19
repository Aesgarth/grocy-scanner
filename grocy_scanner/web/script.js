const video = document.getElementById("camera");
const startScanButton = document.getElementById("start-scan");
const message = document.getElementById("message");
const beepSound = document.getElementById("beep");

let scanning = false;
let handledBarcodes = new Set(); // Initialize as a Set to track unique barcodes

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
    handledBarcodes.clear();
    
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
        const response = await fetch(`${BASE_PATH}/api/check-barcode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ barcode })
        });

        if (!response.ok) {
            message.textContent = `Error: ${response.statusText}. Please try again.`;
            return;
        }

        const result = await response.json();

        if (result.status === "success") {
            const product = result.product;
            if (product && product.product_name) {
                message.textContent = `Product found: ${product.product_name}. What would you like to do?`;
                showActions(barcode); // Show action buttons
            } else {
                message.textContent = "Product details not available.";
            }
        } else if (result.status === "not_found") {
            message.textContent = "Product not found in Grocy. Would you like to add it?";
        } else {
            message.textContent = `Error: ${result.message}`;
        }
    } catch (error) {
        console.error("Error checking barcode in Grocy:", error);
        message.textContent = "Error checking barcode. Please try again.";
    }
}

function showActions(barcode) {
    const actionsDiv = document.getElementById("actions");
    const purchaseButton = document.getElementById("purchase-button");
    const consumeButton = document.getElementById("consume-button");
    const openButton = document.getElementById("open-button");

    actionsDiv.style.display = "block";

    purchaseButton.onclick = () => performAction("purchase", barcode);
    consumeButton.onclick = () => performAction("consume", barcode);
    openButton.onclick = () => performAction("open", barcode);
}

async function performAction(action, barcode) {
    const quantity = document.getElementById("quantity").value || 1;
    const endpoint = {
        purchase: "/api/purchase-product",
        consume: "/api/consume-product",
        open: "/api/open-product",
    }[action];

    const body = action === "open" ? { barcode } : { barcode, quantity };

    try {
        const response = await fetch(`${BASE_PATH}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        const result = await response.json();
        if (result.status === "success") {
            message.textContent = result.message;
        } else {
            message.textContent = `Error: ${result.message}`;
        }
    } catch (error) {
        console.error(`Error performing ${action}:`, error);
        message.textContent = `Error performing ${action}. Please try again.`;
    }
}

// Attach event listeners
startScanButton.addEventListener('click', startScanning);

// Start the camera on page load
startCamera();
