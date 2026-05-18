const SoundEffects = {
    successPath: "/static/audio/bipe.mp3",
    errorPath: "/static/audio/bipeerro.mp3",

    playSuccess() {
        return this.play(this.successPath, "success");
    },

    playError() {
        return this.play(this.errorPath, "error");
    },

    play(path, tone) {
        return new Promise((resolve) => {
            const audio = new Audio(path);
            let finished = false;

            const finalize = () => {
                if (finished) {
                    return;
                }
                finished = true;
                resolve();
            };

            const fallback = () => {
                this.playFallbackTone(tone);
                finalize();
            };

            audio.preload = "auto";
            audio.volume = 1;
            audio.addEventListener("ended", finalize, { once: true });
            audio.addEventListener("error", fallback, { once: true });

            audio.play().then(() => {
                window.setTimeout(finalize, 280);
            }).catch(fallback);
        });
    },

    playFallbackTone(tone) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) {
            return;
        }

        const context = new AudioContextClass();
        const oscillator = context.createOscillator();
        const gainNode = context.createGain();

        oscillator.type = tone === "error" ? "sawtooth" : "square";
        oscillator.frequency.value = tone === "error" ? 220 : 920;
        gainNode.gain.setValueAtTime(0.0001, context.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.18, context.currentTime + 0.02);
        gainNode.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.18);

        oscillator.connect(gainNode);
        gainNode.connect(context.destination);
        oscillator.start();
        oscillator.stop(context.currentTime + 0.2);
        oscillator.onended = () => context.close();
    },
};

window.SoundEffects = SoundEffects;
