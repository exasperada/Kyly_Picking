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

    setupRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            return;
        }
        this.recognition = new SpeechRecognition();
        this.recognition.lang = "pt-BR";
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        this.recognition.onresult = (event) => {
            const command = event.results[0][0].transcript.toLowerCase();
            if (command.includes("confirm")) {
                document.getElementById("btn-confirmar")?.click();
            } else if (command.includes("pular")) {
                document.getElementById("btn-pular")?.click();
            } else if (command.includes("erro")) {
                document.getElementById("btn-erro")?.click();
            } else if (command.includes("falta")) {
                document.getElementById("btn-falta")?.click();
            }
        };
        this.recognition.onend = () => {
            if (this.active) {
                this.recognition.start();
            }
        };
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
        if (this.active) {
            this.recognition.start();
        } else {
            this.recognition.stop();
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
