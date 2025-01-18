// Initialize QuaggaJS for barcode scanning
function startScanner() {
    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: document.querySelector('#scanner-container') // Target element
        },
        decoder: {
            readers: ["code_128_reader"] // Supported barcode type
        }
    }, function (err) {
        if (err) {
            console.error("Scanner initialization failed:", err);
            return;
        }
        console.log("Scanner initialized");
        Quagga.start();
    });

    Quagga.onDetected(function (data) {
        const barcode = data.codeResult.code;
        console.log("Barcode detected:", barcode);

        // Send barcode to the backend
        fetch(`/scan/${barcode}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to fetch product data");
                }
                return response.json();
            })
            .then(productData => {
                console.log("Product Data:", productData);
                alert(`Product found: ${productData.product.product_name}`);
            })
            .catch(error => {
                console.error("Error fetching product data:", error);
                alert("Product not found.");
            });
    });
}

// Event listener for the button
document.querySelector("button").addEventListener("click", startScanner);
