// Gets the base URL for the backend API. In local testing, this is http://localhost:5000/. In
// production, this is https://itsc4155.abus.sh/
export function getBackendURL() {
    return window.origin.replace("4200", "5000");
}

// Gets the amount of time to cache Canvas API results in seconds.
export function getCanvasCacheTime() {
    return 30;
}