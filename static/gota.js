document.addEventListener("DOMContentLoaded", () => {

    const gota = document.getElementById("gota-fill");
    const ojoIzq = document.getElementById("ojo-izq");
    const ojoDer = document.getElementById("ojo-der");
    const boca = document.getElementById("boca");

    if (!gota) return;

    // Inputs del formulario
    const social = document.querySelector("input[name='energia_social']");
    const fisica = document.querySelector("input[name='energia_fisica']");
    const senales = document.querySelector("select[name='senales']");
    const emocion = document.querySelector("select[name='emocion']");
    const drenantes = document.querySelector("textarea[name='drenantes']");

    const inputs = [social, fisica, senales, emocion, drenantes];

    inputs.forEach(i => i.addEventListener("input", actualizarGota));

    function actualizarGota() {
        let s = parseInt(social.value) || 0;
        let f = parseInt(fisica.value) || 0;

        let sen = senales.value;
        let emo = emocion.value;

        let dren = drenantes.value.trim() !== "" ? 1 : 0;

        // Valores base (CORREGIDOS)
        const senales_valores = {
            "Dolor de cabeza": 1,
            "Cansancio": 2,
            "Palpitaciones": 1,
            "Tensión muscular": 2,
            "Estómago revuelto": 1,
            "Respiración acelerada": 1,
            "Tranquil@": 4,
            "Neutr@": 3,
            "Estable": 4,
            "Energétic@": 5
        };

        const emociones_valores = {
            "Triste": 1,
            "Ansios@": 2,
            "Irritable": 2,
            "Estresad@": 2,
            "Cansad@": 2,
            "Neutr@": 3,
            "Tranquil@": 4,
            "En paz": 4,
            "Alegre": 5,
            "Motivad@": 5
        };

        let sen_val = senales_valores[sen] || 0;
        let emo_val = emociones_valores[emo] || 0;

        let indice = (s + f + sen_val * 2 + emo_val * 2) / 4;

        if (dren) indice -= 1;

        indice = Math.max(0, Math.min(indice, 10));

        animarGota(indice);
        actualizarCarita(indice * 10);
        actualizarColor(indice);
    }

    function animarGota(valor) {
        const porcentaje = (valor / 10) * 100;
        const alturaMax = 150;
        const altura = (porcentaje / 100) * alturaMax;

        gota.setAttribute("height", altura);
        gota.setAttribute("y", 155 - altura);
    }

    function actualizarCarita(porcentaje) {
        if (porcentaje < 30) {
            ojoIzq.setAttribute("d", "M38 90 C40 92 42 92 44 90");
            ojoDer.setAttribute("d", "M56 90 C58 92 60 92 62 90");
            boca.setAttribute("d", "M40 105 C45 100 55 100 60 105");
        } 
        else if (porcentaje < 70) {
            ojoIzq.setAttribute("d", "M38 90 L44 90");
            ojoDer.setAttribute("d", "M56 90 L62 90");
            boca.setAttribute("d", "M40 105 L60 105");
        } 
        else {
            ojoIzq.setAttribute("d", "M38 90 C40 88 42 88 44 90");
            ojoDer.setAttribute("d", "M56 90 C58 88 60 88 62 90");
            boca.setAttribute("d", "M40 102 C45 108 55 108 60 102");
        }
    }

    function actualizarColor(valor) {
        const grad = document.getElementById("grad-gota");

        if (!grad) return;

        if (valor < 3) {
            grad.children[0].setAttribute("stop-color", "#ff4d4d");
            grad.children[1].setAttribute("stop-color", "#b30000");
        } 
        else if (valor < 6) {
            grad.children[0].setAttribute("stop-color", "#ffa64d");
            grad.children[1].setAttribute("stop-color", "#ff7b00");
        } 
        else if (valor < 8) {
            grad.children[0].setAttribute("stop-color", "#ffd24d");
            grad.children[1].setAttribute("stop-color", "#ffbf00");
        } 
        else {
            grad.children[0].setAttribute("stop-color", "#4cd964");
            grad.children[1].setAttribute("stop-color", "#2eb82e");
        }
    }
});
