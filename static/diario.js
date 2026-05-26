document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("canvas-dibujo");
    const limpiar = document.getElementById("limpiar-dibujo");
    const descargar = document.getElementById("descargar-dibujo");

    if (!canvas) return;

    // Asegurar tamaño real del canvas
    if (!canvas.width) canvas.width = 600;
    if (!canvas.height) canvas.height = 300;

    const ctx = canvas.getContext("2d");
    let dibujando = false;

    canvas.addEventListener("mousedown", () => dibujando = true);
    canvas.addEventListener("mouseup", () => dibujando = false);
    canvas.addEventListener("mouseleave", () => dibujando = false);

    canvas.addEventListener("mousemove", (e) => {
        if (!dibujando) return;

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        ctx.fillStyle = "#000";
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
    });

    if (limpiar) {
        limpiar.addEventListener("click", () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });
    }

    if (descargar) {
        descargar.addEventListener("click", () => {
            const enlace = document.createElement("a");
            enlace.download = "mi_dibujo.png";
            enlace.href = canvas.toDataURL("image/png");
            enlace.click();
        });
    }
});
