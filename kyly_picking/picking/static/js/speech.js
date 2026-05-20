const SpeechService = {
    isSupported() {
        return "speechSynthesis" in window;
    },

    speak(text) {
        if (!this.isSupported()) {
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "pt-BR";
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
    },
};

const VoiceControl = {
    recognition: null,
    active: false,
    restartTimer: null,

    normalize(text) {
        return (text || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^\w\s]/g, " ")
            .replace(/\s+/g, " ")
            .trim();
    },

    showStatus(message, type = "warning") {
        window.Utils?.showFeedback?.(message, type);
        const statusElement = document.getElementById("sku-scanner-status");
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.dataset.state = type === "error" ? "error" : type;
        }
    },

    setButtonState() {
        const button = document.getElementById("btn-voice-control");
        if (!button) {
            return;
        }
        button.classList.toggle("is-listening", this.active);
        button.textContent = this.active ? "Ouvindo voz" : "Comando por voz";
    },

    getTranscript(event) {
        const alternatives = [];
        for (let index = event.resultIndex; index < event.results.length; index += 1) {
            const result = event.results[index];
            for (let altIndex = 0; altIndex < result.length; altIndex += 1) {
                alternatives.push(result[altIndex].transcript);
            }
        }
        return alternatives.join(" ");
    },

    execute(command) {
        const normalizedCommand = this.normalize(command);

        const patterns = [
            {
                name: "confirmar",
                regex: /\b(confirmar|confirma|confirmo|confirmado|validar|valida|ok|certo|beleza)\b/,
                action: () => document.getElementById("btn-validar")?.click(),
            },
            {
                name: "pular",
                regex: /\b(pular|pula|proximo|proxima|passar|passa|ignorar|ignora)\b/,
                action: () => document.getElementById("btn-pular")?.click(),
            },
            {
                name: "erro",
                regex: /\b(erro|relatar erro|reportar erro|problema|divergencia|avaria|danificado|danificada)\b/,
                action: () => document.getElementById("btn-erro")?.click(),
            },
            {
                name: "item em falta",
                regex: /\b(falta|sem item|nao encontrado|nao achei|nao tem|acabou|ausente)\b/,
                action: () => document.getElementById("btn-falta")?.click(),
            },
        ];

        const match = patterns.find((pattern) => pattern.regex.test(normalizedCommand));
        if (!match) {
            this.showStatus(`Nao entendi: "${command}". Tente confirmar, pular, erro ou falta.`, "warning");
            return;
        }

        this.showStatus(`Comando reconhecido: ${match.name}.`, "success");
        match.action();
    },

    setupRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            return;
        }
        this.recognition = new SpeechRecognition();
        this.recognition.lang = "pt-BR";
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 3;
        this.recognition.onresult = (event) => {
            this.execute(this.getTranscript(event));
        };
        this.recognition.onnomatch = () => {
            this.showStatus("Nao consegui reconhecer o comando. Tente confirmar, pular, erro ou falta.", "warning");
        };
        this.recognition.onerror = (event) => {
            if (event.error === "no-speech") {
                this.showStatus("Nao ouvi nada ainda. Fale mais perto do microfone.", "warning");
                return;
            }
            if (event.error === "not-allowed") {
                this.active = false;
                this.setButtonState();
                this.showStatus("Permita o acesso ao microfone para usar comando por voz.", "error");
                return;
            }
            this.showStatus(`Falha no reconhecimento de voz: ${event.error}.`, "error");
        };
        this.recognition.onend = () => {
            if (this.active) {
                window.clearTimeout(this.restartTimer);
                this.restartTimer = window.setTimeout(() => this.start(), 250);
            }
        };
    },

    start() {
        try {
            this.recognition.start();
            this.showStatus("Comando por voz ativo. Fale confirmar, pular, erro ou falta.", "success");
        } catch (error) {
            this.showStatus("Comando por voz ja esta ativo.", "warning");
        }
    },

    stop() {
        window.clearTimeout(this.restartTimer);
        try {
            this.recognition.stop();
        } catch (error) {
            this.recognition.abort();
        }
        this.showStatus("Comando por voz desativado.", "warning");
    },

    toggle() {
        if (!this.recognition) {
            this.setupRecognition();
        }
        if (!this.recognition) {
            alert("Reconhecimento de voz nao suportado neste navegador.");
            return;
        }

        this.active = !this.active;
        this.setButtonState();
        if (this.active) {
            this.start();
        } else {
            this.stop();
        }
    },
};

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("btn-falar")?.addEventListener("click", () => {
        const itemAtual = window.itemAtual;
        if (!itemAtual) {
            return;
        }
        SpeechService.speak(
            `Dirija-se a ${itemAtual.localizacao} e colete ${
                itemAtual.quantidade - itemAtual.quantidadeColetada
            } unidade${itemAtual.quantidade - itemAtual.quantidadeColetada > 1 ? "s" : ""} do produto ${
                itemAtual.produto
            }.`
        );
    });

    document.getElementById("btn-voice-control")?.addEventListener("click", () => {
        VoiceControl.toggle();
    });
});
