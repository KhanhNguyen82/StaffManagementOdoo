/** @odoo-module **/

(function () {
    // Detect Chrome version
    function getChromeVersion() {
        const raw = navigator.userAgent.match(/Chrom(e|ium)\/([0-9]+)\./);
        return raw ? parseInt(raw[2], 10) : null;
    }

    const chromeVersion = getChromeVersion();
    console.log("Detected Chrome version:", chromeVersion);


    if (typeof Promise.withResolvers !== "function" || (chromeVersion && chromeVersion < 120)) {
        Promise.withResolvers = function () {
            let resolve, reject;
            const promise = new Promise((res, rej) => {
                resolve = res;
                reject = rej;
            });
            return { promise, resolve, reject };
        };
        console.log("✅ Polyfill Promise.withResolvers loaded");
    } else {
        console.log("⚡ Native Promise.withResolvers available");
    }
})();

