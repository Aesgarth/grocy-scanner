# Grocy Item Scanner Addon Requirements

## Core Features

### Barcode Scanning

- Use the device’s camera to scan product barcodes.
- Retrieve product information from an external database (e.g., OpenFoodFacts or similar free APIs).
- Allow users to specify an external API key for additional databases.

### Grocy Integration

- **Automatic Detection of Grocy URL:**
  - Automatically detect the Grocy instance if it’s running as a Home Assistant addon.
  - Use ingress to interact with Grocy for seamless integration.
- **Inventory Management:**
  - Check if the scanned product exists in Grocy:
    - If it exists, add it to the inventory with optional quantity input.
    - Provide options to consume the item (e.g., as used or spoiled).
  - If it doesn’t exist, create the product in Grocy with the following details:
    - Name.
    - Default Location.
    - Quantity Unit (stock, purchase, consume, and prices).

### Web UI

- Accessible through Home Assistant’s sidebar using ingress.
- Provide a settings page to configure the addon:
  - Manual Grocy URL configuration (if automatic detection fails).
  - External API key for product lookup (optional).
- Include a testing interface for configuration validation (e.g., testing Grocy and external API connectivity).

## Technical Requirements

### Ingress Support

- Use ingress for seamless integration into Home Assistant’s UI.
- Dynamically handle ingress ports (no fixed port required for ingress).
- Direct access is optional and not required.

### Static Files

- Serve static files (e.g., `index.html`, `style.css`, `app.js`) for the web UI.
- Ensure proper routing for all static assets.

### Backend Logic

- Use a backend framework (e.g., Flask, FastAPI, or another lightweight alternative) for API handling.
- Provide the following API endpoints:
  - `/scan`: Handle barcode scanning requests.
  - `/config`: Manage configuration and validation.
  - `/health`: Provide a health check endpoint for debugging.

### Dockerized Addon

- Package the addon as a Docker container.
- Ensure compatibility with Home Assistant Supervisor.
- Follow Home Assistant addon best practices (e.g., ingress, schema validation, minimal dependencies).

### Error Handling and Logging

- Provide clear error messages for common issues (e.g., Grocy connectivity, invalid barcodes).
- Implement detailed logging for debugging.

## Optional Features

### Offline Mode

- Cache recently scanned products for offline use (fallback when external APIs are unavailable).

### Localization

- Support multiple languages for the web UI and API responses.

### Custom Grocy Actions

- Allow users to define additional actions for scanned products (e.g., define quantity, add or remove from inventory).

### Enhancements for Grocy Detection

- Automatically configure the Grocy instance based on Home Assistant’s internal API or environment variables.

## Development Workflow

1. **Define Addon Configuration:**
   - Implement `config.yaml` with the appropriate schema for addon settings.
2. **Backend Development:**
   - Build the API and logic for barcode scanning and Grocy integration.
3. **Frontend Development:**
   - Develop the web UI for scanning, settings, and testing.
4. **Testing:**
   - Test functionality locally before deploying to Home Assistant.
5. **Integration:**
   - Deploy the addon and verify ingress, Grocy connectivity, and API responses.
