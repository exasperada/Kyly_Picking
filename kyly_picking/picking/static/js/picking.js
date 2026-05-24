const Utils = {
    getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content || "";
    },

    async fetchJSON(url, options = {}) {
        const headers = {
            "Content-Type": "application/json",
            "X-CSRFToken": Utils.getCsrfToken(),
            ...(options.headers || {}),
        };
        const response = await fetch(url, { ...options, headers });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.mensagem || "Falha na requisicao.");
        }
        return data;
    },

    showFeedback(message, type = "success") {
        const feedback = document.getElementById("feedback");
        if (!feedback) {
            return;
        }
        feedback.textContent = message;
        feedback.className = `feedback show feedback-${type}`;
    },

    playSuccessSound() {
        return window.SoundEffects?.playSuccess?.() || Promise.resolve();
    },

    playErrorSound() {
        return window.SoundEffects?.playError?.() || Promise.resolve();
    },
};

const PickingPage = {
    init() {
        this.app = document.getElementById("picking-app");
        this.bindStartButtons();

        if (!this.app) {
            return;
        }

        this.itemAtual = {
            id: Number(this.app.dataset.itemId),
            pedidoId: Number(this.app.dataset.pedidoId),
            sku: this.app.dataset.sku,
            produto: this.app.dataset.produto,
            quantidade: Number(this.app.dataset.quantidade),
            quantidadeColetada: Number(this.app.dataset.coletada),
            localizacao: this.app.dataset.localizacao,
        };

        this.setupScanner();

        document.getElementById("btn-validar")?.addEventListener("click", () => this.validarSku());
        document.getElementById("btn-pular")?.addEventListener("click", () => this.pularItem());
        document.getElementById("btn-erro")?.addEventListener("click", () => this.reportarErro());
        document.getElementById("btn-falta")?.addEventListener("click", () => this.marcarFalta());
        document.getElementById("sku-input")?.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                this.validarSku();
            }
        });

        window.itemAtual = this.itemAtual;
    },

    setupScanner() {
        const openButton = document.getElementById("btn-abrir-camera-sku");
        const closeButton = document.getElementById("btn-fechar-camera-sku");
        const statusElement = document.getElementById("sku-scanner-status");
        const input = document.getElementById("sku-input");

        if (!window.LiveBarcodeScanner || !openButton || !statusElement) {
            return;
        }

        this.scanner = new window.LiveBarcodeScanner({
            video: document.getElementById("sku-scanner-video"),
            statusElement,
            formats: ["code_39", "code_128", "qr_code"],
            onDetect: async (rawValue) => {
                const normalizedValue = rawValue.trim().toUpperCase();
                input.value = normalizedValue;
                statusElement.textContent = `Codigo lido: ${normalizedValue}. Validando item...`;
                statusElement.dataset.state = "success";
                await this.validarSku(true);
            },
        });

        this.backendScanTimer = null;

        openButton.addEventListener("click", async () => {
            const started = await this.scanner.start();
            if (started) {
                openButton.hidden = true;
                closeButton.hidden = false;
                this.startBackendFallbackIfNeeded();
            }
        });

        closeButton?.addEventListener("click", () => {
            this.scanner?.stop();
            this.stopBackendFallback();
            statusElement.textContent = "Camera desligada. Voce ainda pode digitar a SKU manualmente.";
            statusElement.dataset.state = "warning";
            openButton.hidden = false;
            closeButton.hidden = true;
        });

        window.setTimeout(async () => {
            const started = await this.scanner.start();
            if (started) {
                openButton.hidden = true;
                closeButton.hidden = false;
                this.startBackendFallbackIfNeeded();
            } else {
                statusElement.textContent = "Libere a camera para escanear a SKU ou digite manualmente.";
                statusElement.dataset.state = "warning";
            }
        }, 150);
    },

    startBackendFallbackIfNeeded() {
        if (window.LiveBarcodeScanner?.hasDetectionSupport?.()) {
            return;
        }

        if (this.backendScanTimer) {
            return;
        }

        const statusElement = document.getElementById("sku-scanner-status");
        statusElement.textContent = "Camera ativa. Usando leitor embutido do servidor.";
        statusElement.dataset.state = "warning";
        this.backendScanTimer = window.setInterval(() => this.decodeFrameViaBackend(), 850);
    },

    stopBackendFallback() {
        if (this.backendScanTimer) {
            window.clearInterval(this.backendScanTimer);
            this.backendScanTimer = null;
        }
    },

    captureVideoFrame() {
        const video = document.getElementById("sku-scanner-video");
        if (!video || !video.videoWidth || !video.videoHeight) {
            return null;
        }

        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext("2d", { willReadFrequently: true });
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL("image/png");
    },

    async decodeFrameViaBackend() {
        const statusElement = document.getElementById("sku-scanner-status");
        const image = this.captureVideoFrame();
        if (!image) {
            return;
        }

        try {
            const data = await Utils.fetchJSON("/api/scan/item/", {
                method: "POST",
                body: JSON.stringify({ image }),
            });

            const rawValue = (data.codigo || "").trim().toUpperCase();
            if (!rawValue) {
                return;
            }

            document.getElementById("sku-input").value = rawValue;
            statusElement.textContent = `Codigo lido: ${rawValue}. Validando item...`;
            statusElement.dataset.state = "success";
            await this.validarSku(true);
        } catch (error) {
            statusElement.textContent = "Falha na leitura pelo servidor. Centralize o codigo e aproxime mais da camera.";
            statusElement.dataset.state = "error";
        }
    },

    bindStartButtons() {
        document.querySelectorAll(".btn-iniciar-picking").forEach((button) => {
            button.addEventListener("click", async () => {
                try {
                    const data = await Utils.fetchJSON("/picking/iniciar/", {
                        method: "POST",
                        body: JSON.stringify({ numero_pedido: button.dataset.pedido }),
                    });
                    await Utils.playSuccessSound();
                    Utils.showFeedback(data.mensagem, "success");
                    setTimeout(() => window.location.reload(), 900);
                } catch (error) {
                    await Utils.playErrorSound();
                    alert(error.message);
                }
            });
        });
    },

    async validarSku(originatedFromScanner = false) {
        const skuInput = document.getElementById("sku-input");
        const statusElement = document.getElementById("sku-scanner-status");
        const skuInformado = skuInput?.value.trim().toUpperCase();

        if (!skuInformado) {
            await Utils.playErrorSound();
            Utils.showFeedback("Informe a SKU do item.", "warning");
            if (statusElement) {
                statusElement.textContent = "Nenhum codigo informado. Digite ou escaneie a SKU.";
                statusElement.dataset.state = "warning";
            }
            return;
        }

        try {
            const data = await Utils.fetchJSON("/picking/validar-sku/", {
                method: "POST",
                body: JSON.stringify({
                    item_id: this.itemAtual.id,
                    sku_informado: skuInformado,
                    quantidade: 1,
                }),
            });

            this.itemAtual.quantidadeColetada = data.quantidade_nova;
            document.getElementById("quantidade-status").textContent =
                `${data.quantidade_nova} / ${this.itemAtual.quantidade}`;
            skuInput.value = "";
            await Utils.playSuccessSound();
            Utils.showFeedback(data.mensagem, "success");
            if (statusElement) {
                statusElement.textContent = `SKU ${skuInformado} confirmada com sucesso.`;
                statusElement.dataset.state = "success";
            }

            if (data.pedido_completo) {
                Utils.showFeedback("Caixa finalizada com sucesso.", "success");
                setTimeout(() => window.location.reload(), 1200);
                return;
            }

            if (data.item_completo) {
                setTimeout(() => this.proximaColeta(), 700);
            } else if (originatedFromScanner) {
                skuInput.focus();
            }
        } catch (error) {
            await Utils.playErrorSound();
            Utils.showFeedback(error.message, "error");
            if (statusElement) {
                statusElement.textContent = error.message;
                statusElement.dataset.state = "error";
            }
        }
    },

    async pularItem() {
        try {
            const data = await Utils.fetchJSON("/picking/pular-item/", {
                method: "POST",
                body: JSON.stringify({ item_id: this.itemAtual.id }),
            });
            await Utils.playErrorSound();
            Utils.showFeedback(data.mensagem, "warning");
            const statusElement = document.getElementById("sku-scanner-status");
            if (statusElement) {
                statusElement.textContent = "Item pulado e recolocado na fila de coleta.";
                statusElement.dataset.state = "warning";
            }
            setTimeout(() => this.proximaColeta(), 600);
        } catch (error) {
            await Utils.playErrorSound();
            Utils.showFeedback(error.message, "error");
        }
    },

    async reportarErro() {
        await Utils.playErrorSound();
        const descricao = window.prompt("Descreva o erro encontrado:");
        if (!descricao) {
            return;
        }

        try {
            const data = await Utils.fetchJSON("/picking/reportar-erro/", {
                method: "POST",
                body: JSON.stringify({
                    item_id: this.itemAtual.id,
                    tipo_erro: "outro",
                    descricao,
                }),
            });
            Utils.showFeedback(data.mensagem, "warning");
        } catch (error) {
            await Utils.playErrorSound();
            Utils.showFeedback(error.message, "error");
        }
    },

    async marcarFalta() {
        try {
            const data = await Utils.fetchJSON("/picking/item-em-falta/", {
                method: "POST",
                body: JSON.stringify({
                    item_id: this.itemAtual.id,
                    descricao: "Item nao encontrado pelo operador.",
                }),
            });
            await Utils.playErrorSound();
            Utils.showFeedback(data.mensagem, "warning");
            const statusElement = document.getElementById("sku-scanner-status");
            if (statusElement) {
                statusElement.textContent = data.mensagem;
                statusElement.dataset.state = "warning";
            }
            setTimeout(() => window.location.reload(), 1200);
        } catch (error) {
            await Utils.playErrorSound();
            Utils.showFeedback(error.message, "error");
        }
    },

    async proximaColeta() {
        try {
            this.scanner?.stop();
            this.stopBackendFallback();
            await Utils.fetchJSON("/picking/proxima-coleta/", {
                method: "POST",
                body: JSON.stringify({ pedido_id: this.itemAtual.pedidoId }),
            });
            window.location.reload();
        } catch (error) {
            await Utils.playErrorSound();
            Utils.showFeedback(error.message, "error");
        }
    },
};

document.addEventListener("DOMContentLoaded", () => PickingPage.init());

window.Utils = Utils;
