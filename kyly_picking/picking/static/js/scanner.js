(function () {
    class LiveBarcodeScanner {
        constructor(options = {}) {
            this.video = options.video || null;
            this.statusElement = options.statusElement || null;
            this.onDetect = options.onDetect || (() => {});
            this.formats = Array.isArray(options.formats) ? options.formats : [];
            this.stream = null;
            this.detector = null;
            this.active = false;
            this.rafId = null;
            this.lastDetectedValue = "";
            this.lastDetectedAt = 0;
        }

        static hasCameraSupport() {
            return Boolean(
                navigator.mediaDevices &&
                typeof navigator.mediaDevices.getUserMedia === "function"
            );
        }

        static hasDetectionSupport() {
            return Boolean(window.BarcodeDetector);
        }

        static isSupported() {
            return Boolean(
                LiveBarcodeScanner.hasCameraSupport()
            );
        }

        static async getFormats(preferredFormats = []) {
            if (!window.BarcodeDetector) {
                return [];
            }

            let supportedFormats = [];
            if (typeof window.BarcodeDetector.getSupportedFormats === "function") {
                try {
                    supportedFormats = await window.BarcodeDetector.getSupportedFormats();
                } catch (error) {
                    supportedFormats = [];
                }
            }

            if (!supportedFormats.length) {
                return preferredFormats;
            }

            const filtered = preferredFormats.filter((format) => supportedFormats.includes(format));
            return filtered.length ? filtered : supportedFormats;
        }

        setStatus(message, type = "neutral") {
            if (!this.statusElement) {
                return;
            }
            this.statusElement.textContent = message;
            this.statusElement.dataset.state = type;
        }

        async start() {
            if (!LiveBarcodeScanner.hasCameraSupport()) {
                this.setStatus("Camera nao suportada neste navegador.", "error");
                return false;
            }

            if (!this.video) {
                this.setStatus("Video do leitor nao configurado.", "error");
                return false;
            }

            try {
                this.video.setAttribute("autoplay", "true");
                this.video.setAttribute("muted", "true");
                this.video.setAttribute("playsinline", "true");

                this.stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: { ideal: "environment" },
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                    },
                    audio: false,
                });
                this.video.srcObject = this.stream;
                this.active = true;

                try {
                    await this.video.play();
                } catch (playError) {
                    this.setStatus(
                        "Camera liberada. Se a imagem nao aparecer, toque na area do scanner.",
                        "warning"
                    );
                }

                if (LiveBarcodeScanner.hasDetectionSupport()) {
                    const formats = await LiveBarcodeScanner.getFormats(
                        this.formats.length ? this.formats : ["code_39", "code_128", "qr_code"]
                    );
                    this.detector = new window.BarcodeDetector({ formats });
                    this.setStatus("Camera ativa. Posicione o codigo dentro da moldura.", "success");
                    this.scanLoop();
                } else {
                    this.detector = null;
                    this.setStatus(
                        "Camera ativa, mas este navegador nao possui leitor nativo de codigo de barras.",
                        "warning"
                    );
                }

                return true;
            } catch (error) {
                const denied = error && error.name === "NotAllowedError";
                this.setStatus(
                    denied
                        ? "Permissao de camera negada. Libere a camera para escanear."
                        : "Nao foi possivel iniciar a camera do leitor.",
                    "error"
                );
                this.stop();
                return false;
            }
        }

        stop() {
            this.active = false;
            if (this.rafId) {
                window.cancelAnimationFrame(this.rafId);
                this.rafId = null;
            }
            if (this.video) {
                this.video.pause();
                this.video.srcObject = null;
            }
            if (this.stream) {
                this.stream.getTracks().forEach((track) => track.stop());
                this.stream = null;
            }
        }

        async scanLoop() {
            if (!this.active || !this.video || !this.detector) {
                return;
            }

            try {
                const results = await this.detector.detect(this.video);
                if (results.length) {
                    const rawValue = (results[0].rawValue || "").trim();
                    const now = Date.now();
                    if (
                        rawValue &&
                        (rawValue !== this.lastDetectedValue || now - this.lastDetectedAt > 1500)
                    ) {
                        this.lastDetectedValue = rawValue;
                        this.lastDetectedAt = now;
                        await this.onDetect(rawValue, results[0]);
                    }
                }
            } catch (error) {
                this.setStatus("Falha momentanea na leitura. Tente aproximar o codigo.", "warning");
            }

            this.rafId = window.requestAnimationFrame(() => this.scanLoop());
        }
    }

    window.LiveBarcodeScanner = LiveBarcodeScanner;
})();
